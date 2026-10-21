---
name: sweep
description: Step 2 of the job search playbook. Checks the sweep's file once you have moved it into run/03-results.txt — its rows beside the last pass's sweep, what its COVERAGE block says the run did not reach, and any warning signs — and says whether to continue the sweep. Reads only; moves and changes no file.
disable-model-invocation: true
context: fork
model: sonnet
effort: medium
background: false
allowed-tools:
  - Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/checks.py" *)
disallowed-tools: Edit, Write, NotebookEdit
---

# Sweep

Step 2 runs in Advanced Research on claude.ai, with the messages RUNBOOK.md
gives. You download the file it writes and move it into the repository
yourself, replacing `run/03-results.txt`. This command checks that moved
version. Its program has already run, below: it counted the file, and the
last pass's sweep from git. It only reads: it never moves, renames, deletes
or edits a file, in the repository or anywhere else. Your last message is
its report, in full.

1. If a FILE line below says stop, say "/sweep won't check the file", say
   which check failed, and stop.
2. Report the ROWS lines, the moved version beside the last pass's sweep,
   and the COVERAGE lines, as printed. Take every count from them, and
   count nothing yourself.
3. Read `run/03-results.txt` for the warning signs a count can't find, as
   WHAT BAD LOOKS LIKE in Step 2 of `root/00-playbook.txt` describes them:
   US locations marked OK; a posting named in the closing notes with no row;
   and iOS roles with no video, 3D or visualization in the product, or cloud
   full-stack roles. Then report each warning sign you or the SIGNS lines
   found, in these words:
   - A row with no status token
   - US locations marked OK, or forty rows in one segment
   - A posting named in the closing notes with no row
   - More RELOCATE rows than OK rows, on six rows or more
   - iOS roles with no video, 3D or visualization in the product, or
     cloud full-stack roles
   - A segment with three rows or fewer through a full round of its
     targets
   - No COVERAGE block, or one with lines missing

   If there are none, say "No warning signs."
4. Give the fix RUNBOOK.md's warning-sign table gives for each sign you
   reported. When a fix runs the sweep again or has the file written again,
   that is the next step. Otherwise the next step is what the Next line
   says, and a fix that only changes later passes goes with it.

## Checks

!`python3 "${CLAUDE_SKILL_DIR}/scripts/checks.py" file`
