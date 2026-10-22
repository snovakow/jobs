#!/usr/bin/env python3
"""The counts /sweep reports, printed for it to act on.

    checks.py file   whether the moved file can be checked; its rows by
                     segment and by token beside the last pass's sweep;
                     what its COVERAGE block says the run did not reach;
                     the warning signs a count can find; and the next step

The moved file is run/03-results.txt as it stands. Which committed copy is
the last pass's sweep is in .claude/scripts/sweeps.py. It only reads; it
changes nothing.
"""

import sys
import textwrap
from pathlib import Path

# Import the shared module without writing a __pycache__ into the repository.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from sweeps import (KINDS, PROMPT, RESULTS, ROOT, SEGMENTS,  # noqa: E402
                    TOKENS, TRIAGE, counted, counts, coverage,
                    ends_with_link_check, git, missing, passes, round_of,
                    rows, runs, thin, tokens)

FORTY = 40


def line(name, text, verdict):
    parts = textwrap.wrap(text, 52)
    for n, part in enumerate(parts):
        label = name if n == 0 else ""
        end = f" {verdict}" if n == len(parts) - 1 else ""
        print(f"  {label:<10} {part:<52}{end}".rstrip())


def note(name, text):
    parts = textwrap.wrap(text, 66)
    for n, part in enumerate(parts):
        print(f"  {name if n == 0 else '':<10} {part}")


def plural(n, word, many=None):
    return f"{n} {word}" if n == 1 else f"{n} {many or word + 's'}"


def tally(text):
    """Rows by segment and by token, with the rows carrying no token."""
    found = rows(text)
    by_token = dict.fromkeys(TOKENS, 0)
    bare = []
    for fields in found:
        marks = tokens(fields)
        for mark in set(marks):
            by_token[mark] += 1
        if not marks:
            bare.append(f"{fields[1]} - {fields[2]}")
    return counts(text), by_token, len(found), bare


def copied(text):
    """Rows identical to a row of the file the last pass left, the one the
    sweep's first message attaches: a write-out that took it for runs of
    this thread."""
    base = (git("log", "-1", "--format=%H", "--", TRIAGE) or b"").strip()
    old = git("show", f"{base.decode()}:{RESULTS}") if base else None
    if not old:
        return []
    before = {" | ".join(fields)
              for fields in rows(old.decode("utf-8", "replace"))}
    return [f"{fields[1]} - {fields[2]}" for fields in rows(text)
            if " | ".join(fields) in before]


def checked(text):
    """Print the FILE lines; False when the file can't be checked."""
    print("FILE")
    last = git("show", f"HEAD:{RESULTS}")
    same = last is not None and last.decode("utf-8", "replace") == text
    # The header names the segment first, written short or as the template's
    # column list, and has the table's nine columns.
    cells = text.split("\n", 1)[0].split(" | ")
    header = len(cells) >= 9 and cells[0].startswith("Segment")
    results = (
        ("Moved", "differs from its last commit" if not same
         else "the same as its last commit: nothing new was moved in",
         not same),
        ("Header", "starts with the sweep's table header" if header
         else "does not start with the sweep's table header", header),
        ("Ending", "ends with no LINK CHECK block"
         if not ends_with_link_check(text) else "ends with a LINK CHECK block",
         not ends_with_link_check(text)),
    )
    for name, words, passed in results:
        line(name, words, "ok" if passed else "stop")
    return all(passed for _, _, passed in results)


