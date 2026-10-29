# Job search runbook

What to do to run a pass, step by step. Each command you type is in a code
block of its own, ready to copy.

## The pass

| Step | Command | Runs |
| --- | --- | --- |
| 1. Setup | `/setup` | Once, and when something changes |
| 2. Sweep | `/sweep` | Every pass |
| 2B. Link check | `/linkcheck` | Every pass |
| 3. LinkedIn | `/linkedin`, `/capture` | When there's time |
| 3B. Indeed | `/indeed`, `/capture` | When there's time |
| 4. Triage | `/triage` | Every pass |
| 5. Apply | `/advice` | Every pass |

Minimally, run Steps 2, 2B and 4.

To have one thread hand you each step, see Running a pass from one thread.

Don't set a model or effort for `/sweep`, `/save` or `/commit`.

To commit a change to the playbook, RUNBOOK.md or a command, in a new Claude
Code thread, enter:
```
/commit
```

## Running a pass from one thread

Optional. Runs in a Claude Code thread of its own, which hands you each step
and reviews the pass at the end.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | high |

1. Start it
   - Start a new Claude Code thread, in Auto mode.
   - Set the model and effort.
   - Enter:
     ```
     /executioner
     ```
   - Read where it says the pass stands, then set the effort its last
     line names:
     ```
     /effort max
     ```
     or:
     ```
     /effort xhigh
     ```
     or:
     ```
     /effort high
     ```
   - Then enter:
     ```
     /executioner Start
     ```
2. Run each step it hands you
   - Do what its message says, in the thread it names.
   - When that's done, come back to this thread and set the effort its
     last line names:
     ```
     /effort max
     ```
     or:
     ```
     /effort xhigh
     ```
     or:
     ```
     /effort high
     ```
   - Then enter:
     ```
     /executioner Continue
     ```
3. When it says the steps are done
   - For its review of the pass, set the effort its last line names, as in
     item 2, then enter:
     ```
     /executioner Continue
     ```
   - Or, to leave the review out this pass, enter:
     ```
     /executioner Skip
     ```
4. When it proposes changes, during the pass or in its review
   - Read them, then set the effort its last line names, as in item 2.
   - To make them all, enter:
     ```
     /executioner Approve
     ```
   - To make only some, enter `/executioner Approve` followed by their
     numbers, and say why you leave out the others:
     ```
     /executioner Approve
     ```
   - To make none of them, enter `/executioner Decline` followed by why:
     ```
     /executioner Decline
     ```
   - Then do what its message says, as in item 2.
5. To carry on a pass in a new thread, start it as in item 1.

## Before the first pass

1. Connect Chrome
   - In any Claude Code thread, enter:
     ```
     /chrome
     ```
   - Check that it shows Status: Enabled and Extension: Installed.
2. Set up the Chrome profile the extension runs in
   - Log in to LinkedIn.
   - Sign out of Indeed.
3. Check claude.ai
   - File creation is on in your settings.
   - A Research thread accepts three attachments on one message.

## Step 1 — Setup

Run once. Run again only after one of these:
- a new skill, or a materially revised resume
- a change in what you're aiming at
- a change to a search prompt template that its prompt file doesn't carry
  yet
- a segment still thin on the sweep's Maximum setting
- all four segments thin
- triage's item 2b saying to re-run Step 1, or to rework a search

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | Max |
| Maximum | Fable | Max |

1. Save any ledger edits
   - In any Claude Code thread, enter:
     ```
     /save
     ```
2. Run setup
   - Start a new Claude Code thread.
   - Set the model and effort.
   - Enter:
     ```
     /setup
     ```
   - Wait for it to finish.
   - If it stops on a file that failed twice:
     - Read both reports.
     - Enter what to change. Or fix the file yourself, then enter:
       ```
       /verify
       ```
3. Read Part A item 4 in its reply.
4. Save the files
   - In any Claude Code thread, enter:
     ```
     /save
     ```

## Step 2 — Sweep

Runs in a claude.ai Research thread, then Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Sonnet | Max |
| Maximum | Opus | Max |

1. Run the sweep
   - In claude.ai, start a new thread with Research on.
   - Set the model and effort.
   - Attach `root/resume.pdf` and `root/02-sweep.txt` from the repo, and
     `run/03-results.txt` if it exists.
   - Copy this message, paste it, and send:
     ```
     Run the job search in the attached prompt file. My resume is attached too,
     and so is the last sweep's results file when there is one. Follow the
     prompt file's location, recency and verification rules strictly, and use
     its output format exactly.
     ```
   - Wait for the report.
