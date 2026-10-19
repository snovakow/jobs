# jobs

An AI-driven job search. Claude finds live postings, checks that they are
real, ranks them against my resume and says how to pitch the strongest ones.
A ledger remembers every posting surfaced so far, so nothing already dealt
with gets ranked twice.

It is tuned to my own search, which centres on visualization — real-time 3D
and XR, video, and frontend work with real technical depth — but most of the
machinery is general.

The whole system is a playbook of prompts, run from Claude Code. Claude keeps
nothing between conversations, so each step runs as its own conversation,
reads the files the steps before it wrote, and writes its own back into this
repository. The files here are that state: the prompts, the latest pass's
results and the ledger.

Two documents divide the work. The runbook, `RUNBOOK.md`, is what I follow:
each step as the actions to take and the commands to enter. The playbook,
`root/00-playbook.txt`, is what the agents run from: each step's prompt, the
templates setup copies, and the reasons behind them. Each step is a Claude
Code command that reads its prompt from the playbook when it runs. Only the
sweep leaves Claude Code, for Advanced Research on claude.ai, and the browser
steps run in my own Chrome, driven from Claude Code through the Claude in
Chrome extension.

## How a pass works

Setup runs once, and again only when something real changes, such as a
revised resume or a new target. It reads the resume, writes a positioning
read — the job titles, search keywords, LinkedIn descriptions and target
companies that fit — and turns it into three standalone search prompts.
Every pass after that is Steps 2 to 5.

| Step | Command | Where it runs | Produces |
| --- | --- | --- | --- |
| 1. Setup | `/setup` | Claude Code | The positioning read and three search prompts |
| 1B. Verify | `/verify`, run by `/setup` | Claude Code, in a fresh context | A pass/fail check of every file setup wrote |
| 2. Sweep | `/sweep` takes its file in | Advanced Research on claude.ai, one run | `03-results.txt` |
| 2B. Link check | `/linkcheck`, which runs `/diffcheck` | Chrome, driven from Claude Code, then a check in a fresh context | `03-results.txt` with closed postings cut |
| 3. LinkedIn AI job search | `/linkedin`, then `/capture` | Chrome, driven from Claude Code | `04-linkedin.txt` |
| 3B. Indeed | `/indeed`, then `/capture` | Chrome, driven from Claude Code | `04-indeed.txt` |
| 4. Triage | `/triage` | Claude Code | `05-triage.txt` and rows appended to `ledger.csv` |
| 5. Apply | `/advice`, and by hand | You, with Claude Code | Status updates in `ledger.csv` |

The **sweep** searches employer career pages and hosted job boards —
Greenhouse, Lever, Ashby, Workday and the like — in one run covering four
segments: graphics and XR, video infrastructure, frontend with depth, and
Apple-platform apps that deliver visualization or media.

The **link check** exists because Research can read a posting that has already
closed: a search index, a cached copy or an aggregator keeps a posting's text
long after the employer takes it down, and a row read from one looks like any
other. Claude Code opens every sweep row's link in Chrome, as the page now
stands, and cuts the postings that have closed, before triage reads the file.
Neither a dead link nor a live aggregator page is proof on its own: employers
move between job boards, leaving old links dead while the role stays open, and
an aggregator can show a whole posting under a notice that it was removed. So
the check looks for the role on the employer's own career page, and keeps the
row, with that link, only if the role is listed there. A staffing agency's
posting, which may exist only on job boards, stays if its link is live.

The browser run's edits are checked in turn, in a fresh context of their own.
It edits the file in place to cut a few rows, and a long run can still change
a row on the way that nobody asked it to touch. Its LINK CHECK block says
exactly what it meant to change, so the check diffs the file against the
sweep's committed copy, and any difference the block does not account for is
a mistake: when there is one, the check rebuilds the file from the sweep's
copy and the block.

The **LinkedIn run** exists because Research cannot read LinkedIn. Claude Code
uses LinkedIn's AI job search in my own logged-in Chrome instead, in one run:
five descriptions of the job I want, two for segment 1 and one for each other
segment, each leading with the work rather than a job title.

The **Indeed run** exists for the same reason, and runs signed out, which it
checks before it searches. It searches Indeed for four sets of quoted
keywords, one set per segment, each searched once for Toronto and once for
Canada-remote.

**Triage** merges every result file, sets aside anything already dealt with,
and ranks the rest into three tiers: apply now, apply if the first tier is
thin, and skip, with a five-word reason. For each first-tier role it names the
resume bullets to lead with and the line to open the application with, and it
gives the same advice for any lower-tier role I choose to apply to. Across the
whole pass it reports which missing skills keep coming up, and it reads my past
decisions back against its tiers to show where its ranking and my choices
disagree, and which searches find postings I go on to apply to, so the next
setup can rework a search that rarely does. A small program checks its inputs
before it ranks and the ledger after it writes, and the reply ends with what
those checks found and any fix they call for.

**Applying** is manual. So is deciding whether a posting is applied, closed or
skipped; triage only ranks. Claude Code records a decision in the ledger when
told one.

## Why it is built this way

- **Verified beats voluminous.** Research finds postings; a browser confirms
  them. Every sweep row is opened in Chrome, on the employer's own site,
  before triage reads it, and any that has closed is cut. Nothing recalled
  from training data, no guessed links. Six real postings are a better result
  than forty plausible ones.
