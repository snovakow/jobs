---
name: triage
description: Step 4 of the job search playbook. Checks this pass's inputs, ranks the results against the resume and the ledger, writes run/05-triage.txt, appends new rows to root/ledger.csv, and ends with a CHECKS block.
disable-model-invocation: true
effort: max
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
  - Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/checks.py" *)
---

# Triage

Step 4 of `root/00-playbook.txt`. The session's model runs it: Opus, or Fable
for the Maximum setting.

1. This step runs in a conversation of its own. If this conversation
   already holds another step's work, stop and tell me to start a new one.
   If you are neither Opus nor Fable, stop and tell me to enter
   `/model opus`, or `/model fable` for the Maximum setting, and run
   `/triage` again.
2. Run the prompt below exactly as written. The INPUTS and SOURCES blocks
   it refers to follow it, from the checks program.
3. When the files are written, run the ledger check, and end your reply with
   the CHECKS block as the prompt says:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/checks.py" ledger
   ```

## The prompt

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "STEP 4"`

## INPUTS

!`python3 "${CLAUDE_SKILL_DIR}/scripts/checks.py" inputs`

## SOURCES

!`python3 "${CLAUDE_SKILL_DIR}/scripts/checks.py" sources`
