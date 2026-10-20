---
name: save
description: Commits a pass's files — run/, the ledger, Step 1's positioning read and search prompts, and the resume — after the commit review's checks, under a short message built from what changed. Leaves every other change for /commit, and never pushes.
disable-model-invocation: true
context: fork
model: haiku
effort: low
background: false
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/save.py" *)
disallowed-tools: Edit, Write, NotebookEdit
---

# Save

The cheap commit for a pass. Its program has already run, below. It took
the files a pass writes — `run/`, `root/ledger.csv`,
`root/01-positioning.txt`, the `root/02-*` prompt files and
`root/resume.pdf` — ran the commit review's checks on them, and committed
them if the review flagged nothing. Every other change, such as to the
playbook, RUNBOOK.md or a command, is /commit's, and it was left as it was.

Give me its result in a line or two: what it saved, or why it saved
nothing, and anything it left for /commit. When the review flagged
anything, show its lines after that, in full and as printed. Do nothing
else. Run no other check, /verify included, and stage, commit, edit or push
nothing yourself.

## Result

!`python3 "${CLAUDE_SKILL_DIR}/scripts/save.py" save`
