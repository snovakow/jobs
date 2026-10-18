---
name: capture
description: The CAPTURE CHECK that ends Steps 3 and 3B of the job search playbook. Checks a LinkedIn or Indeed run's capture at Max effort, then writes the run's file into run/.
disable-model-invocation: true
model: opus
effort: max
---

# Capture check

The CAPTURE CHECK of `root/00-playbook.txt`. It runs in the conversation of
the LinkedIn or Indeed run it checks: if this conversation holds no
`/linkedin` or `/indeed` run, stop and say so.

Run the check below exactly as written. On a FAIL, when I reply Re-run, run
the re-run message you printed; when that run stops, I run `/capture` again.

## The check

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "CAPTURE CHECK"`
