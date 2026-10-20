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

Don't set a model or effort for `/sweep` or `/save`. Commit a change to the
playbook, RUNBOOK.md or a command with `/commit`, in a new conversation.

## Before the first pass

1. Connect Chrome
   - In any Claude Code conversation, enter:
     ```
     /chrome
     ```
   - Check that it shows Status: Enabled and Extension: Installed.
2. Set up the Chrome profile the extension runs in
   - Log in to LinkedIn.
   - Sign out of Indeed.
3. Check claude.ai
   - File creation is on in your settings.
   - A Research chat accepts two attachments on one message.

## Step 1 — Setup

Run once. Run again only after one of these:
- a new skill, or a materially revised resume
- a change in what you're aiming at
- a change to a search prompt template
- a segment still thin on the sweep's Maximum setting
- all four segments thin on two passes in a row
- triage's item 2b saying to re-run Step 1, or to rework a search

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | Max |
| Maximum | Fable | Max |

1. Save any ledger edits
   - In any Claude Code conversation, enter:
     ```
     /save
     ```
2. Run setup
   - Start a new Claude Code conversation.
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
   - In any Claude Code conversation, enter:
     ```
     /save
     ```

## Step 2 — Sweep

Runs in a claude.ai Research chat, then Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Sonnet | Max |
| Maximum | Opus | Max |

1. Run the sweep
   - In claude.ai, start a new chat with Research on.
   - Set the model and effort.
   - Attach `root/resume.pdf` and `root/02-sweep.txt` from the repo.
   - Copy this message, paste it, and send:
     ```
     Run the job search in the attached prompt file. My resume is attached too.
     Follow its location, recency and verification rules strictly, and use its
     output format exactly.
     ```
   - Wait for the report.
2. Get the file
   - In the same chat, turn Research off and switch to Sonnet at low effort.
   - Copy this message, paste it, and send:
     ```
     Write that report to a file, verbatim — the full table with every URL and
     every status token intact, and the closing notes. Don't re-rank, summarize,
     drop rows, or move any row out of the table.

     Name the file 03-results.txt. No date in the filename.

     Plain text, no markdown: pipe-delimited table, dashed rule under the header,
     no # or **. Give me the download link.
     ```
   - Download the file it writes.
   - Move the download into the repo, replacing `run/03-results.txt`.
3. Check the file
   - In any Claude Code conversation, enter:
     ```
     /sweep
     ```
   - If it reports a warning sign, act on it as the table below says.
4. Save the file
   - In any Claude Code conversation, enter:
     ```
     /save
     ```

| Warning sign | What to do |
| --- | --- |
| A row with no status token | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| US locations marked OK, or forty rows in one segment | Run the sweep again |
| A posting named in the closing notes with no row | Run the sweep again |
| More RELOCATE rows than OK rows, on six rows or more | Run the sweep again. If it happens twice, ask Claude Code to check 02-sweep.txt against its template and fix any drift, then enter `/verify` |
| iOS roles with no video, 3D or visualization in the product, or cloud full-stack roles | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| A segment with three rows or fewer, two passes running | Run the sweep at the Maximum setting from then on. Still thin there: run Step 1 |
| /sweep won't check the file | Check you moved the report's file into `run/03-results.txt`. If it's in markdown, ask the claude.ai chat for it again, in plain text |

Ask for a drift fix in a new Claude Code conversation on Sonnet at high
effort, then enter `/verify` in the same conversation.

## Step 2B — Link check

Runs in your Chrome, driven from Claude Code.

| Setting | Model | Effort |
| --- | --- | --- |
| Recommended | Opus | xhigh |
| Maximum | Opus | Max |

1. Run the link check
   - Start a new Claude Code conversation, in Auto mode.
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
2. If it stops after a second FAIL
   - In a new Claude Code conversation on Haiku at low effort, enter:
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
   - Start a new Claude Code conversation, in Auto mode.
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
   - In the same conversation, enter:
     ```
     /capture
     ```
   - Wait for the CAPTURE CHECK verdict. If no verdict appears, repeat this
     item.
3. If the verdict is FAIL, choose one:
   - Re-run the failed searches. In the same conversation, enter:
     ```
     Re-run
     ```
     When the run stops, go back to item 2.
   - Leave the gap this pass. In a new Claude Code conversation on Sonnet at
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
   - Start a new Claude Code conversation, in Auto mode.
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
   - In the same conversation, enter:
     ```
     /capture
     ```
   - Wait for the CAPTURE CHECK verdict. If no verdict appears, repeat this
     item.
3. If the verdict is FAIL, choose one:
   - Re-run the failed searches. In the same conversation, enter:
     ```
     Re-run
     ```
     When the run stops, go back to item 2.
   - Leave the gap this pass. In a new Claude Code conversation on Sonnet at
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
   - In any Claude Code conversation, enter:
     ```
     /save
     ```
2. Run triage
   - Start a new Claude Code conversation.
   - Set the model and effort.
   - Enter:
     ```
     /triage
     ```
   - Wait for it to finish.
   - Keep this conversation for Step 5.
3. Read the CHECKS block at the end of its reply
   - If its To do line names anything, do it.
