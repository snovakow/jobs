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
read — the job titles, search keywords, LinkedIn descriptions and target
companies that fit — and turns it into three standalone search prompts.
Every pass after that is Steps 2 to 5.

| Step | Where it runs | Produces |
| --- | --- | --- |
| 1. Setup | Chat | The positioning read, three search prompts and an empty ledger |
| 1B. Verify | Chat | A pass/fail check of every file setup wrote |
| 2. Sweep | Advanced Research, one run | `03-results.txt` |
| 2B. Link check | Claude in Chrome, one run | `03-results.txt` with closed postings cut |
| 3. LinkedIn AI job search | Claude in Chrome, one run | `04-linkedin.txt` |
| 3B. Indeed | Claude in Chrome, one run | `04-indeed.txt` |
| 4. Triage | Chat | `05-triage.txt` and an updated `ledger.csv` |
| 5. Apply | By hand | Status updates in `ledger.csv` |

The **sweep** searches employer career pages and hosted job boards —
Greenhouse, Lever, Ashby, Workday and the like — in one run covering four
segments: graphics and XR, video infrastructure, frontend with depth, and
Apple-platform apps that deliver visualization or media.

The **link check** exists because Research can read a posting that has already
closed: a search index, a cached copy or an aggregator keeps a posting's text
long after the employer takes it down, and a row read from one looks like any
other. Claude in Chrome opens every sweep row's link as the page now stands and
cuts the postings that have closed, before triage reads the file. Neither a
dead link nor a live aggregator page is proof on its own: employers move
between job boards, leaving old links dead while the role stays open, and an
aggregator can show a whole posting under a notice that it was removed. So the
check looks for the role on the employer's own career page, and keeps the row,
with that link, only if the role is listed there. A staffing agency's posting,
which may exist only on job boards, stays if its link is live.

The **LinkedIn run** exists because Research cannot read LinkedIn. Claude in
Chrome uses LinkedIn's AI job search in my own logged-in browser instead, in
one run: five descriptions of the job I want, two for segment 1 and one for
each other segment, each leading with the work rather than a job title.

The **Indeed run** exists for the same reason, and runs signed out. Claude in
Chrome searches Indeed for four sets of quoted keywords, one set per segment,
each searched once for Toronto and once for Canada-remote.

**Triage** merges every result file, sets aside anything already dealt with,
and ranks the rest into three tiers: apply now, apply if the first tier is
thin, and skip, with a five-word reason. For each first-tier role it names the
resume bullets to lead with and the line to open the application with, and it
gives the same advice for any lower-tier role I choose to apply to. Across the
whole pass it reports which missing skills keep coming up, and it reads my past
decisions back against its tiers to show where its ranking and my choices
disagree.

**Applying** is manual. So is marking a posting applied, closed or skipped;
triage only ranks.

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
  Triage appends to it without touching an existing row, and matches
  postings on company and role title, normalized, never on URL: the same role
  arrives as a LinkedIn or Indeed link from one run and an employer link from
  another. Triage only ever writes `new`; `applied`, `closed` and `skipped`
  record what a person did or found. Setup writes `ledger-seed.csv`, never
  `ledger.csv`, so re-running it cannot wipe the history.
- **Silence is never a report.** Any block a run must print has an explicit
  empty form, such as `LINK CHECK: NONE`, so a run with nothing to report
  can be told apart from one that skipped the step.
- **Maximum effort where a model could flatter.** Setup, its verifier and
  triage run at maximum effort, because that is where a model pleases you
  instead of informing you: a first tier padded to look healthy, a check
  that passes everything. The verifier has to print its evidence under every
  pass. The LinkedIn and Indeed runs end at maximum effort too: the last step
  of each checks every posting it collected against what it searched for,
  quoting the words that tie each one to its search, and holds out of the
  results file a description, or a keyword set in one location, if most of its
  postings fail the check. The quotes end the file, so triage repeats the check
  from them, and holds out a file that carries none.
- **Searches name the work.** A LinkedIn description that opened with a
  generic job title returned generic roles, so each description leads with
  the work itself. Indeed matches the words searched for, so each keyword is a
  phrase real postings use that names the work — a technology, a standard,
  a kind of work or a title such as rendering engineer — never a generic
  title, and never an everyday word ("Metal" finds fabrication jobs).
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
- a chat that takes six attachments on one message, which is what a full
  triage uses
- a LinkedIn login in the Chrome profile the extension runs in

A pass does not have to happen in one sitting, or in full: the sweep and its
link check, then triage, is a real pass. Good roles close within two or three
weeks, so a longer gap between passes lets postings open and close unseen.

## Adapting it

The machinery — the file flow, the status tokens, the ledger and the checks —
is general. What ties it to my search:

- `resume.pdf`
- the passages that describe my background, in the Step 1 prompt, the prompt
  templates and the triage prompt
- the four segment definitions in the runbook's appendix
- the location rules, which target Ontario and Canada-remote roles, and the
  Toronto and Canada locations the LinkedIn and Indeed runs search

Change those, run Step 1 and check its output with Step 1B, and the three
generated prompts are aimed at the new search.
