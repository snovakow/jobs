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

## Before the first pass

1. Connect Chrome
   - In Claude Code, enter:
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

1. Commit any ledger edits
   - Enter:
     ```
     /commit
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
4. Commit
   - Enter:
     ```
     /commit
     ```

## Step 2 — Sweep

Runs in a claude.ai Research chat. Claude Code takes the file back.

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
   - In the same chat, copy this message, paste it, and send:
     ```
     Write that report to a file, verbatim — the full table with every URL and
     every status token intact, and the closing notes. Don't re-rank, summarize,
     drop rows, or move any row out of the table.

     Name the file 03-results.txt. No date in the filename.

     Plain text, no markdown: pipe-delimited table, dashed rule under the header,
     no # or **. Give me the download link.
     ```
   - Download the file it writes.
3. Move the download into the repo, replacing `run/03-results.txt`
   - In Claude Code, enter:
     ```
     /sweep
     ```
   - If it reports a warning sign, act on it as the table below says.
4. Commit
   - Enter:
     ```
     /commit
     ```

| Warning sign | What to do |
| --- | --- |
| A row with no status token | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| US locations marked OK, or forty rows in one segment | Run the sweep again |
| A posting named in the closing notes with no row | Run the sweep again |
| More RELOCATE rows than OK rows, on six rows or more | Run the sweep again. If it happens twice, ask Claude Code to check 02-sweep.txt against its template and fix any drift, then enter `/verify` |
| Senior iOS or cloud full-stack roles | Ask Claude Code to check 02-sweep.txt against its template and fix any drift, enter `/verify`, then run the sweep again |
| A segment with three rows or fewer, two passes running | Run the sweep at the Maximum setting from then on. Still thin there: run Step 1 |
| /sweep won't take the file in | Check you downloaded the report's file. If it's in markdown, ask the claude.ai chat for it again, in plain text |

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
   - Ask Claude Code to restore `run/03-results.txt` from its last commit.
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
   - Leave the gap this pass. In the same conversation, enter:
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
   - Leave the gap this pass. In the same conversation, enter:
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

1. Commit any ledger edits
   - Enter:
     ```
     /commit
     ```
2. Run triage
   - Start a new Claude Code conversation.
   - Set the model and effort.
   - Enter:
     ```
     /triage
     ```
   - Wait for it to finish.
   - Keep this conversation. Step 5 continues in it.
3. Read the CHECKS block at the end of its reply
   - If its To do line names anything, do it.
4. Commit
   - Enter:
     ```
     /commit
     ```

## Step 5 — Apply

You, with Claude Code.

1. Decide each row, Tier 1 first
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
     tell Claude Code its URL, its status and your tier.
4. Make the tier check
   - In the triage conversation, enter:
     ```
     Make the tier check: give each ledger row you ranked into a different tier this pass's tier, unless it was at applied or skipped before this pass and still is.
     ```
5. Commit
   - Enter:
     ```
     /commit
     ```

## If something goes wrong

### Chrome asks permission at each new site

- Start the step again in a new conversation, in Auto mode, and enter
  `@browser` before the step's command.

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

### A browser command stops and asks for xhigh effort

- The session's effort is below xhigh, where a run opens fewer pages than
  its prompt calls for. Enter:
  ```
  /effort xhigh
  ```
  Or `/effort max` for the Maximum setting. Then enter the command again.

### /linkcheck stops before opening anything

- If it says the file has uncommitted changes, the sweep's file isn't
  committed. Enter:
  ```
  /commit
  ```
  Then start Step 2B again.
- If it says the file already ends with a LINK CHECK block, no new sweep
  has come in since the last link check. Run Step 2 first.

### /setup or /triage stops before starting

- The ledger has uncommitted changes. If they're your status edits, enter:
  ```
  /commit
  ```
- If a triage already added rows this pass, enter:
  ```
  Restore root/ledger.csv and run/05-triage.txt from their last commit.
  ```
- Start the step again.

### Triage ranks senior iOS or cloud full-stack roles above tier 3

- In the triage conversation, enter:
  ```
  Read my resume by its work history, as item 2 says, and re-rank.
  ```

### Triage ranks a US-only role as if it were local

- If its row carries RELOCATE, that's correct. Nothing to do.
- If it carries no status token, in the triage conversation, enter:
  ```
  Carry every row's status token through, as item 1b says, and re-rank.
  ```

### A role you already applied to comes back in the ranking

- In the triage conversation, enter:
  ```
  Dedupe on company plus role title, normalized as item 1 says, and re-rank.
  ```

### A ledger row's notes don't start with a status token

- Enter:
  ```
  Restore the status token at the front of each ledger row's notes that lacks one, from the results of the pass that added it.
  ```

### This pass's ledger rows have no "gap:" in their notes

- In the triage conversation, enter:
  ```
  Add "gap: " and the single biggest gap to the notes of each row you appended this pass.
  ```
- Leave older rows as they are.

### A status you set is gone

- Tell Claude Code the company and the role, and ask it to restore the
  status from the ledger's git history.

### The same roles come back every pass

- Their statuses were never set. Decide them in Step 5.

### Tier 3 rows have piled up at new

- Read their five-word reasons, not the postings, and tell Claude Code which
  to set to skipped.
- If more than a couple are worth keeping, run Step 1.

### A prompt file has a section header ending in a dash

- Enter:
  ```
  Check the root/02-* prompt files against their templates and fix any drift.
  ```
- Then enter:
  ```
  /verify
  ```
