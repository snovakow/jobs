# jobs

An AI-driven job search. Claude finds live postings, checks that they are
real, ranks them against my resume and says how to pitch the strongest ones.
A ledger remembers every posting surfaced so far, so nothing already dealt
with gets ranked twice.

It is tuned to my own search, which centres on visualization — real-time 3D
and XR, video, and frontend work with real technical depth — but most of the
machinery is general.

The whole system is a runbook of prompts. Claude keeps nothing between
conversations, so each step runs as its own conversation, writes a plain-text
file, and hands that file to the next step as an attachment. The files in
this repository are that state: the prompts, the latest pass's results and
the ledger.

## How a pass works

Setup runs once, and again only when something real changes, such as a
revised resume or a new target. It reads the resume, writes a positioning
read — the job titles, search keywords and target companies that fit — and
turns it into twelve standalone search prompts. Every pass after that is
Steps 2 to 5.

| Step | Where it runs | Produces |
| --- | --- | --- |
| 1. Setup | Chat | The positioning read, twelve search prompts and an empty ledger |
| 1B. Verify | Chat | A pass/fail check of every file setup wrote |
| 2. Sweep | Advanced Research, four runs | `03-results-seg*.txt` |
| 3. LinkedIn | Claude in Chrome, eight runs | `04-linkedin-*.txt` |
| 4. Triage | Chat | `05-triage.txt`, `keyword-append-edits.txt` and an updated `ledger.csv` |
| 4B. Patch | Chat, when a keyword fails | Keyword swaps in the LinkedIn prompts |
| 5. Apply | By hand | Status updates in `ledger.csv` |

The **sweeps** search employer career pages and hosted job boards —
Greenhouse, Lever, Ashby, Workday and the like — with one run for each of four
segments: graphics and XR, video infrastructure, frontend with depth, and
Apple-platform apps that deliver visualization or media.

The **LinkedIn runs** exist because Research cannot read LinkedIn. Claude in
Chrome searches LinkedIn Jobs in my own logged-in browser instead: four
keyword sets, each run once for Toronto and once for Canada-remote, in small
sessions that stop at the first sign of rate limiting.

**Triage** merges every result file, sets aside anything already dealt with,
and ranks the rest into three tiers: apply now, apply if the first tier is
thin, and skip, with a five-word reason. For each first-tier role it names
the resume bullets to lead with and the line to open the application with,
and across the whole pass it reports which missing skills keep coming up.

**Applying** is manual. So is marking a posting applied, rejected or skipped;
triage only ranks.

## Why it is built this way

- **Narrow runs beat broad ones.** A Research run has a finite search budget.
  Asked for five kinds of role at once, it comes back shallow on all five;
  four runs of one segment each go deep. Browser sessions have a budget too,
  so the LinkedIn work is eight small runs rather than one long one, and each
  prints its table after every keyword so that a stalled run loses nothing.
- **Verified beats voluminous.** Every sweep row is a posting the run opened,
  or one it found on two independent sources and marked `UNVERIFIED`.
  Nothing recalled from training data, no guessed links. Six real postings
  are a better result than forty plausible ones.
- **Every posting is a row.** A posting that does not fit cleanly — wrong
  city, older than 30 days, a page that would not open — goes into the table
  with a status token (`OK`, `RELOCATE`, `UNCLEAR`, `STALE`, `UNVERIFIED`)
  rather than into a paragraph under it. Everything downstream keys off rows,
  and a posting that exists only in prose is one the system cannot see.
- **The ledger only grows.** `ledger.csv` holds every posting ever surfaced.
  Triage appends to it without touching an existing row, and matches
  postings on company and role title, normalized, never on URL: the same role
  arrives as a LinkedIn link from one run and an employer link from another.
  Triage only ever writes `new`; `applied`, `rejected` and `skipped` record
  decisions a person made. Setup writes `ledger-seed.csv`, never
  `ledger.csv`, so re-running it cannot wipe the history.
- **Silence is never a report.** Any block a run must print has an explicit
  empty form, such as `KEYWORD EDITS: NONE`, so a run with nothing to report
  can be told apart from one that skipped the step.
- **Maximum effort where a model could flatter.** Setup, its verifier and
  triage run at maximum effort, because that is where a model pleases you
  instead of informing you: a first tier padded to look healthy, a check
  that passes everything. The verifier has to print its evidence under every
  pass.
- **Keywords are tested, and failures are kept.** LinkedIn search is
  semantic, so a keyword has to name a technology or a kind of work — never
  a job title, which matches nearly every posting at that level, and never
  an everyday word ("Metal" finds fabrication jobs). It also has to be
  common enough for LinkedIn's index to hold. Every term ruled out goes into
  `keyword-edits.txt`, which setup reads so that a re-run does not propose
  it again.
- **The resume is read as a history.** A skills list weighs every skill the
  same; a work history shows what a career is about. The prompts that judge
  fit read it that way, so a skill that served the main work does not make a
  role built around that skill look like a match.

## Repository layout

```text
.claude/skills/commit/      A Claude Code skill: /commit reviews the changes
                            and commits them
00-runbook-quick-guide.txt  Every prompt, in order: what a pass runs from
root/                       Permanent files, never dated or copied
  00-runbook.txt            The full runbook: reasoning, prompt templates,
                            troubleshooting
  01-positioning.txt        The positioning read from setup
  02-segment-*.txt          Four Research prompts, one per segment
  02-linkedin-*.txt         Eight LinkedIn prompts, one per keyword set and
                            location
  keyword-edits.txt         Every LinkedIn keyword ruled out so far
  ledger.csv                Every posting surfaced, with its status
  resume.pdf                The resume the judging steps read
run/                        The most recent pass
  03-results-seg*.txt       Sweep results
  04-linkedin-*.txt         LinkedIn results
  05-triage.txt             The ranked pass
  keyword-append-edits.txt  The keywords this pass ruled out, for Step 4B
```

These are the working files of an active search, committed as they stand
after each pass. Each pass overwrites `run/`; earlier passes are in the
commit history. Filenames never change, so attaching the right files to a
step is mechanical rather than a decision.

## Running a pass

[`00-runbook-quick-guide.txt`](00-runbook-quick-guide.txt) has every prompt
in the order it runs. [`root/00-runbook.txt`](root/00-runbook.txt) explains
each step and holds the prompt templates, the segment definitions and a
table of what goes wrong and how to fix it.

You will need:

- a Claude plan with file creation, Advanced Research and the Claude in
  Chrome extension
- a chat that takes fifteen attachments on one message, which is what a full
  triage uses
- a LinkedIn login in the Chrome profile the extension runs in

A pass does not have to happen in one sitting, or in full: sweeping the two
most important segments and then running triage is a real pass. Good roles
close within two or three weeks, so a longer gap between passes lets
postings open and close unseen.

## Adapting it

The machinery — the file flow, the status tokens, the ledger and the checks —
is general. What ties it to my search:

- `resume.pdf`
- the passages that describe my background, in the Step 1 prompt, the prompt
  templates and the triage prompt
- the four segment definitions in the runbook's appendix
- the location rules, which target Ontario and Canada-remote roles

Change those, run Step 1 and check its output with Step 1B, and the twelve
generated prompts are aimed at the new search.
