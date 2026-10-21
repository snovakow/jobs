#!/usr/bin/env python3
"""The counts Step 1 reads, printed for /setup to act on.

    checks.py sweeps   each segment's rows in the sweep's file from each
                       pass, and the target companies each file's COVERAGE
                       block lists as not reached; each segment's last full
                       round, and the segments thin or short; and the
                       closing notes each file ends with

Which committed copies count, and as which pass, is in
.claude/scripts/sweeps.py. It only reads; it changes nothing.
"""

import sys
import textwrap
from pathlib import Path

# Import the shared module without writing a __pycache__ into the repository.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from sweeps import (KINDS, PROMPT, RESULTS, SEGMENTS,  # noqa: E402
                    counted, counts, coverage, git, passes, round_of, rows,
                    short, thin)

# How many passes the table shows, the latest ones.
SHOWN = 6


def note(name, text):
    parts = textwrap.wrap(text, 66)
    for n, part in enumerate(parts):
        print(f"  {name if n == 0 else '':<10} {part}")


def listed(items):
    """Names joined for prose: a, b and c."""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def notes_of(text):
    """Everything the file holds after its table's last row."""
    lines = text.split("\n")
    ends = [n for n, line in enumerate(lines) if rows(line)]
    return "\n".join(lines[ends[-1] + 1:]).strip() if ends else ""


def unreached(cover, code):
    """How many target companies the segment's COVERAGE line lists as not
    reached, or - when the file has no such line."""
    if cover is None or KINDS[0] not in cover[code]:
        return "-"
    return len(cover[code][KINDS[0]])


def sweeps():
    print("SWEEPS")
    found = passes()
    if found is None:
        note("Note", f"{PROMPT} has uncommitted changes, so no sweep counts "
             "until it is committed.")
        return
    texts = [text for _, _, text, _ in found]
    marked, waiting = thin(texts), short(texts)
    shown = found[:SHOWN][::-1]
    print(f"  {'Segment':<10}" + "".join(f"{d:>12}" for d, _, _, _ in shown)
          + f"{'Round':>10}")
    for code in SEGMENTS:
        cells = "".join(f"{counts(t)[code]}/{unreached(coverage(t), code)}"
                        .rjust(12) for _, _, t, _ in shown)
        size = round_of(texts, code)
        mark = "   thin" if code in marked else "   short" if code in waiting \
            else ""
        print(f"  {code:<10}{cells}"
              f"{f'{size} passes' if size else 'open':>10}{mark}".rstrip())
    if len(found) < 2:
        note("Thin", f"none: it takes the sweep's files from two {counted()}, "
             f"and there {'is' if len(found) == 1 else 'are'} {len(found)}")
    else:
        note("Thin", f"{listed(marked)}: three rows or fewer in every pass of "
             f"{'its' if len(marked) == 1 else 'their'} last full round"
             if marked else "none")
    if waiting:
        note("Short", f"{listed(waiting)}: three rows or fewer in the last two "
             "passes, but its round is open, so not thin: the next sweep "
             "starts with the target companies left")
    note("From", "Each column is one pass's sweep, its file as committed "
         "before its link check, a pass ending when its triage is committed: "
         "rows, then the target companies its COVERAGE block lists as not "
         f"reached, - where it has no such line. It counts only {counted()}. A "
         "segment's round is the fewest latest passes, two at least, that "
         "between them reached every target company in its list; open means "
         "they have not yet. A row two segments found counts under each.")
    if git("status", "--porcelain", "--", RESULTS):
        note("Note", f"{RESULTS} has uncommitted changes, so a sweep it "
             "holds counts nothing until it is committed.")
    keep = max([round_of(texts, code) for code in marked] + [2])
    for (date, commit, text, _) in found[:keep][::-1]:
        print()
        print(f"CLOSING NOTES — the sweep's file committed {date} ({commit})")
        # Research may leave a paragraph on one line; only those get wrapped.
        for line in (notes_of(text) or "(none)").split("\n"):
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
