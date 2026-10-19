---
name: advice
description: Step 5 of the job search playbook. In the triage conversation, gives application advice at Max effort for roles triage ranked below Tier 1.
argument-hint: "<company and role, for each>"
disable-model-invocation: true
effort: max
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
---

# Advice

Step 5's advice request in `root/00-playbook.txt`. It belongs in the
conversation that ran `/triage`: if this conversation didn't, stop and tell
me to go back to that one. If no roles follow the command, ask me which.

Answer this message, with the roles listed under it:

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "STEP 5"`

$ARGUMENTS
