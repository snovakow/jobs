---
name: sweep
description: Step 2 of the job search playbook. Checks the sweep's file once you have moved it into run/03-results.txt, compares it with the copy last committed, and reports its rows and any warning signs. Reads only; moves and changes no file.
disable-model-invocation: true
context: fork
model: sonnet
effort: medium
background: false
disallowed-tools: Edit, Write, NotebookEdit
---

# Sweep

Step 2 runs in Advanced Research on claude.ai, with the two messages
RUNBOOK.md gives. You download the file it writes and move it into the
repository yourself, replacing `run/03-results.txt`. This command checks
that moved version against the repository version, the copy last committed,
which is the last pass's. It only reads: it never moves, renames, deletes or
edits a file, in the repository or anywhere else.

1. Read the moved version, `run/03-results.txt` as it stands, and the
   repository version, `git show HEAD:run/03-results.txt`. The moved
   version must differ from the repository version, its first line must be
   the sweep's table header, which starts `Segment |`, and it must not end
   with a LINK CHECK block. If any of these fails, say "/sweep won't check
   the file", say which check failed, and stop.
2. Report the rows per segment and per status token, for the moved version
   beside the repository version. Then check the moved version against
   WHAT BAD LOOKS LIKE in Step 2 of `root/00-playbook.txt`, and report each
   warning sign you find, in these words:
   - A row with no status token
   - US locations marked OK, or forty rows in one segment
   - A posting named in the closing notes with no row
   - More RELOCATE rows than OK rows, on six rows or more
   - iOS roles with no video, 3D or visualization in the product, or
     cloud full-stack roles
   - A segment with three rows or fewer, two passes running: three rows or
     fewer in both the moved version and the repository version

   If there are none, say "No warning signs."
3. The next step is `/save`, then Step 2B.
