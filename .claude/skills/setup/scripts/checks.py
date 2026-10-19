#!/usr/bin/env python3
"""The counts Step 1 reads, printed for /setup to act on.

    checks.py sweeps   each segment's rows in the sweep's last two files,
                       the segments thin in both, and the closing notes
                       each file ends with

A sweep's file is a committed copy of run/03-results.txt that does not end
with a LINK CHECK block: Step 2 commits it before the link check edits it.
It only reads; it changes nothing.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RESULTS = "run/03-results.txt"
# In the order the sweep runs them.
SEGMENTS = ("seg1", "seg3", "seg2", "seg4")
# A segment with this many rows or fewer in both files is thin.
THIN = 3


def git(*args):
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return done.stdout if done.returncode == 0 else None


def note(name, text):
    parts = textwrap.wrap(text, 66)
    for n, part in enumerate(parts):
        print(f"  {name if n == 0 else '':<10} {part}")


def ends_with_link_check(text):
    lines = [l for l in text.split("\n") if l.strip()]
    for n in range(len(lines) - 1, -1, -1):
        if lines[n] in ("LINK CHECK: NONE", "LINK CHECK:"):
            rest = lines[n + 1:]
            if lines[n] == "LINK CHECK: NONE":
                return not rest
            return bool(rest) and all(l.startswith(("CLOSED: ", "MOVED: "))
                                      for l in rest)
    return False


def segments_of(line):
    """The segments a table row names, or None for any other line."""
    fields = line.split(" | ")
    codes = fields[0].split()
    if len(fields) < 9 or not codes or not set(codes) <= set(SEGMENTS):
        return None
    return set(codes)


def listed(items):
    """Names joined for prose: a, b and c."""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def sweep_files():
    """The last two sweep files, earliest first, as (date, commit, text)."""
    found = []
    log = git("log", "--date=short", "--format=%h %ad", "--", RESULTS) or b""
    for entry in log.decode().split("\n"):
        if not entry.strip():
            continue
        commit, date = entry.split()
        data = git("show", f"{commit}:{RESULTS}")
        if data is None:
            continue
        text = data.decode("utf-8", "replace")
        if not ends_with_link_check(text):
            found.append((date, commit, text))
        if len(found) == 2:
            break
    return found[::-1]


def sweeps():
    print("SWEEPS")
    files = sweep_files()
    counts, notes = [], []
    for _, _, text in files:
        lines = text.split("\n")
        rows = [n for n, l in enumerate(lines) if segments_of(l)]
        count = dict.fromkeys(SEGMENTS, 0)
        for n in rows:
            for code in segments_of(lines[n]):
                count[code] += 1
        counts.append(count)
        notes.append("\n".join(lines[rows[-1] + 1:]).strip() if rows else "")
    print(f"  {'Segment':<10}" + "".join(f"{d:>12}" for d, _, _ in files))
    thin = []
    for code in SEGMENTS:
        if len(counts) == 2 and all(c[code] <= THIN for c in counts):
            thin.append(code)
        print((f"  {code:<10}" + "".join(f"{c[code]:>12}" for c in counts) +
               ("   thin" if code in thin else "")).rstrip())
    if len(files) < 2:
        note("Thin", f"none: it takes two sweep files in git, and there "
             f"{'is' if len(files) == 1 else 'are'} {len(files)}")
    else:
        note("Thin", f"{listed(thin)}: three rows or fewer in both"
             if thin else "none")
    note("From", "Each column is the sweep's file committed that day, before "
         "its link check. A row two segments found counts under each.")
    if git("status", "--porcelain", "--", RESULTS):
        note("Note", f"{RESULTS} has uncommitted changes, so a sweep it "
             "holds counts nothing until it is committed.")
    for (date, commit, _), text in zip(files, notes):
        print()
        print(f"CLOSING NOTES — the sweep's file committed {date} ({commit})")
        # Research may leave a paragraph on one line; only those get wrapped.
        for line in (text or "(none)").split("\n"):
            body = line.lstrip()
            hang = line[:len(line) - len(body)]
            hang += "  " if body.startswith("- ") else ""
            print("\n".join(textwrap.wrap(line, 79, subsequent_indent=hang)))


if __name__ == "__main__":
    modes = {"sweeps": sweeps}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    modes[sys.argv[1]]()
