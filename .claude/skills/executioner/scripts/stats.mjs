#!/usr/bin/env node
// Read-only helper for the /executioner skill: measures one thread from its transcript, so the
// executioner can weigh a step's model and effort against what the step cost. It prints the thread's
// time, the messages typed into it, the models and efforts its replies ran at and their tokens, the
// forked commands it ran, its tool calls, compactions and stops, and the cost Claude Code recorded for
// it at API prices. It reads files and changes nothing. Node 18 or later, no dependencies.
//
//     node stats.mjs <transcript.jsonl | thread id> [--from <ISO time>] [--to <ISO time>] [--cwd <dir>]
//         measure the thread, or only its records from --from to --to; a thread id, or the start of
//         one, is looked up among the transcripts of the project at <dir> (the working directory by
//         default)

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { homedir } from 'node:os';

const args = process.argv.slice(2);
const option = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const target = args.find((a, i) => !a.startsWith('--') && (i === 0 || !args[i - 1].startsWith('--')));

// The transcripts of a project live under ~/.claude/projects/<folder> (or under CLAUDE_CONFIG_DIR),
// where <folder> is the working directory with every character that is not a letter or a digit
// replaced by '-'. The record shape inside a transcript is internal to Claude Code and may change;
// only a few labelled fields are read here.
const configDir = process.env.CLAUDE_CONFIG_DIR || join(homedir(), '.claude');
const projectFolder = (cwd) => join(configDir, 'projects', cwd.replace(/[^A-Za-z0-9]/g, '-'));

const records = (path) => {
  const out = [];
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    if (!line) continue;
    try { out.push(JSON.parse(line)); } catch { /* a partial last line while the thread writes */ }
  }
  return out;
};

if (!target) { console.error('usage: stats.mjs <transcript.jsonl | thread id> [--from <ISO time>] [--to <ISO time>] [--cwd <dir>]'); process.exit(2); }

let file = target;
if (!(target.endsWith('.jsonl') && existsSync(target))) {
  const dir = projectFolder(option('--cwd') ?? process.cwd());
  let names = [];
  try { names = readdirSync(dir).filter((n) => n.endsWith('.jsonl') && n.startsWith(target)); } catch { /* no such folder */ }
  if (names.length !== 1) {
    console.error(names.length ? `${names.length} transcripts under ${dir} start with ${target}: give more of the id` : `no transcript under ${dir} starts with ${target}`);
    process.exit(2);
  }
  file = join(dir, names[0]);
}

const bound = (name, fallback) => {
  const text = option(name);
  if (text === undefined) return fallback;
  const t = Date.parse(text);
  if (Number.isNaN(t)) { console.error(`${name} is not a time: ${text}`); process.exit(2); }
  return t;
};
const from = bound('--from', -Infinity);
const to = bound('--to', Infinity);
const windowed = from !== -Infinity || to !== Infinity;
const time = (r) => (r.timestamp ? Date.parse(r.timestamp) : NaN);
const inWindow = (r) => { const t = time(r); return !Number.isNaN(t) && t >= from && t <= to; };

const n = (x) => x.toLocaleString('en-US');
const iso = (t) => new Date(t).toISOString().replace(/\.\d{3}Z$/, 'Z');
const span = (ms) => {
  const m = Math.round(ms / 60000);
  return m >= 60 ? `${Math.floor(m / 60)}h${String(m % 60).padStart(2, '0')}m` : `${m}m`;
};

const all = records(file);

const textOf = (content) => (typeof content === 'string' ? content
  : Array.isArray(content) ? content.filter((b) => b?.type === 'text').map((b) => b.text).join('\n') : '');
