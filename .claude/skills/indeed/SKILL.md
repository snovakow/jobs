---
name: indeed
description: Step 3B of the job search playbook. Checks that Indeed is signed out, then runs root/02-indeed.txt on Indeed in Chrome; /capture follows it in the same conversation.
disable-model-invocation: true
model: opus
---

# Indeed

Step 3B of `root/00-playbook.txt`, run in my Chrome through the Claude in
Chrome tools, at the session's effort: xhigh effort, or Max effort for the
Maximum setting.

1. This step runs in a conversation of its own. If this conversation
   already holds another step's work, stop and tell me to start a new one.
2. If the Claude in Chrome tools can't be loaded or don't connect, stop and
   tell me to enter @browser and run `/indeed` again.
3. Before any search, open https://ca.indeed.com/ and read the page header.
   Go ahead only when it shows a "Sign in" link, which is what Indeed shows
   a signed-out visitor. If it shows an account or profile menu, or you
   can't tell for certain, stop and ask me to sign out, and check again
   when I enter Continue. Never sign in or out yourself.
4. Run the prompt below exactly as written, in Chrome.
5. When the run stops, tell me to run `/capture` here.

## The prompt

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" --file root/02-indeed.txt`
