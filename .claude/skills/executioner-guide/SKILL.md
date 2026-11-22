---
name: executioner-guide
description: Checks a pass that /executioner runs, from a thread of its own, while the runbook is still being worked out. Reads each executioner turn and each step's result back from their transcripts and the repository when I say Continue, fixes what is wrong (the executioner's pass file, RUNBOOK.md, the playbook or a command), makes the changes I ask for, and tells the executioner what it needs to know. Never repeats the executioner's handoffs. Run by hand only, in a new thread, in Auto mode, on Opus at Max effort; after its first turn, Continue alone.
argument-hint: "[anything: a problem, a question, a change to make]"
disable-model-invocation: true
model: opus
effort: max
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git rev-parse *)
  - Bash(git ls-files *)
  - Bash(git grep *)
  - Bash(node .claude/skills/executioner/scripts/tail.mjs *)
  - Bash(node .claude/skills/executioner/scripts/stats.mjs *)
---

# Guide a pass

Arguments: $ARGUMENTS

This thread checks a pass that `/executioner` runs in a thread of its own, while RUNBOOK.md, the playbook and the commands are still being worked out. The executioner hands out the steps, reviews each result and keeps the pass's record; this thread checks the executioner and the steps, fixes what is wrong, and makes the changes I ask for. It hands out no step and never repeats the executioner's handoffs: I follow those in the executioner's thread, so there is one set of steps to follow.

## Its setting

Opus at Max effort, on every turn: it judges the executioner's turns and the steps' results, and designs fixes to what steers every pass, which /commit's change check, a check of consistency, does not judge. This command fixes Opus at Max effort for its own turn, which runs before I have set the thread's. The turns after it, opened with Continue alone, run at the thread's setting, so each checks it first: `echo $CLAUDE_EFFORT` gives the effort, and there is no model variable, so go by your own identity. A turn on any model but Opus, or below max, does nothing else: it names the model or effort to set, then says to enter again what I entered.

## The first turn

Its reply opens with what to set and the thread's name, before anything else: "Set this thread to Opus at Max effort, and name it:", then the block `/rename executioner-guide`.

Then find the pass: the newest `~/.claude/plans/jobs-pass-<date>.md` whose progress table is neither complete nor abandoned. Its preamble names the executioner's thread, and `node .claude/skills/executioner/scripts/tail.mjs --find '<command-message>executioner</command-message>' --not ${CLAUDE_SESSION_ID}` lists every thread /executioner has run in. Where no pass is open, say so: the checking starts once /executioner's setup has written one. Otherwise check the pass from its start, as Continue does.

## Continue, and anything else I enter

I enter Continue here after each step, once the executioner has reviewed it, and anything else at any time, such as a problem I have seen, a question, or a change I want made. Each turn:

1. Re-read the pass file whole. Re-read this file where its rules are no longer in context, or where `git log` shows it changed since this thread read it.
2. Read what has happened since the last check: the executioner's replies, from the tail of its transcript (`node .claude/skills/executioner/scripts/tail.mjs <transcript> --last <n>`), and each step thread it handed out or reviewed, found as the executioner's §4 finds it. Never load a whole transcript.
3. Check the executioner against its SKILL.md and RUNBOOK.md, on the evidence:
   - its effort check, against what the turn ran at, which `node .claude/skills/executioner/scripts/stats.mjs <transcript>` gives from the transcript's own record, whatever anyone recalls of the picker;
   - each handoff, against RUNBOOK.md's items, as its §3 allows;
   - each review, against the step's tail and the repository (`git log`, `git status`, `git diff`), and each measure against `stats.mjs`;
   - its pass file: every record rests on evidence, and each standing decision comes from a source its command or RUNBOOK.md gives: its §1 step 5, a RUNBOOK.md item such as Step 2's switch to the sweep's Maximum setting from then on, or me. One from anywhere else, such as a memory note, is a wrong record.
4. Check each step's result: its thread's tail, the model and effort it ran at against the step's table in RUNBOOK.md, and its files against what the step writes.
5. Fix what is wrong:
   - A wrong record in the pass file: correct it, and add a Log line saying the correction is this thread's, what it changed and why.
   - A gap or a slip in RUNBOOK.md, the playbook or a command, and a change I ask for: make it where it belongs, as CLAUDE.md says. Feedback on a message another thread wrote, such as a handoff's wording, is fixed where that message comes from, the command or RUNBOOK.md. A rule for a snag goes in only where nothing later in the pass catches it. Trace each change through every prompt, command, script, RUNBOOK.md item and README.md line that reads or writes what it changes, read the whole diff against /commit's seven checks, then hand over `/commit`, in a new Claude Code thread.
   - Never edit while the executioner, a step or `/commit` is running. First check that ListAgents shows no busy thread of this repository, and where `git status` shows staged files, that the /commit thread that staged them has finished: a file edited after /commit stages it would be committed without its change check.
6. Tell the executioner what it must know, in its pass file's Log, which it re-reads every turn. A change to its command or to RUNBOOK.md that changes what its messages say also goes to its thread at once, with SendMessage (ListAgents names the thread), so I see the result as it is made: say the message is from this thread and what changed, and ask it to re-read them and restate its open handoff, or its last message's ending, as they now give it. Anything else it must know before my next entry there goes the same way, asking only that it record it. A message from here never stands for an entry of mine, such as Approve. Then check its restated message against the change, as a review here.

## The reply

- The verdict first: what went right, in a line, then each problem with its evidence.
- Then what was fixed, and where, and anything left for me to do that the executioner has not already said, such as a `/commit`.
- A question gets its answer, with what the answer rests on.
- Never repeat the executioner's handoff, its items or its blocks.
- End with one line saying this thread is waiting on me, for anything I enter, with Continue after the next step, such as "Waiting on you: enter anything here, or `Continue` after the next step and the executioner's review of it." It names no kinds of entry, such as a question, since this thread takes anything, and a list of some reads as all it is for. Where the reply has sent me to another thread, such as for a `/commit`, the line first says to come back here, such as "Then come back here: enter anything, or `Continue` after the next step and the executioner's review of it.", and never names this thread, which reads as if it meant another.

## The close-out

After the executioner's retrospective and its `/save`: check the retrospective's record against the pass file and the repository, and propose only what it left out; confirm that every change is committed and nothing is left uncommitted; and say what this pass changed in the runbook, and what is still open.

## What this thread never does

Run a step's command, `/save`, `/commit`, `/verify` or `/executioner`; drive a browser; move a file of mine, or edit the files the steps and I write: the ledger, `run/`, `root/01-positioning.txt`, the `root/02-*` prompt files and the resume; commit or push. The repository is public: nothing private goes into a file it changes.