const isToolResult = (r) => Array.isArray(r.message?.content) && r.message.content.some((b) => b?.type === 'tool_result');
// A message a person typed: a user record that is not the harness's own (a skill's expanded text, a
// caveat or a notice), not a tool's result, and not a subagent's.
const typedText = (r) => {
  if (r.type !== 'user' || r.isMeta || r.isSidechain || isToolResult(r)) return '';
  const text = textOf(r.message?.content).trim();
  return /^(<task-notification>|<system-reminder>|\[Request interrupted)/.test(text) ? '' : text;
};
// A command typed in the thread opens with its name tag; a forked one is stored as typed, "/save";
// @browser arrives as the extension's instructions.
const commandOf = (text) => {
  const tagged = text.match(/<command-name>(\/[^<\s]+)<\/command-name>/);
  if (tagged) return tagged[1];
  const bare = text.match(/^\/[A-Za-z][\w:-]*/);
  if (bare) return bare[0];
  return text.startsWith('<browser_instruction>') ? '@browser' : null;
};

const usage = () => ({ output: 0, thinking: 0, input: 0, write: 0, write1h: 0, read: 0 });
const addUsage = (acc, u = {}) => {
  acc.output += u.output_tokens ?? 0;
  acc.thinking += u.output_tokens_details?.thinking_tokens ?? 0;
  acc.input += u.input_tokens ?? 0;
  acc.write += u.cache_creation_input_tokens ?? 0;
  acc.write1h += u.cache_creation?.ephemeral_1h_input_tokens ?? 0;
  acc.read += u.cache_read_input_tokens ?? 0;
};
const showUsage = (u) => `output ${n(u.output)} (thinking ${n(u.thinking)}), input ${n(u.input)}, cache write ${n(u.write)} (1h ${n(u.write1h)}), cache read ${n(u.read)}`;
// A reply's records repeat its usage once per content block, so each message id counts once. A
// <synthetic> record and an API error carry no tokens of their own.
const replies = (recs) => {
  const byId = new Map();
  for (const r of recs) {
    if (r.type !== 'assistant' || !inWindow(r) || r.isApiErrorMessage) continue;
    if (r.message?.model === '<synthetic>') continue;
    byId.set(r.message?.id ?? r.uuid, r);
  }
  return [...byId.values()];
};
const effortOf = (r) => r.effort ?? r.perTurnEffort ?? '?';

const main = all.filter((r) => !r.isSidechain);
// The thread's own messages, tool results and command output. The harness's bookkeeping records, such
// as the queue entry written just before a typed message, would stretch a turn to the next one.
const stamped = main.filter((r) => ['user', 'assistant', 'system'].includes(r.type) && inWindow(r))
  .sort((a, b) => time(a) - time(b));

let title = '';
for (const r of all) if (r.type === 'ai-title' && r.aiTitle) title = r.aiTitle;
console.log(`thread ${basename(file, '.jsonl')}${title ? `  "${title}"` : ''}`);
if (windowed) console.log(`window ${from === -Infinity ? 'start' : iso(from)} to ${to === Infinity ? 'end' : iso(to)}`);
if (stamped.length === 0) { console.log('no records in the window'); process.exit(0); }

// Active time: each turn, from the message that opened it to its last record before the next one,
// so the hours a thread sits waiting for a person do not count. A turn's last record is work done in
// it: not a notice the harness adds, and not a <synthetic> reply such as "No response requested.",
// which the harness can write just before the next message. An API error does end a turn.
const typed = stamped.filter((r) => typedText(r));
const work = (r) => !(r.type === 'user' && r.isMeta)
  && !(r.type === 'assistant' && r.message?.model === '<synthetic>' && !r.isApiErrorMessage);
let active = 0;
for (let i = 0; i < typed.length; i++) {
  const start = time(typed[i]);
  const next = i + 1 < typed.length ? time(typed[i + 1]) : Infinity;
  let end = start;
  for (const r of stamped) { const t = time(r); if (work(r) && t > start && t < next) end = Math.max(end, t); }
  active += end - start;
}
const first = time(stamped[0]), last = time(stamped[stamped.length - 1]);
console.log(`records ${iso(first)} to ${iso(last)} (span ${span(last - first)}); active ${span(active)} over ${typed.length} turns`);

const versions = [...new Set(stamped.map((r) => r.version).filter(Boolean))];
if (versions.length) console.log(`Claude Code ${versions.join(', ')}`);

const commands = new Map();
let free = 0;
for (const r of typed) {
  const c = commandOf(typedText(r));
  if (c) commands.set(c, (commands.get(c) ?? 0) + 1);
  else free += 1;
}
const listed = [...commands].map(([c, k]) => (k > 1 ? `${c} ×${k}` : c));
console.log(`typed: ${listed.length ? listed.join(', ') : 'no commands'}; ${free} other ${free === 1 ? 'message' : 'messages'}`);

const own = replies(main);
const mix = new Map();
const tokens = new Map();
for (const r of own) {
  const model = r.message?.model ?? '?';
  if (!mix.has(model)) mix.set(model, new Map());
  const efforts = mix.get(model);
  efforts.set(effortOf(r), (efforts.get(effortOf(r)) ?? 0) + 1);
  if (!tokens.has(model)) tokens.set(model, usage());
  addUsage(tokens.get(model), r.message?.usage);
}
console.log(`replies: ${[...mix].map(([m, e]) => `${m} ${[...e].map(([x, k]) => `at ${x} ×${k}`).join(', ')}`).join('; ') || 'none'}`);
for (const [model, u] of tokens) console.log(`tokens, ${model}: ${showUsage(u)}`);

// Forked commands and agents write their own transcripts under <thread>/subagents.
const subDir = join(dirname(file), basename(file, '.jsonl'), 'subagents');
let subFiles = [];
try { subFiles = readdirSync(subDir).filter((name) => name.endsWith('.jsonl')); } catch { /* none ran */ }
const forked = new Map();
const sidechain = all.filter((r) => r.isSidechain);
const runs = subFiles.map((name) => ({ name, recs: records(join(subDir, name)) }));
if (sidechain.length) runs.push({ name: 'sidechain', recs: sidechain });
for (const { name, recs } of runs) {
  const own = replies(recs);
  if (own.length === 0) continue;
  let agentType = '';
  try { agentType = JSON.parse(readFileSync(join(subDir, name.replace(/\.jsonl$/, '.meta.json')), 'utf8')).agentType ?? ''; } catch { /* no meta file */ }
  const label = own.find((r) => r.attributionSkill)?.attributionSkill ?? (agentType || 'agent');
  const key = `${label} on ${own[0].message?.model ?? '?'} at ${effortOf(own[0])}`;
  if (!forked.has(key)) forked.set(key, { runs: 0, u: usage() });
  const entry = forked.get(key);
  entry.runs += 1;
  for (const r of own) addUsage(entry.u, r.message?.usage);
}
for (const [key, { runs: k, u }] of forked) console.log(`forked: ${key} ×${k}: ${showUsage(u)}`);

const tools = new Map();
const seen = new Set();
let errors = 0;
for (const r of stamped) {
  if (r.type === 'assistant') {
    for (const b of Array.isArray(r.message?.content) ? r.message.content : []) {
      if (b?.type !== 'tool_use' || seen.has(b.id)) continue;
      seen.add(b.id);
      const name = b.name.startsWith('mcp__') ? `mcp ${b.name.split('__')[1]}` : b.name;
      tools.set(name, (tools.get(name) ?? 0) + 1);
    }
  } else if (r.type === 'user' && isToolResult(r)) {
    errors += r.message.content.filter((b) => b?.type === 'tool_result' && b.is_error).length;
  }
}
const toolList = [...tools].sort((a, b) => b[1] - a[1]).map(([t, k]) => `${t} ${k}`);
console.log(`tools: ${toolList.length ? toolList.join(', ') : 'none'}; ${errors} ${errors === 1 ? 'error' : 'errors'}`);

const compactions = stamped.filter((r) => r.type === 'system' && r.subtype === 'compact_boundary').length;
console.log(`compactions: ${compactions || 'none'}`);

const stops = new Map();
for (const r of stamped) {
  if (r.type !== 'assistant' || !r.isApiErrorMessage) continue;
  const kind = r.error ?? 'error';
  if (!stops.has(kind)) stops.set(kind, { k: 0, at: time(r) });
  stops.get(kind).k += 1;
}
console.log(`stops: ${[...stops].map(([kind, { k, at }]) => `${kind} ×${k}, first at ${iso(at)}`).join('; ') || 'none'}`);

// Claude Code writes a cost record at points such as the thread's close, without a time of its own;
// what it covers is everything written before it.
let cost = null, upTo = -Infinity;
for (const r of all) {
  const t = time(r);
  if (!Number.isNaN(t)) upTo = Math.max(upTo, t);
  if (r.type === 'cost-state') cost = { r, upTo };
}
if (!cost) {
  console.log('recorded cost: none yet');
} else {
  const { r, upTo: covered } = cost;
  const models = Object.entries(r.modelUsage ?? {}).map(([m, u]) => `${m} $${(u.costUSD ?? 0).toFixed(2)}`).join(', ');
  const apiTime = r.totalAPIDuration ? `, API time ${span(r.totalAPIDuration)}` : '';
  const scope = windowed ? 'for the whole thread, not the window,' : 'for the thread';
  const gap = last > covered ? `; records after ${iso(covered)} are not in it yet` : '';
  console.log(`recorded cost: $${(r.totalCostUSD ?? 0).toFixed(2)} at API prices (${models})${apiTime}, ${scope} up to ${iso(covered)}${gap}`);
}
