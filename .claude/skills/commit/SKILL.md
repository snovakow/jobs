---
name: commit
description: Stage every change but a pass's files, which /save commits, have its change check review them in a fresh context, and commit them as itemised commits with a subject and description each, updating README.md where a change makes it inaccurate. Stops on a failed check. Nothing is pushed; the commits wait for manual review.
argument-hint: "[notes on what changed]"
disable-model-invocation: true
model: opus
effort: max
---

# Commit

Turn every change in the working tree, except a pass's files, into a short
series of well-described commits on the current branch, then stop. The user
reviews the commits and pushes them. So this skill never pushes, never
creates or switches a branch, and never amends or rewrites a commit that
existed before it ran: everything it does stays undoable with a single
reset.

Arguments passed with the command are the user's notes on what the changes
are, such as the pass they came from or why the playbook changed. Use them
in the messages.

## 1. Stage everything but a pass's files

A pass's files are /save's: `run/`, `root/ledger.csv`,
`root/01-positioning.txt`, the `root/02-*` prompt files and
`root/resume.pdf`. /save checks and commits them cheaply, so leave them out
of every commit here, unstaging any that are staged, and name them in the
report as left for /save.

```bash
git add -A -- . ':!run' ':!root/ledger.csv' ':!root/01-positioning.txt' ':!root/02-*.txt' ':!root/resume.pdf'
git reset -q -- run root/ledger.csv root/01-positioning.txt 'root/02-*.txt' root/resume.pdf
git status
git diff --cached --stat
```

Stop and say why if nothing is staged, or if git reports a merge, rebase or
cherry-pick in progress, or a detached HEAD. Splitting commits in the middle
of one of those would tangle it. When a pass's files are all that changed,
say that /save commits them.

## 2. Review

Run the repository's checks against what is staged:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/review.py"
```

It prints one line per check and explains each flag. The checks cover the
failures that cost real work:

- **strays**: a `ledger.csv` outside `root/`
- **ledger**: every row from the last commit still present, with
  first_seen, company, role, source and url unchanged; LF endings, every
  field quoted, valid statuses and tiers; no appended row repeating a
  company and role. It has nothing to check here unless the ledger was
  staged by mistake; /save runs it on every pass's commit.
- **width**: the playbook stays within 79 columns
- **templates**: an appendix template or segment definition that changed
  without the 02-* prompt files built from it

Unstage every file the strays check names, with `git reset -q -- "<path>"`,
and leave it out of every commit. Committed, a second ledger would split the
history; left in the working tree, it waits for the user to delete it. Any
other flag does not stop the run, because the user reviews before pushing;
it goes at the top of the report instead.

Then read the diff itself, in full: the playbook, RUNBOOK.md, README.md,
CLAUDE.md, anything under `.claude/`. Look for what the checks cannot see,
such as a file that looks accidental. Leave out anything that looks like a
credential, as with a stray, and put it first in the report. The repository
is public.

If nothing is left once the strays are out, stop and say so.

Then run the `changecheck` skill. It reviews what is staged against the rest
of the system, in a fresh context at Max effort. Read its last line:

- `CHANGE CHECK: PASS`: go on.
- `CHANGE CHECK: FAIL`: stop before committing, show me its report in full,
  and leave everything staged. Commit past a FAIL only when the notes with
  the command accept every problem it names, and put those first in the
  report.
- No CHANGE CHECK line: run it again. If it still gives none, stop and say
  so.

Do not run /verify. It is Step 1B's check of the files setup writes, not a
check to make before a commit, and it costs a fresh run at Max effort.

## 3. Itemise

Split the changes into commits, one for each change a reader would want to
review or revert on its own. What usually belongs together here:

- a playbook change: root/00-playbook.txt with RUNBOOK.md where the steps
  changed, and any command under `.claude/` that runs its prompts. When an
  appendix template moved, the 02-* files rebuilt from it come later, from
  the Step 1 run that rebuilds them, saved with /save.
- a command or one of its scripts changed on its own, with the RUNBOOK.md
  lines that run it
- a README.md or CLAUDE.md change on its own

Split at file boundaries. When one file's changes serve two commits, put it
in the one it mostly belongs to and mention the rest in that commit's
description; splitting hunks across commits is fragile and rarely worth it.
Order the commits so each leaves the repository consistent, for example a
command before the playbook text that describes it.

Write each message the way this repository's history does (`git log -10`
shows it):

- **Subject**: imperative, sentence case, no full stop, under about 70
  characters. Two related changes can share one: "Write the ledger with LF,
  and say so in RUNBOOK.md".
- **Description**: wrapped at 72 columns. Say what changed and why, which
  is the reasoning a reviewer cannot get from the diff, then what was
  verified, for example "The review flags nothing and the change check
  passes; the appendix is unchanged, so no 02-* file needs rebuilding."
- **Kept public-safe**: a commit message outlives any later clean-up of the
  files it describes. Never name the employers, postings, pay or fit
  judgements in a pass, even when a change was prompted by one.
- End with the co-author trailer this session's instructions ask for, if
  any.

## 4. Update README.md where it has become untrue

README.md is the repository's public description. For each commit, ask
whether its change makes the README untrue or incomplete: the steps and
where they run, the files and folders, the design choices, what a pass
needs, or what someone adapting the system would change. Where it does,
edit the affected passage just before making that commit, so the edit lands
in it. Most commits need nothing.

Write README edits the way the README is written. Describe the idea rather
than the playbook's or RUNBOOK.md's wording, and leave model versions,
counts and prompt text to them; copying them makes the README go stale the
next time they change. Nothing from the ledger, a triage or the positioning
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

Lead with the review's flags, if any, any change check problem my notes
accepted, and every file left uncommitted with the reason, a pass's files
as left for /save. Then, for each commit in order: its short hash and
subject, its description, and its files. Close by saying that nothing was
pushed, and that `git reset --soft HEAD~<n>` undoes the run and leaves every
change staged.
