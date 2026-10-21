---
name: linkcheck
description: Step 2B of the job search playbook. Opens every row of run/03-results.txt in Chrome, cuts the closed postings from the file in place, then runs /diffcheck on the result.
disable-model-invocation: true
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
---

# Link check

Step 2B of `root/00-playbook.txt`, run in my Chrome through the Claude in
Chrome tools, on Opus at the thread's effort: xhigh effort, or Max effort
for the Maximum setting.

1. This step runs in a thread of its own. If this thread
   already holds another step's work, stop and tell me to start a new one.
2. This thread's model and effort run the whole step: this turn, and
   every reply I send after it, such as Continue. If you are not Opus, stop
   and tell me to enter `/model opus` and run `/linkcheck` again. The
   effort is ${CLAUDE_EFFORT}. Below xhigh a run opens fewer pages than its
   prompt calls for, so if that is low, medium or high, stop and tell me to
   enter `/effort xhigh`, or `/effort max` for the Maximum setting, and run
   `/linkcheck` again.
3. If the Claude in Chrome tools can't be loaded or don't connect, stop and
   tell me to enter @browser and run `/linkcheck` again.
4. Run the prompt below exactly as written, in Chrome.
5. Then run the `diffcheck` skill and read its verdict:
   - PASS or REBUILT: show me its verdict and counts lines, and any
     difference it found.
   - FAIL: fix what the verdict names in `run/03-results.txt`, the block or
     a line that names no row, with the pages you opened in mind. Then run
     `diffcheck` again. If it fails a second time, stop and show me both
     verdicts.
   - No DIFF CHECK line: run it again.

## The prompt

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "STEP 2B"`

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" --file run/03-results.txt`
