---
name: verify
description: Step 1B of the job search playbook. Checks the files a setup run wrote into root/ against its checklist, in a fresh context at Max effort, and changes nothing. /setup runs it; run it again to recheck the files.
context: fork
model: opus
effort: max
background: false
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
disallowed-tools: Edit, Write, NotebookEdit
---

Run the check below exactly as written. It fixes nothing: change no file.
Your last message is its REPORT, in full.

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "STEP 1B"`
