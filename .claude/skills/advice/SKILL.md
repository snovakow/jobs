---
name: advice
description: Step 5 of the job search playbook. In the triage thread, reads each posting in Chrome and gives application advice at Max effort for roles triage ranked below Tier 1.
argument-hint: "<company and role, for each>"
disable-model-invocation: true
effort: max
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
---

# Advice

Step 5's advice request in `root/00-playbook.txt`. It belongs in the
thread that ran `/triage`: if this thread didn't, stop and tell
me to go back to that one. It runs on Opus, or Fable for the Maximum
setting: if you are neither, stop and tell me to enter `/model opus`, or
`/model fable`, and run `/advice` again. If no roles follow the command,
ask me which. It reads each posting in Chrome: if the Claude in Chrome
tools can't be loaded, don't connect or fail partway, stop and tell me to
enter @browser and run `/advice` again.

Answer this message, with the roles listed under it:

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "STEP 5"`

$ARGUMENTS