2. Get the file
   - In the same thread, turn Research off and switch to Sonnet at low effort.
   - Copy this message, paste it, and send:
     ```
     Write the whole report to a file, verbatim — one table with every row from
     every research run in this thread, every URL and every status token intact;
     then each research run's closing notes under a heading line of their own,
     CLOSING NOTES, RUN 1 above the first run's and CLOSING NOTES, RUN 2 above a
     second run's; then the latest COVERAGE block, as the last thing in the file.
     Leave out the results file attached to my first message: its rows and notes
     are the last sweep's, not a run in this thread. Don't re-rank, summarize,
     drop rows, or move any row out of the table.

     Name the file 03-results.txt. No date in the filename.

     Plain text, no markdown: pipe-delimited table, dashed rule under the header,
     no # or **. Give me the download link.
     ```
   - Download the file it writes.
   - Move the download into the repo, replacing `run/03-results.txt`.
3. Check the file
   - In any Claude Code thread, enter:
     ```
     /sweep
     ```
   - If it reports a warning sign, act on it as the table below says.
4. Continue the sweep, if /sweep says to
   - In the same claude.ai thread, turn Research on and set the step's model
     and effort.
   - Copy this message, paste it, and send:
     ```
     Continue the job search. In each segment, check the target companies your
     COVERAGE block lists as not reached and search the keyword strings it lists
     as not searched, in the order it gives them, under every rule in the prompt
     file. Add every posting you find as a row in the same table format, give
     your closing notes for this run, and end with the COVERAGE block brought up
     to date for both runs.
     ```
   - If claude.ai says there isn't enough usage left for a research run, do
     Steps 3 and 3B, then come back to this item.
   - Wait for the report, then do items 2 and 3 again.
5. Save the file
   - In any Claude Code thread, enter:
     ```
     /save
     ```

| Warning sign | What to do |
| --- | --- |
| A row with no status token | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| US locations marked OK, or forty rows in one segment | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| A posting named in the closing notes with no row | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, then enter `/verify`. If it fixed drift, run the sweep again. If it found none, go on to the next step /sweep names |
| More RELOCATE rows than OK rows, on six rows or more | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| iOS roles with no video, 3D or visualization in the product, or full-stack roles that are really server or cloud infrastructure | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, then enter `/verify`. If it fixed drift, run the sweep again. If it found none, go on to the next step /sweep names |
| A segment with three rows or fewer through a full round of its targets | Run the sweep at the Maximum setting from then on. Still thin there, or all four segments thin at once: run Step 1 |
| No COVERAGE block, or one with lines missing | In the same claude.ai thread, with Research off, on Sonnet at low effort, send `Add the COVERAGE block the prompt file asks for, from what your report says you checked and searched, and write the file again.` Then move the download into the repo and enter `/sweep` again |
| Rows copied from the last pass's file | In the same claude.ai thread, with Research off, on Sonnet at low effort, send item 2's message again. Then move the download into the repo and enter `/sweep` again |
| /sweep won't check the file | Check you moved the report's file into `run/03-results.txt`. If it's in markdown, ask the claude.ai thread for it again, in plain text |

To run the sweep again, first, in a new Claude Code thread on Sonnet at
low effort, enter:
```
Restore run/03-results.txt as it was in the last commit that changed run/05-triage.txt, or delete it if no commit changed that file.
```
Then start again from item 1, in a new claude.ai thread.

Ask for a drift fix in a new Claude Code thread on Sonnet at high
effort. Then, in the same thread, enter:
```
/verify
```

## Step 2B — Link check

Runs in your Chrome, driven from Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | xhigh |
| Maximum | Opus | Max |

1. Run the link check
   - Start a new Claude Code thread, in Auto mode.
   - Set the model and effort.
   - Enter:
     ```
     @browser
     ```
   - Enter:
     ```
     /linkcheck
     ```
   - Wait for the DIFF CHECK verdict. PASS or REBUILT ends the step.
2. If it stops and shows two FAIL verdicts
   - In a new Claude Code thread on Sonnet at low effort, enter:
     ```
     Restore run/03-results.txt from its last commit.
     ```
   - Start this step again.

## Step 3 — LinkedIn

Runs in your Chrome, driven from Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | xhigh |
| Maximum | Opus | Max |

