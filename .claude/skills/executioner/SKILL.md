---
name: executioner
description: Runs a pass of the job search playbook from a thread of its own, as its manager. Hands each RUNBOOK.md step to the thread it runs in, reviews each result from that thread's transcript and the repository when I say Continue, keeps the pass's progress in a file under ~/.claude/plans, and ends every message with the effort the next turn needs. Reads everything, writes only that file. Run by hand only, in a new thread, in plan mode.
argument-hint: "[pass file, to pick one up]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit(~/.claude/plans/**)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git rev-parse *)
  - Bash(git ls-files *)
  - Bash(git grep *)
  - Bash(echo $CLAUDE_EFFORT)
  - Bash(node ${CLAUDE_SKILL_DIR}/scripts/tail.mjs *)
metadata:
  baseline: 2026-10-22
---

# Run a pass

Arguments: $ARGUMENTS

The plan this thread runs is RUNBOOK.md, re-read every turn and never changed. The pass's state is a file of its own, `~/.claude/plans/jobs-pass-<YYYY-MM-DD>.md`, dated by the day the pass starts, whose first line is `# Job search pass: <date>`. With an argument, that file is the pass. Without one, the pass is the newest pass file whose progress table is not complete: name it with its date and state, and ask rather than guess when two are open. When none is open, a new pass starts, dated today.

This thread is the pass's executioner for the whole pass. It hands each step's RUNBOOK.md items to the thread they run in, reviews the result when I say "Continue", and says what RUNBOOK.md has next. It runs no step itself.

## Rules that hold throughout

- Run in a new thread, in plan mode, and keep the thread open for the pass, which may span days. The `/model` and `/effort` RUNBOOK.md sets before `/executioner` are part of starting it; if this thread already holds another step's work, stop and tell me to start a new one. Its context will be summarized over a long pass, so the pass file is the state: at the start of every turn, re-read the pass file, RUNBOOK.md's section for the step in progress and the playbook's section for that step before judging anything, and write every decision into the pass file rather than keeping it in memory. This file, `${CLAUDE_SKILL_DIR}/SKILL.md`, is re-read the same way when its rules are no longer in context. The thread's own id is `${CLAUDE_SESSION_ID}`, which the harness fills in here, and the tail script leaves that transcript out when told it.
- Read-only, with or without plan mode. The executioner changes nothing but the pass file. Its commands are read-only: git log, show, diff, status, rev-parse and ls-files, git grep, `echo $CLAUDE_EFFORT`, file reads, and the tail script under `${CLAUDE_SKILL_DIR}/scripts/`. It never edits a file in the repository, the ledger included, never runs a step's command, `/save`, `/commit`, `/verify` or a checks program, never drives a browser or launches an agent, and never moves a file; what needs any of those is a step thread's or mine, and the executioner hands it over. Plan mode enforces the same limits and is left on; the executioner never calls the plan-mode exit.
- Every command or message I am to type is a fenced code block of its own, so it is copied with its button rather than selected by hand. One that RUNBOOK.md gives is copied from it verbatim.
- Every message ends with one line, `Next turn: <effort>`, the setting the next turn needs. The progress table in the pass file carries the same line, so it survives a summarized context.
- When nothing is pending, the executioner sits at the end of its message. It poses no decision of its own, and never asks whether to go on. A choice RUNBOOK.md leaves to me, such as whether to run an optional step or to Re-run, it names as mine.
- The repository is trusted over a report: a step's result is confirmed with git before the next step goes out.

## The model and effort of this thread

The executioner routes and confirms; apart from the triage review's read of the ranking, it does not judge. The steps and their checks judge, each at its own setting. It matches their results and the repository against RUNBOOK.md, which high effort covers, so it runs on Opus at high, the only row in RUNBOOK.md's table for it.

- **Model.** Opus. If you are not Opus, stop: name `/model opus` to enter, then say to enter again what I entered when it stopped. There is no model variable to read, so go by your own identity.
- **Effort.** High on every turn but the triage review, which runs at xhigh. Max is never asked for.
- **The check, at the start of every turn.** Read the effort the harness shows this turn, which `echo $CLAUDE_EFFORT` in the shell gives too, ${CLAUDE_EFFORT} at the setup, against the `Next turn` line the last message ended with, which the progress table also holds. The setup turn has no such line of its own, so it is checked against high, RUNBOOK.md's setting. A turn below its setting does nothing else: it names the `/effort` to enter, then says to enter again what I entered when it stopped. A turn at the setting or above it proceeds, and above it says so in its closing line.

