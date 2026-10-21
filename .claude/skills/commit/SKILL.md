---
name: commit
description: Stage every change but a pass's files, which /save commits, have its change check review them in a fresh context, and commit them as itemised commits with a subject and description each, updating README.md where a change makes it inaccurate. Stops on a failed check, and unless it is the first thing in its thread. Nothing is pushed; the commits wait for manual review.
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
existed before it ran, except the unpushed commits the user says to take
back (step 1): everything it does stays undoable with a single reset.

Arguments passed with the command are the user's notes on what the changes
are, such as the pass they came from or why the playbook changed. Use them
in the messages.

Run in a new thread, as the first thing in it. A thread that
made the changes remembers making them and cannot review them from the
repository alone, and one that has already run this would run it again over
the same work. So if anything precedes this command in the thread, an
earlier message, work done here or a summary carried over from a longer
context, stop before anything is read or run, and say to start a new
thread with `/commit` as its first message.

## 1. Stage everything but a pass's files

First run `git status`. Stop and say why if it reports a merge, rebase or
cherry-pick in progress, or a detached HEAD. Taking commits back or
splitting them in the middle of one of those would tangle it.

Then, before staging anything, list the commits that are not pushed, oldest
first:

```bash
git log --format='%h %s' --reverse HEAD --not --remotes
```

If it lists any, see which can be taken back. A /save commit, which touches
nothing but a pass's files (defined below), is never taken back, so only the
commits listed after the last /save commit can be, or all of them when none
is /save's. When the last commit listed is a /save commit, none can be: say
so and go on. Otherwise ask before going on, with AskUserQuestion, naming
each listed commit by hash and subject and marking /save's. The choices:
leave them as they are and commit only the working tree; take back every
commit that can be, so this run reviews their changes and commits them
again; or stop, so the user can push first and run again. Say in the
question that to take back only some, the user chooses Other and types the
hash of the last commit to keep: it and every commit listed before it stay
as they are, and those listed after it are taken back. When a /save commit
is listed, the hash typed must be that of the last /save commit or of one
listed after it.

Taking back is `git reset --soft <the last commit kept, or the pushed tip
when none is kept>`. It leaves every change of those commits staged and
nothing else, and it is the one rewrite this skill makes: of unpushed
commits only, and only on the user's answer. Note the hash the branch
stood at first, since a soft reset to it restores those commits. Once any
are taken back, every later stop gives `git reset --soft <that hash>` as
the way to restore them, and the report gives the hash in place of
`HEAD~<n>`.

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

Stop and say why if nothing is staged. When a pass's files are all that
changed, say that /save commits them.

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

## 7. After the report

The run ends with the report. Anything the user asks for next, in this
thread or another, is development work, not part of the run: make the
change and commit none of it, leaving it in the working tree for the next
run to review and commit, or for /save when it is a pass's files. This
skill writes no version commit to mark where a run ended, so a commit made
now could not be told from the run's own, and the next run could not know
it was never reviewed. The next batch gets its own `/commit`, which the user
starts in a new thread.