1. Run the search
   - Start a new Claude Code thread, in Auto mode.
   - Set the model and effort.
   - Enter:
     ```
     @browser
     ```
   - Enter:
     ```
     /linkedin
     ```
   - If asked to log in to LinkedIn, do so, then enter:
     ```
     Continue
     ```
   - Wait for the run to stop.
2. Check the capture
   - In the same thread, enter:
     ```
     /capture
     ```
   - Wait for the CAPTURE CHECK verdict. If no verdict appears, repeat this
     item.
3. If the verdict is FAIL, choose one:
   - Re-run the failed searches. In the same thread, enter:
     ```
     Re-run
     ```
     When the run stops, go back to item 2.
   - Leave the gap this pass. In a new Claude Code thread on Sonnet at
     high effort, enter:
     ```
     Check root/02-linkedin.txt against its template and fix any drift.
     ```
     Then enter:
     ```
     /verify
     ```

## Step 3B — Indeed

Runs in your Chrome, driven from Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | xhigh |
| Maximum | Opus | Max |

1. Run the search
   - Start a new Claude Code thread, in Auto mode.
   - Set the model and effort.
   - Enter:
     ```
     @browser
     ```
   - Enter:
     ```
     /indeed
     ```
   - If asked to sign out of Indeed, do so, then enter:
     ```
     Continue
     ```
   - Wait for the run to stop.
2. Check the capture
   - In the same thread, enter:
     ```
     /capture
     ```
   - Wait for the CAPTURE CHECK verdict. If no verdict appears, repeat this
     item.
3. If the verdict is FAIL, choose one:
   - Re-run the failed searches. In the same thread, enter:
     ```
     Re-run
     ```
     When the run stops, go back to item 2.
   - Leave the gap this pass. In a new Claude Code thread on Sonnet at
     high effort, enter:
     ```
     Check root/02-indeed.txt against its template and fix any drift.
     ```
     Then enter:
     ```
     /verify
     ```

## Step 4 — Triage

Runs in Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | Max |
| Maximum | Fable | Max |

1. Save the pass so far
   - In any Claude Code thread, enter:
     ```
     /save
     ```
2. Run triage
   - Start a new Claude Code thread.
   - Set the model and effort.
   - Enter:
     ```
     /triage
     ```
   - Wait for it to finish.
   - Keep this thread for Step 5.
3. Read its reply
   - If the To do line in the CHECKS block at its end names anything, do it.
   - If the ranking shows one of the triage problems under If something goes
     wrong, make its fix now.
4. Save the triage
   - In any Claude Code thread, enter:
     ```
     /save
     ```

## Step 5 — Apply

You, with Claude Code, in the triage thread.

1. Decide each row, Tier 1 first
   - First, in the triage thread, enter:
     ```
     /effort medium
     ```
   - The rows: every row in `root/ledger.csv` at new, and every row triage's
     reply marks as reopened or changed.
   - A row at applied stays applied, even when triage says its posting
     changed.
   - A row that repeats a role already in the ledger takes the earlier row's
     status, unless that is closed: then decide it like any other row.
   - If its title, or on a tier 3 row its five-word reason, rules it out,
     set it to skipped.
   - Otherwise open its URL, read the posting, and set one of:

     | Status | When |
     | --- | --- |
     | skipped | Not worth applying to |
     | closed | Gone when you went to act on it |
     | applied | You submitted. Set it as you send it. It stays applied whatever comes back, a rejection included |
     | new | Undecided, even on a row back from closed or skipped |

   - To set a status, edit it in `root/ledger.csv`, or tell Claude Code the
     company, the role and the status.
2. Apply
   - When you want to tailor the resume or write a cover letter or note for
     a row, use its advice.
   - For a Tier 1 row, the advice is in item 3 of `run/05-triage.txt`.
   - For any other row, in the triage thread, enter:
     ```
     @browser
     ```
   - Then enter `/advice` followed by the company and role of each:
     ```
     /advice
     ```
   - Check any advice marked "unread posting" against the posting before you
     use it.
3. Add another role (optional)
   - For a role from the company's own board, or from triage's LEADS list,
     tell the triage thread its URL, its status and your tier.
4. Make the tier check
   - In the triage thread, enter:
     ```
     Make the tier check: give each ledger row you ranked into a different tier this pass's tier, unless it was at applied or skipped before this pass and still is.
     ```
5. Save the ledger
   - In any Claude Code thread, enter:
     ```
     /save
     ```

## If something goes wrong

### Chrome asks permission at each new site

