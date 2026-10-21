---
name: changecheck
description: The review /commit runs before it commits. Checks the staged change to the playbook, RUNBOOK.md, CLAUDE.md or a command against the rest of the system, in a fresh context at Max effort, and changes nothing. Only /commit runs it.
user-invocable: false
context: fork
model: opus
effort: max
background: false
allowed-tools:
  - Bash(git diff *)
  - Bash(git show *)
  - Bash(git log *)
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
disallowed-tools: Edit, Write, NotebookEdit
---

# Change check

The review `/commit` runs before it commits: a fresh read of what it has
staged, by a model that did not make the change. `/save` commits a pass's
own files, so everything staged here changes what steers every pass. It
fixes nothing: change no file. Your last message is its REPORT, in full.

The change is what `git diff --cached` shows, and `git diff --cached --stat`
lists its files. If nothing is staged, say so and stop. Read the whole
change, then read, as they now stand, the files it touches and the files
that name what it touches: `root/00-playbook.txt`, RUNBOOK.md, CLAUDE.md,
and the commands under `.claude/skills/` with their scripts. README.md is
`/commit`'s to keep true after this check; read it only for check 7.

Judge the change. A problem it did not cause, which `git show HEAD:<path>`
shows was already there, is reported under its check as already there, and
does not fail it.

1. **Commands.** Every command still finds what it runs from. Run
   `python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py"` with each label
   and each `--file` path that a command under `.claude/skills/` passes it,
   and check that every script, file and skill a command names exists.
2. **Playbook, commands and scripts.** What a changed command or script
   does matches what the playbook's steps, rules and definitions say it
   does, and what a changed playbook passage says a command or script does,
   it does.
3. **RUNBOOK.md.** Each step's items, commands, files, order, threads,
   model and effort match what the commands and the playbook do. An
   instruction names its thread where that matters, and its model and
   effort where they differ from its step's table. RUNBOOK.md holds
   instructions only; their reasons are in the playbook.
4. **Nothing left behind.** Anything the change renames, removes or moves,
   such as a section, file, command, field, status, token or setting, has
   changed everywhere it is named, scripts included. Search for the old
   name.
5. **No contradictions.** No rule the change adds or alters contradicts
   another, in the playbook, CLAUDE.md, a command or a script.
6. **Settings.** Each command's model and effort, set in its frontmatter or
   checked in its text, match MODEL AND EFFORT in the playbook and the
   step's table in RUNBOOK.md.
7. **Public.** The repository is public. Nothing in the change is a
   credential, or an employer, posting, pay or fit judgement from a pass,
   outside `run/` and the ledger.

Print the REPORT in this form:

    CHANGE CHECK REPORT
    1. Commands: PASS
       <evidence>
    2. Playbook, commands and scripts: FAIL
       <evidence>
    ...
    CHANGE CHECK: FAIL — 1 problem

Under a PASS, the evidence is what you compared; for check 1, every label
and path you ran, and every script, file and skill you found. Under a FAIL,
it is each problem: its file and line, what it says, and what it
contradicts or leaves behind. The last line is `CHANGE CHECK: PASS`, or
`CHANGE CHECK: FAIL — ` and the number of problems.