def main():
    file = ROOT / RESULTS
    if not file.is_file():
        print("FILE")
        line("Moved", f"there is no {RESULTS}", "stop")
        return
    text = file.read_text(encoding="utf-8", errors="replace")
    if not checked(text):
        return

    found = passes()
    last = next((entry for entry in found or [] if entry[3]), None)
    segs, by_token, total, bare = tally(text)
    if last:
        old_segs, old_tokens, old_total, old_bare = tally(last[2])
    print("ROWS")
    print(f"  {'Segment':<10} {'This file':>9} {'Last pass':>10}")
    for code in SEGMENTS:
        print(f"  {code:<10} {segs[code]:>9} "
              f"{old_segs[code] if last else '-':>10}")
    print(f"  {'All rows':<10} {total:>9} {old_total if last else '-':>10}")
    for mark in TOKENS:
        print(f"  {mark:<10} {by_token[mark]:>9} "
              f"{old_tokens[mark] if last else '-':>10}")
    print(f"  {'No token':<10} {len(bare):>9} "
          f"{len(old_bare) if last else '-':>10}")
    if found is None:
        source = (f"no last pass: {PROMPT} has uncommitted changes, so no "
                  "earlier sweep counts until it is committed.")
    elif last:
        source = (f"the last pass's sweep is its file committed {last[0]} "
                  f"({last[1]}), before its link check.")
    else:
        source = ("no last pass to compare: no triaged pass has a sweep "
                  f"among the {counted()}.")
    note("From", source[0].upper() + source[1:] + " A row two segments found "
         "counts under each, and a row with two tokens under both.")

    cover = coverage(text)
    print("COVERAGE")
    not_reached = 0
    if cover is None:
        line("Block", "the file has no COVERAGE block", "missing")
    else:
        for code in SEGMENTS:
            parts = []
            for kind in KINDS:
                names = cover[code].get(kind)
                parts.append(f"{kind}: no line" if names is None
                             else f"{kind}: {len(names)}")
            note(code, ", ".join(parts))
            not_reached += len(cover[code].get(KINDS[0]) or [])
    done = runs(text)
    note("Runs", f"{done}: the closing notes come from "
         f"{'one research run' if done == 1 else f'{done} research runs'}")

    print("SIGNS")
    gaps = missing(cover) if cover is not None else []
    many = [f"{code}: {segs[code]} rows" for code in SEGMENTS
            if segs[code] >= FORTY]
    relocate, ok = by_token["RELOCATE"], by_token["OK"]
    # This file is the newest pass of a round, ahead of the triaged ones.
    history = [text] + [entry[2] for entry in found or [] if entry[3]]
    marked = thin(history)
    carried = copied(text)
    signs = (
        ("Rows copied from the last pass's file",
         f"{len(carried)}: " + "; ".join(carried) if carried else "none"),
        ("A row with no status token",
         "; ".join(bare) if bare else "none"),
        ("Forty rows in one segment", "; ".join(many) if many else "none"),
        ("More RELOCATE rows than OK rows, on six rows or more",
         ("yes" if total >= 6 and relocate > ok else "no") +
         f": {relocate} RELOCATE, {ok} OK, {plural(total, 'row')}"),
        ("A segment with three rows or fewer through a full round of its "
         "targets",
         ", ".join(f"{code} (a round of {round_of(history, code)} passes)"
                   for code in marked) if marked else "none"),
        ("No COVERAGE block, or one with lines missing",
         "no block" if cover is None else
         ("lines missing: " + "; ".join(gaps) if gaps else "no")),
    )
    for name, finding in signs:
        note("", f"{name}: {finding}")

    print("NEXT")
    left = plural(not_reached, "target company", "target companies")
    if carried:
        note("Next", "have the file written again without the last pass's "
             "rows, as that sign's fix says, then enter /sweep again. Until "
             "then the counts above include those rows, and Runs counts any "
             "of the last pass's notes it copied as runs.")
    elif cover is None or gaps:
        note("Next", "fix the COVERAGE block first, as its warning sign "
             "says, then enter /sweep again.")
    elif not_reached and done == 1:
        note("Next", f"continue the sweep, Step 2 item 4: {left} not "
             "reached in this pass's one run. Then enter /sweep again.")
    else:
        rest = (f" The next pass's sweep starts with the {left} still not "
                "reached." if not_reached else "")
        note("Next", "/save, then Step 2B." + rest)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] != "file":
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    main()