4. Save the triage
   - In any Claude Code conversation, enter:
     ```
     /save
     ```

## Step 5 — Apply

You, with Claude Code, in the triage conversation.

1. Decide each row, Tier 1 first
   - First, in the triage conversation, enter:
     ```
     /effort medium
     ```
   - The rows: every row in `root/ledger.csv` at new, and every row triage's
     reply marks as reopened or changed.
   - A row at applied stays applied, even when triage says its posting
     changed.
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
   - For a Tier 1 row, use its advice in item 3 of `run/05-triage.txt`.
   - For any other row, in the triage conversation, enter `/advice` followed
     by the company and role of each:
     ```
     /advice
     ```
   - Check any advice marked "unread posting" against the posting before you
     use it.
3. Add another role (optional)
   - For a role from the company's own board, or from triage's LEADS list,
     tell the triage conversation its URL, its status and your tier.
4. Make the tier check
   - In the triage conversation, enter:
     ```
     Make the tier check: give each ledger row you ranked into a different tier this pass's tier, unless it was at applied or skipped before this pass and still is.
     ```
5. Save the ledger
   - In any Claude Code conversation, enter:
     ```
     /save
     ```

## If something goes wrong

For a fix at Max effort in the triage conversation, enter `/effort max`
first if Step 5 has lowered it, and `/effort medium` after it to go on with
Step 5.

### Chrome asks permission at each new site

- Start the step again in a new conversation at the step's setting, in Auto
  mode, and enter `@browser` before the step's command.

### A browser run stops working partway

- In the run's conversation, enter:
  ```
  /chrome
  ```
- Select Reconnect extension.
- Enter:
  ```
  Continue from where you stopped.
  ```

### A command stops and asks for another model or effort

- In the conversation where it stopped, enter the `/model` or `/effort`
  command it gives, then enter the command again.

### /linkcheck stops before opening anything

- If it says the file has uncommitted changes, in any Claude Code
  conversation, enter:
  ```
  /save
  ```
  Then start Step 2B again.
- If it says the file already ends with a LINK CHECK block, run Step 2
  first.

### /setup or /triage says the ledger has uncommitted changes

- If they're your status edits, in any Claude Code conversation, enter:
  ```
  /save
  ```
- If a triage added them this pass, in a new Claude Code conversation on
  Haiku at low effort, enter:
  ```
  Restore root/ledger.csv and run/05-triage.txt from their last commit.
  ```
- Start the step again.

### /save stops on a review flag

- If it names a stray ledger.csv, delete that file.
- If it names a ledger problem, in a new Claude Code conversation on Sonnet
  at medium effort, enter the following, then paste the review lines /save
  showed:
  ```
  Fix the ledger problems this review names, and change nothing else.
  ```
- Then, in any Claude Code conversation, enter:
  ```
  /save
  ```

### Triage ranks iOS or cloud full-stack roles too high

- An iOS role with no video, 3D or visualization in the product, or a cloud
  full-stack role, belongs in tier 3. A native role on a video or
  visualization product that asks for current Apple-platform depth goes no
  higher than tier 2.
- In the triage conversation, at Max effort, enter:
  ```
  Read my resume by its work history, as item 2 says, and re-rank.
  ```

### Triage ranks a US-only role as if it were local

- If its row carries RELOCATE, leave it.
- If it carries no status token, in the triage conversation, at Max effort,
  enter:
  ```
  Carry every row's status token through, as item 1b says, and re-rank.
  ```

### A role you already applied to comes back in the ranking

- In the triage conversation, at Max effort, enter:
  ```
  Dedupe on company plus role title, normalized as item 1 says, and re-rank.
  ```

### A ledger row's notes don't start with a status token

- In a new Claude Code conversation on Sonnet at high effort, enter:
  ```
  Restore the status token at the front of each ledger row's notes that lacks one, from the results of the pass that added it.
  ```

### This pass's ledger rows have no "gap:" in their notes

- In the triage conversation, at medium effort, enter:
  ```
  Add "gap: " and the single biggest gap to the notes of each row you appended this pass.
  ```
- Leave older rows as they are.

### A status you set is gone

- In a new Claude Code conversation on Sonnet at medium effort, give the
  company and the role, and ask it to restore the status from the ledger's
  git history.

### The same roles come back every pass

- Decide their statuses in Step 5.

### Tier 3 rows have piled up at new

- In Step 5, read their five-word reasons, not the postings, and tell the
  triage conversation which to set to skipped.
- If more than a couple are worth keeping, run Step 1.

### /commit stops on a CHANGE CHECK FAIL

- In the conversation that made the change, or a new Claude Code
  conversation on Opus at high effort, enter the following, then paste the
  report:
  ```
  Fix the problems this CHANGE CHECK report names.
  ```
  Or fix the files yourself.
- Then, in a new Claude Code conversation, enter:
  ```
  /commit
  ```
- To commit past a problem instead, enter `/commit` followed by a note
  accepting it.

### A prompt file has a section header ending in a dash

- In a new Claude Code conversation on Sonnet at high effort, enter:
  ```
  Check the root/02-* prompt files against their templates and fix any drift.
  ```
- Then enter:
  ```
  /verify
  ```
