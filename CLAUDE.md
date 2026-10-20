# jobs

A job search run as a playbook of prompts, with Claude Code as home base.

- `RUNBOOK.md` is the person's instructions for a pass: what to do, where
  and at what setting, and never why. `root/00-playbook.txt` is what the
  commands run from: each step's prompt, the appendix templates Step 1
  copies, the rules and definitions the steps act on, and the reasons
  behind them and behind RUNBOOK.md's instructions. Each step is a command
  in `.claude/skills/` that reads its prompt when it runs, through
  `.claude/scripts/prompt.py`: from the playbook, or for the LinkedIn and
  Indeed runs, from the 02-* file Step 1 built from it. A prompt changes in
  the playbook, never in a command.
- `root/ledger.csv` only grows. Triage appends rows, and never rewrites a
  row it did not add this pass. Outside triage, append only the rows Step
  5's ANOTHER ROLE WORTH PURSUING describes, and in an existing row change
  only the field asked for: a status in Step 5, a tier in its tier check, or
  the notes a RUNBOOK.md fix names. Every field double-quoted, LF line
  endings.
- When I give a Step 5 decision, set that row's status as STATUS VALUES in
  the playbook defines it, and change nothing else in the row.
- The playbook and every file a step writes are plain text. Only
  run/05-triage.txt, which I read, wraps at 79 columns; the rest take lines
  of any length, so an edit never rewraps a paragraph. Table rows, ledger
  rows and the entries of a LINK CHECK or CAPTURE CHECK block stay one line
  each, however long, and run/03-results.txt keeps the lines Research
  wrote. The playbook's 79-dash rules mark where each prompt starts and
  ends.
- The repository is public: nothing private goes in a file or a commit
  message. `/save` commits a pass's files, and `/commit` commits every
  other change once the `changecheck` skill has reviewed it; nothing is
  pushed. `/verify` is Step 1B's check of the files setup writes, never a
  check to run before a commit.
