# jobs

A job search run as a playbook of prompts, with Claude Code as home base.

- `RUNBOOK.md` is the person's instructions for a pass. `root/00-playbook.txt`
  is what the commands run from: each step's prompt, the appendix templates
  Step 1 copies, the rules and definitions the steps act on, and the reasons
  behind them. Each step is a command in `.claude/skills/` that reads its
  prompt from the playbook when it runs, through `.claude/scripts/prompt.py`.
  A prompt changes in the playbook, never in a command.
- `root/ledger.csv` only grows. Triage appends rows and never rewrites one.
  Outside triage, change only the field asked for: a status in Step 5, or a
  tier in its tier check. Every field double-quoted, LF line endings.
- When I give a Step 5 decision, set that row's status as STATUS VALUES in
  the playbook defines it, and change nothing else in the row.
- The playbook is plain text within 79 columns, and so is every file a step
  writes, apart from its table rows and the ledger.
- The repository is public: nothing private goes in a file or a commit
  message. `/commit` reviews the changes and commits them; nothing is
  pushed.
