---
name: indeed
description: Step 3B of the job search playbook. Checks that Indeed is signed out, then runs root/02-indeed.txt on Indeed in Chrome; /capture follows it in the same thread.
disable-model-invocation: true
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
---

# Indeed

Step 3B of `root/00-playbook.txt`, run in my Chrome through the Claude in
Chrome tools, on Opus at the session's effort: xhigh effort, or Max effort
for the Maximum setting.

1. This step runs in a thread of its own. If this thread
   already holds another step's work, stop and tell me to start a new one.
2. This session's model and effort run the whole step: this turn, and
   every reply I send after it, such as Continue or Re-run. If you are not
   Opus, stop and tell me to enter `/model opus` and run `/indeed`
   again. The effort is ${CLAUDE_EFFORT}. Below xhigh a run opens fewer
   pages than its prompt calls for, so if that is low, medium or high,
   stop and tell me to enter `/effort xhigh`, or `/effort max` for the
   Maximum setting, and run `/indeed` again.
3. If the Claude in Chrome tools can't be loaded or don't connect, stop and
   tell me to enter @browser and run `/indeed` again.
4. Before any search, open https://ca.indeed.com/ and read the page header.
   Go ahead only when it shows a "Sign in" link, which is what Indeed shows
   a signed-out visitor. If it shows an account or profile menu, or you
   can't tell for certain, stop and ask me to sign out, and check again
   when I enter Continue. Never sign in or out yourself.
5. Run the prompt below exactly as written, in Chrome.
6. When the run stops, tell me to run `/capture` here.

## The prompt

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" --file root/02-indeed.txt`
