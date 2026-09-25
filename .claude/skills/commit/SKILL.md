---
name: commit
description: Stage all changes, review them, and commit them as itemised commits with a subject and description each, updating README.md where a change makes it inaccurate. Nothing is pushed; the commits wait for manual review.
argument-hint: "[notes on what changed]"
disable-model-invocation: true
model: opus
effort: max
---

# Commit

Turn everything in the working tree into a short series of well-described
commits on the current branch, then stop. The user reviews the commits and
pushes them. So this skill never pushes, never creates or switches a branch,
and never amends or rewrites a commit that existed before it ran: everything
it does stays undoable with a single reset.

Arguments passed with the command are the user's notes on what the changes
are, such as the pass they came from or why the runbook changed. Use them in
the messages.

## 1. Stage everything

```bash
git add -A
git status
git diff --cached --stat
```

Stop and say why if nothing is staged, or if git reports a merge, rebase or
cherry-pick in progress, or a detached HEAD. Splitting commits in the middle
of one of those would tangle it.

## 2. Review

Run the repository's checks against what is staged:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/review.py"
```

It prints one line per check and explains each flag. The checks cover the
failures the runbook names as the ones that cost real work:

- **strays**: a download with a duplicate counter, like
  `03-results-seg1 (1).txt`; a `ledger.csv` outside `root/`; a leftover
  `ledger-seed.csv`
- **ledger**: every row from the last commit still present, with
  first_seen, company, role, source and url unchanged; LF endings, every
  field quoted, valid statuses and tiers; no appended row repeating a
  company and role. Its summary counts rows appended and statuses changed,
  which a pass's commit message uses.
- **prompts**: the quick guide carries the runbook's prompts byte for byte
- **width**: the runbook and the quick guide stay within 79 columns
- **templates**: an appendix template or segment definition that changed
  without the 02-* prompt files built from it

Unstage every file the strays check names, with `git reset -q -- "<path>"`,
and leave it out of every commit. Committed, a stale copy files the wrong
pass's results; left in the working tree, it waits for the user to delete
or rename it. Any other flag does not stop the run, because the user reviews
before pushing; it goes at the top of the report instead.

Then read the diff itself. Read the diffs of hand-edited files in full: the
runbook, the quick guide, README.md, anything under `.claude/`. For
generated files, such as a pass's results or the 02-* files from a Step 1
run, read enough to know what produced them. Look for what the checks
cannot see: a file that looks accidental, results that seem to come from
two different passes. Leave out anything that looks like a credential, as
with a stray, and put it first in the report. The repository is public.

If nothing is left once the strays are out, stop and say so.

## 3. Itemise

Split the changes into commits, one for each change a reader would want to
review or revert on its own. What usually belongs together here:

- a pass: its run results and the updated ledger
- a Step 4B patch: the 02-linkedin-* pair it swapped a keyword in, and the
  lines appended to keyword-edits.txt
- a Step 1 run: 01-positioning.txt, the 02-* files, the rejection lines
  appended to keyword-edits.txt, and resume.pdf when a revision prompted it
- a runbook change: root/00-runbook.txt with its mirror in the quick guide,
  and the 02-* files when an appendix template moved
- ledger status edits made by hand between passes

Split at file boundaries. When one file's changes serve two commits, put it
in the one it mostly belongs to and mention the rest in that commit's
description; splitting hunks across commits is fragile and rarely worth it.
Order the commits so each leaves the repository consistent, for example a
runbook change before the 02-* files regenerated from it.

Write each message the way this repository's history does (`git log -10`
shows it):

- **Subject**: imperative, sentence case, no full stop, under about 70
  characters. Two related changes can share one: "Write the ledger with LF,
  and resync the quick guide".
- **Description**: wrapped at 72 columns. Say what changed and why, which
  is the reasoning a reviewer cannot get from the diff, then what was
  verified, for example "Mirrored in 00-runbook-quick-guide.txt, all seven
  prompt blocks byte-identical." For a pass, give its coverage, meaning
  which sweeps and LinkedIn runs it has, and the review's ledger summary.
- **Kept public-safe**: a commit message outlives any later clean-up of the
  files it describes. Describe a pass by coverage and counts, never by the
  employers, postings, pay or fit judgements in it.
- End with the co-author trailer this session's instructions ask for, if
  any.

## 4. Update README.md where it has become untrue

README.md is the repository's public description. For each commit, ask
whether its change makes the README untrue or incomplete: the steps and
where they run, the files and folders, the design choices, what a pass
needs, or what someone adapting the system would change. Where it does,
edit the affected passage just before making that commit, so the edit lands
in it. Most commits need nothing: a pass's results, ledger rows and keyword
swaps never change what the README says.

Write README edits the way the README is written. Describe the idea rather
than the runbook's wording, and leave model versions, counts and prompt
text to the runbook; copying them makes the README go stale the next time
the runbook changes. Nothing from the ledger, a triage or the positioning
read belongs in it. Wrap prose at 79 columns.

## 5. Commit

With a single commit, commit what is staged, adding any README edit first.
With several, unstage everything, then stage and commit each in turn:

```bash
git reset -q
git add -A -- <this commit's paths>
git commit -F - <<'EOF'
<subject>

<description>
EOF
```

`git add -A -- <path>` stages deletions as well as edits. If a hook rejects
a commit, fix the cause and commit again rather than bypassing it.

Afterwards, `git status --short` should list only the files deliberately
left out. Anything else still listed was missed: commit it where it
belongs.

## 6. Report

Lead with the review's flags, if any, and every file left uncommitted with
the reason. Then, for each commit in order: its short hash and subject, its
description, and its files. Close by saying that nothing was pushed, and
that `git reset --soft HEAD~<n>` undoes the run and leaves every change
staged.