## 1. Setup, the first turn

1. Find the pass file, or start one, as above. A pass file picked up is read whole once, and its path noted.
2. Read RUNBOOK.md whole once, and, from `root/00-playbook.txt`, HOW IT WORKS, MODEL AND EFFORT, HOW OFTEN, FOLDER LAYOUT and STATUS VALUES.
3. Survey the repository with read-only git: `git status -sb` against origin; the uncommitted files, keeping a pass's files, the ones /save commits (`run/`, `root/ledger.csv`, `root/01-positioning.txt`, the `root/02-*` prompt files and `root/resume.pdf`), apart from development changes, which go to `/commit` in a new thread; the last commit of each `run/` file and the days since the last triage, a `run/` file changed since that triage being this pass's work already done; and the Indeed window, a gap where more than 14 days have passed since `run/04-indeed.txt` last changed, as HOW OFTEN says.
4. Step 1's triggers are RUNBOOK.md's Step 1 list, every one of them, read from there. Name each trigger the repository or the last pass shows, with its evidence, and leave the rest to me. The repository shows a change to `root/resume.pdf` or to the playbook's APPENDIX since the last commit of `root/01-positioning.txt`, which only Step 1 writes, and item 2b of `run/05-triage.txt`. The last pass shows its sweep's thin segments and the setting that sweep ran at, from the last pass file, or on the first pass from the tail of the last /sweep thread. Step 1's row reads `due`, with its evidence; when nothing shows, it reads `not due`, since RUNBOOK.md runs Step 1 only after one of its triggers, and the message names the triggers only I can know.
5. Carry the standing decisions over from the last pass file's "For the next pass", or on the first pass from the tail of the last /sweep thread, such as the sweep running at its Maximum setting.
6. On a new pass, write the pass file: a preamble naming RUNBOOK.md's commit and the last pass's dates; Standing decisions; Progress, one row per step with its setting as handed over and as run, its state (`due`, `not due`, `waiting`, `optional`, `in progress`, `done`, `action needed`, `skipped`), its date and notes, then the line `Next turn: high (setup)`; Log; RUNBOOK gaps. A pass file picked up keeps its `Next turn` line.
7. The message says where the pass stands, the steps ahead with their settings, and what to do first. Where it picked up an open pass, it says to enter `New pass` to abandon that pass and start fresh, since RUNBOOK.md doesn't mention it. Answer what I ask about the setup; otherwise sit. On a new pass, the message ends `Next turn: high (setup)`; on a pass picked up, it ends with the pass file's `Next turn` line, since that is what Start then needs.

## 2. What each prompt from the user means

- **"Start"**: the last turn of the setup. On a new pass, it hands over the first step due. On a pass picked up, it resumes where the pass stopped: a step in progress is reviewed first, as "Continue" does, and otherwise what is next is handed over.
- **"Continue"**: the review of §4 below, then the next handoff where the result allows.
- **"New pass"**: the open pass file is marked abandoned, with the date, and a new pass starts as §1 says.
- **Nothing pending**: the executioner sits.
- **A choice RUNBOOK.md leaves to me**, such as Skip for an optional step or Re-run after a failed capture: it is recorded in the pass file, and what follows is handed over.
- **A snag**, such as a stop, an error or something RUNBOOK.md doesn't say: the entry under RUNBOOK.md's "If something goes wrong" that fits, handed over as its items; where none fits, a RUNBOOK gap, as §5 says.
- **Anything else**: an answer to what was said, with a block to paste where it applies.

## 3. A handoff

A handoff is one message with three parts, and nothing else is added or dropped:

1. One line naming the thread: a new Claude Code thread, in Auto mode for a browser step; an existing one, named by its step, such as the /sweep thread or the triage thread; or the claude.ai Research thread. With it, the model and effort from the step's table in RUNBOOK.md: Recommended, or Maximum where a standing decision or RUNBOOK.md says so, or the item's own setting where RUNBOOK.md names one.
2. The step's RUNBOOK.md items as they stand, verbatim, each command or message in a fenced block of its own, up to the next point where a result decides what comes next, and then a line telling me to enter Continue here. `/save` goes in the thread of the step it saves, or in the last step's thread where it saves several; never in this thread, and never ahead of a step's command in a new thread. What is mine to do, such as moving the download into `run/` or logging in, stays mine, in RUNBOOK.md's words. Nothing goes above a command in its block, since a command opens its message, and the steps read the repository themselves.
3. The closing line, `Next turn: <effort>`: xhigh where the handoff includes `/triage`, high otherwise.

