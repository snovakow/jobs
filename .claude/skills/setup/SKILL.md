---
name: setup
description: Step 1 of the job search playbook. Reads the resume and the playbook, writes the positioning read and the three 02-* search prompts into root/, then checks them with /verify.
disable-model-invocation: true
effort: max
allowed-tools:
  - WebSearch
  - WebFetch
  - Bash(python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" *)
---

# Setup

Step 1 of `root/00-playbook.txt`. The session's model runs it: Opus, or
Fable for the Maximum setting.

1. This step runs in a conversation of its own. If this conversation
   already holds another step's work, stop and tell me to start a new one.
2. Run `git status --short -- root/ledger.csv`. If it lists the file, stop
   before anything else: the ledger has uncommitted changes, which Step 1B
   could not tell apart from ones this run made. Ask me to commit them.
3. Run the prompt below exactly as written.
4. When the files are written, run the `verify` skill and show me its
   REPORT. For each file that fails, rewrite that file here, where its
   reasoning is, and run `verify` again. A FAIL on `root/ledger.csv` means
   this run touched it: restore it with `git checkout -- root/ledger.csv`.
   If the same file fails twice, stop and show me both reports.
5. Once all five pass, say so.

## The prompt

!`python3 "${CLAUDE_SKILL_DIR}/../../scripts/prompt.py" "STEP 1"`
