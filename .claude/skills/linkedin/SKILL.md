---
name: linkedin
description: Step 3 of the job search playbook. Runs root/02-linkedin.txt through LinkedIn's AI job search in Chrome; /capture follows it in the same conversation.
disable-model-invocation: true
model: opus
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
---

# LinkedIn

Step 3 of `root/00-playbook.txt`, run in my Chrome through the Claude in
Chrome tools, where I'm logged in to LinkedIn, at the session's effort:
xhigh effort, or Max effort for the Maximum setting.

1. This step runs in a conversation of its own. If this conversation
   already holds another step's work, stop and tell me to start a new one.
2. This session's effort is ${CLAUDE_EFFORT}. Below xhigh a run opens
   fewer pages than its prompt calls for, so if that is low, medium or
   high, stop and tell me to enter `/effort xhigh`, or `/effort max` for
   the Maximum setting, and run `/linkedin` again.
3. If the Claude in Chrome tools can't be loaded or don't connect, stop and
   tell me to enter @browser and run `/linkedin` again.
4. Run the prompt below exactly as written, in Chrome. If LinkedIn shows a
   sign-in page, stop and ask me to log in, and carry on when I enter
   Continue.
5. When the run stops, tell me to run `/capture` here.

## The prompt

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" --file root/02-linkedin.txt`