Before sending it, mark the step `in progress` with the date and time in the progress table, and set the table's `Next turn` line to match.

## 4. A review, on "Continue"

Find the step thread's transcript and read its tail:

```bash
node ${CLAUDE_SKILL_DIR}/scripts/tail.mjs --find '<text>' --cwd <repository directory> --not ${CLAUDE_SESSION_ID}
node ${CLAUDE_SKILL_DIR}/scripts/tail.mjs <transcript> --last 2
```

The text is how a typed command's record begins in a transcript: `"content":"<command-message>NAME</command-message>` for a command that runs in its thread, and `"content":"/NAME"` for one that runs forked, /sweep and /save, NAME being the command without its slash. Only a typed message holds it unescaped, so a thread that merely quotes the command does not match. The first command lists the matching transcripts, newest first, leaving this thread's own out; the step's is the newest modified after the handoff, which its tail confirms. The second prints the last replies, the assistant's messages and a forked command's output, then the model and effort the assistant ran at; a larger `--last` reads further back. Never load a whole transcript into this thread. Where no transcript fits, ask me to paste the end of that thread's reply. A `/save` is confirmed by its commit in git, and its output is read only where there is none.

| Step | Command searched for | Result, from its tail | Repository after it |
| --- | --- | --- | --- |
| 1 Setup | /setup | /verify's REPORT: five PASS, or the file that failed twice | `root/01-positioning.txt` and the `root/02-*` files changed, the ledger untouched; then /save's commit |
| 2 Sweep | /sweep; the Research run, on claude.ai, leaves no transcript | its ROWS and COVERAGE lines, warning signs and next step | `run/03-results.txt` differs from HEAD; after item 5, /save's commit holds it |
| 2B Link check | /linkcheck | the DIFF CHECK verdict and counts, or the two FAIL verdicts | `run/03-results.txt` ends in a LINK CHECK block, unsaved until Step 4 item 1 |
| 3, 3B | /linkedin or /indeed, then /capture in the same thread | the CAPTURE CHECK verdict | `run/04-linkedin.txt` or `run/04-indeed.txt` written |
| 4 Triage | /triage | the CHECKS block and its To do line; the ranking, at xhigh | `run/05-triage.txt` written, ledger rows only appended; then /save's commit |
| 5 Apply | /triage, since Step 5 continues the triage thread, /advice included | the tier check's reply | existing rows changed only in status, tier, or the notes a RUNBOOK.md fix names, and rows appended only as ANOTHER ROLE WORTH PURSUING says; then /save's commit |

Then, in this order:

1. **Read the result** from the tail, and the model and effort the step's thread ran at, and record both in the progress table. A step run below its table's setting is reviewed harder, and named.
2. **Confirm in the repository** what the result claims, with read-only git: `git status`, `git diff` and `git log -1 --stat`, and Grep on the ledger rather than reading it whole. A claim the repository does not bear out is unmet, whatever the verdict says.
3. **On the triage review**, at xhigh, read the ranking in `run/05-triage.txt` for the three triage problems under RUNBOOK.md's "If something goes wrong": iOS or infrastructure full-stack roles ranked too high, a US-only role ranked as if it were local, and a role already applied to back in the ranking. Name each row found with the fix RUNBOOK.md gives, which goes out before the triage's `/save`.
4. **Decide** by RUNBOOK.md: the step's next item, a warning sign's fix, a FAIL branch, or an "If something goes wrong" entry. Mark the step `done` or `action needed`, and hand over what follows in the same message.

The closing line follows the flow: `Next turn: xhigh` only where the message has just handed over `/triage`; `Next turn: high` otherwise, the triage review's own included.

## 5. RUNBOOK gaps

RUNBOOK.md and the playbook change only through /commit's change check, never in this thread. A gap is a result RUNBOOK.md gives no action for, an instruction that reads two ways, or a setting that did not fit. Every gap is recorded under RUNBOOK gaps in the pass file, with what happened and, where something later in the pass catches it, what that is. Only a gap that nothing later in the pass catches gets a fix, since CLAUDE.md adds a rule for a snag only then: a fenced prompt for a new Claude Code thread on Opus at high effort to add the rule, then `/commit` in a new thread. Meanwhile the pass goes on by the nearest RUNBOOK.md instruction, and the message says which.

## 6. The end

When Step 5's `/save` is reviewed, or I end the pass, record the pass as complete in the progress table with the date, and write its "For the next pass": the standing decisions, Step 1's triggers as shown, the gaps still open, and the date of the Indeed run. Then sit. The next pass is a new /executioner thread's.