- Start the step again in a new thread at the step's setting, in Auto
  mode. Before the step's command, enter:
  ```
  @browser
  ```

### A browser step asks which Chrome to use

- Choose the option that opens a confirmation screen in every connected
  Chrome.
- In the Chrome on this computer, click Connect.

### A browser run stops working partway

- In the run's thread, enter:
  ```
  /chrome
  ```
- Select Reconnect extension.
- If it was `/advice` that stopped, enter `/advice` again with the same
  roles. Otherwise, enter:
  ```
  Continue from where you stopped.
  ```

### A command stops and asks for another model or effort

- In the thread where it stopped, enter the `/model` or `/effort`
  command it gives, then enter again what you entered when it stopped.

### /linkcheck stops before opening anything

- If it says the file has uncommitted changes, in any Claude Code
  thread, enter:
  ```
  /save
  ```
  Then start Step 2B again.
- If it says the file already ends with a LINK CHECK block, run Step 2
  first.

### /setup or /triage says the ledger has uncommitted changes

- If they're your status edits, in any Claude Code thread, enter:
  ```
  /save
  ```
- If a triage added them this pass, in a new Claude Code thread on
  Sonnet at low effort, enter:
  ```
  Restore root/ledger.csv and run/05-triage.txt from their last commit.
  ```
- Start the step again.

### /save stops on a review flag

- If it names a stray ledger.csv, delete that file.
- If it names a ledger problem, in a new Claude Code thread on Sonnet
  at medium effort, enter the following, then paste the review lines /save
  showed:
  ```
  Fix the ledger problems this review names, and change nothing else.
  ```
- Then, in any Claude Code thread, enter:
  ```
  /save
  ```

### Triage ranks iOS or infrastructure full-stack roles too high

- An iOS role with no video, 3D or visualization in the product, or a
  full-stack role that is really server or cloud infrastructure, belongs in
  tier 3. A native role on a video or visualization product that asks for
  current Apple-platform depth goes no higher than tier 2.
- Before Step 4 saves the triage, in the triage thread, at Max
  effort, enter:
  ```
  Read my resume by its work history, as item 2 says, and re-rank.
  ```
- Once the triage is saved, decide the role in Step 5 instead.

### Triage ranks a US-only role as if it were local

- If its row carries RELOCATE, leave it.
- If it carries no status token, before Step 4 saves the triage, in the
  triage thread, at Max effort, enter:
  ```
  Carry every row's status token through, as item 1b says, and re-rank.
  ```
  Once the triage is saved, decide the role in Step 5 instead, and restore
  its token as "A ledger row's notes don't start with a status token" says.

### A role you already applied to comes back in the ranking

- Before Step 4 saves the triage, in the triage thread, at Max
  effort, enter:
  ```
  Dedupe on company plus role title, normalized as item 1 says, and re-rank.
  ```
- Once the triage is saved, set the row that repeats it to applied in Step 5.

### A ledger row's notes don't start with a status token

- In a new Claude Code thread on Sonnet at high effort, enter:
  ```
  Restore the status token at the front of each ledger row's notes that lacks one, from the results of the pass that added it.
  ```

### This pass's ledger rows have no "gap:" in their notes

- In the triage thread, at medium effort, enter:
  ```
  Add "gap: " and the single biggest gap to the notes of each row you appended this pass.
  ```
- Leave older rows as they are.

### A status you set is gone

- In a new Claude Code thread on Sonnet at medium effort, give the
  company and the role, and ask it to restore the status from the ledger's
  git history.

### The same roles come back every pass

- Decide their statuses in Step 5.

### Tier 3 rows have piled up at new

- In Step 5, read their five-word reasons, not the postings, and tell the
  triage thread which to set to skipped.
- If more than a couple are worth keeping, run Step 1.

### /commit stops on a CHANGE CHECK FAIL

- In the thread that made the change, or a new Claude Code
  thread on Opus at high effort, enter the following, then paste the
  report:
  ```
  Fix the problems this CHANGE CHECK report names.
  ```
  Or fix the files yourself.
- Then, in a new Claude Code thread, enter:
  ```
  /commit
  ```
- To commit past a problem instead, in a new Claude Code thread,
  enter this, followed by a note accepting the problem:
  ```
  /commit
  ```

### A prompt file has a section header ending in a dash

- In a new Claude Code thread on Sonnet at high effort, enter:
  ```
  Check the root/02-* prompt files against their templates and fix any drift.
  ```
- Then enter:
  ```
  /verify
  ```