- **Every posting is a row.** A posting that does not fit cleanly — wrong
  city, older than 30 days, a page that would not open — goes into the table
  with a status token (`OK`, `RELOCATE`, `UNCLEAR`, `STALE`, `UNVERIFIED`)
  rather than into a paragraph under it. Everything downstream keys off rows,
  and a posting that exists only in prose is one the system cannot see.
- **The ledger only grows.** `ledger.csv` holds every posting ever surfaced.
  Triage appends to it without touching an existing row, shows that from git
  in its reply, and matches postings on company and role title, normalized,
  never on URL: the same role arrives as a LinkedIn or Indeed link from one
  run and an employer link from another. Triage only ever writes `new`;
  `applied`, `closed` and `skipped` record what a person did or found. Setup
  never writes the ledger once it exists, and its check fails a run that
  touched it.
- **Files never travel.** Every step reads the repository and writes its
  result back into it, so nothing is attached, downloaded or moved by hand,
  apart from the sweep's files: Research takes its prompt and the resume as
  attachments, and can only hand its report over as a download. A check that
  compares a file with an earlier copy reads that copy from git, and every
  version of every file is in the history.
- **Silence is never a report.** Any block a run must print has an explicit
  empty form, such as `LINK CHECK: NONE`, so a run with nothing to report
  can be told apart from one that skipped the step.
- **Max effort where a model could flatter.** Setup, its verifier and
  triage run at Max effort, because that is where a model pleases you
  instead of informing you: a first tier padded to look healthy, a check
  that passes everything. The verifier has to print its evidence under every
  pass, and so does the check of the link check's file, which runs at Max
  effort for the same reason. Both run in a fresh context, apart from the
  conversation whose work they judge. The LinkedIn and Indeed runs end at
  Max effort too: the last step of each checks every posting it collected
  against what it searched for, quoting the words that tie each one to its
  search, and holds out of the results file a description, or a keyword set in
  one location, if most of its postings fail the check. The quotes end the
  file, so triage repeats the check from them, and will not rank a file that
  carries none.
- **Searches name the work.** A LinkedIn description that opened with a
  generic job title returned generic roles, so each description leads with
  the work itself. Indeed matches the words searched for, so each keyword is a
  phrase real postings use that names the work — a technology, a standard,
  a kind of work or a title such as rendering engineer — never a generic
  title, never an everyday word ("Metal" finds fabrication jobs), and never a
  phrase mostly analysts use ("data visualization" finds BI roles).
- **The resume is read as a history.** A skills list weighs every skill the
  same; a work history shows what a career is about. The prompts that judge
  fit read it that way, so a skill that served the main work does not make a
  role built around that skill look like a match.

## Repository layout

```text
RUNBOOK.md                  Every step of a pass, as the actions to take and
                            the commands to enter
CLAUDE.md                   What Claude Code needs in every conversation
                            here: where prompts live, the ledger's rules
.claude/skills/             Claude Code commands: one for each step, reading
                            its prompt from the playbook, and /commit, which
                            reviews the changes and commits them
.claude/scripts/prompt.py   Prints a step's prompt from the playbook, for its
                            command
root/                       Permanent files, never dated or copied
  00-playbook.txt           What the commands run from: the prompts, the
                            templates setup copies, and the reasoning
  01-positioning.txt        The positioning read from setup
  02-sweep.txt              The Research prompt, covering four segments
  02-linkedin.txt           The LinkedIn prompt: five descriptions for its AI
                            job search
  02-indeed.txt             The Indeed prompt, covering four keyword sets in
                            two locations
  ledger.csv                Every posting surfaced, with its status
  resume.pdf                The resume the judging steps read
run/                        The most recent pass
  03-results.txt            Sweep results
  04-linkedin.txt           LinkedIn results
  04-indeed.txt             Indeed results
  05-triage.txt             The ranked pass
```

These are the working files of an active search, committed as they stand
after each pass. Each pass overwrites `run/`; earlier passes are in the
commit history. Filenames never change, so every command reads and writes
the same paths every pass.

## Running a pass

[`RUNBOOK.md`](RUNBOOK.md) has every step in the order a pass runs it, with
the commands to enter and what to do when something goes wrong.
[`root/00-playbook.txt`](root/00-playbook.txt) holds each step's prompt and
the reasoning behind it, the prompt templates and the segment definitions.

You will need:

- Claude Code, signed in to a Claude plan with file creation, Advanced
  Research and Claude in Chrome. `RUNBOOK.md` is written for VS Code; in the
  terminal, start Claude Code with `claude --chrome` where it says to enter
  `@browser`
- the Claude in Chrome extension, connected to Claude Code, in a Chrome
  profile logged in to LinkedIn
- auto mode for the browser steps, so the extension doesn't ask permission at
  every site

A pass does not have to happen in one sitting, or in full: the sweep and its
link check, then triage, is a real pass. Good roles close within two or three
weeks, so a longer gap between passes lets postings open and close unseen.

## Adapting it

The machinery — the file flow, the status tokens, the ledger and the checks —
is general. What ties it to my search:

- `resume.pdf`
- the passages that describe my background, in the Step 1 prompt, the prompt
  templates and the triage prompt
- the four segment definitions in the playbook's appendix
- the location rules, which target Ontario and Canada-remote roles, and the
  Toronto and Canada locations the LinkedIn and Indeed runs search

Change those, run `/setup`, which checks its own output with Step 1B, and the
three generated prompts are aimed at the new search.
