---
name: sweep
description: Step 2 of the job search playbook. Moves the sweep's 03-results.txt download from ~/Downloads into run/03-results.txt, then reports its rows and any warning signs.
disable-model-invocation: true
---

# Sweep

Step 2 runs in Advanced Research on claude.ai, with the two messages
RUNBOOK.md gives. This command takes its downloaded file into the
repository. In `~/Downloads` it moves that one file and touches nothing else.

1. If `run/03-results.txt` has uncommitted changes, stop and say so: taking
   a download in would overwrite them.
2. Find the newest `03-results*.txt` in `~/Downloads` modified after the
   last commit of `run/03-results.txt`
   (`git log -1 --format=%ct -- run/03-results.txt`). If there is none, stop
   and say no new download is waiting.
3. Its first line must be the sweep's table header, which starts
   `Segment |`, and it must not end with a LINK CHECK block. If either
   fails, say "/sweep won't take the file in", say which check failed, and
   move nothing.
4. Move it to `run/03-results.txt`.
5. Report the rows per segment and per status token. Then check the file
   against WHAT BAD LOOKS LIKE in Step 2 of `root/00-playbook.txt`, and
   report each warning sign you find, in these words:
   - A row with no status token
   - US locations marked OK, or forty rows in one segment
   - A posting named in the closing notes with no row
   - More RELOCATE rows than OK rows, on six rows or more
   - Senior iOS or cloud full-stack roles
   - A segment with three rows or fewer, two passes running: compare each
     segment's count with the last pass's copy,
     `git show HEAD:run/03-results.txt`

   If there are none, say "No warning signs."
6. The next step is `/commit`, then Step 2B.
