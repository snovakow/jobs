---
name: diffcheck
description: The DIFF CHECK that ends Step 2B of the job search playbook. Diffs the link-checked run/03-results.txt against the sweep's committed copy, in a fresh context at Max effort, and rebuilds the file when the link check changed more than its block says. /linkcheck runs it; run it again to recheck.
context: fork
model: opus
effort: max
background: false
---

Run the check below exactly as written. Your last message is everything it
printed, from the first CLOSED or MOVED line through the verdict, in full.

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "DIFF CHECK"`
