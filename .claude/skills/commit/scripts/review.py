#!/usr/bin/env python3
"""Check the staged changes in the jobs repository before they are committed.

With no arguments, compares what is staged with HEAD. With two revisions,
compares the second commit with the first, which is how these checks can be
run against the repository's history. Prints one line per check and exits 1
when anything is flagged. It only reads from git; it changes nothing.

    review.py
    review.py BASE TARGET
"""

import collections
import csv
import fnmatch
import re
import subprocess
import sys

LEDGER = "root/ledger.csv"
RUNBOOK = "root/00-runbook.txt"
GUIDE = "00-runbook-quick-guide.txt"

HEADER = ["first_seen", "status", "company", "role", "source", "tier",
          "notes", "url"]
# Set when a row is appended and never changed after. Status, tier and
# notes are the fields a person edits.
FIXED = (0, 2, 3, 4, 7)
STATUSES = {"new", "applied", "rejected", "skipped"}
TIERS = {"1", "2", "3"}
QUOTED = re.compile(r'"(?:[^"]|"")*"(?:,"(?:[^"]|"")*")*')

RULE = "-" * 79
WIDTH = 79
DUPLICATE_DOWNLOAD = re.compile(r" \(\d+\)(\.[^./]+)?$")

# Which live prompt files each part of the runbook's appendix is copied into.
BUILT_FROM = {
    "sweep template": "root/02-segment-*.txt",
    "LinkedIn template": "root/02-linkedin-*.txt",
    "segment definitions": "root/02-*.txt",
}
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

flagged = []


def line(mark, name, text, details=()):
    print(f"{mark:<5} {name:<10} {text}")
    for detail in details:
        print(f"{'':17}{detail}")


def ok(name, text, details=()):
    line("ok", name, text, details)


def flag(name, text, details=()):
    flagged.append(name)
    line("FLAG", name, text, details)


def skip(name, text):
    line("--", name, text)


def git(*args):
    return subprocess.run(["git", *args], check=True,
                          capture_output=True).stdout


def blob(rev, path):
    """The file at a revision, "" meaning the index; None when absent."""
    spec = f":{path}" if rev == "" else f"{rev}:{path}"
    done = subprocess.run(["git", "show", spec], capture_output=True)
    return done.stdout if done.returncode == 0 else None


def changes(base, target):
    """(status, path) pairs; a rename counts as a deletion and an addition."""
    args = ["diff", "--name-status", "-z", "--no-renames"]
    args += ["--cached", base] if target == "" else [base, target]
    fields = git(*args).decode("utf-8").split("\0")
    return list(zip(fields[0::2], fields[1::2]))


def count(n, noun):
    return f"{n} {noun}" + ("" if n == 1 else "s")


def short(numbers, limit=6):
    shown = ", ".join(str(n) for n in numbers[:limit])
    return shown + (" and more" if len(numbers) > limit else "")


def check_strays(changed):
    strays = []
    for status, path in changed:
        name = path.rsplit("/", 1)[-1]
        if status == "D":
            continue
        if DUPLICATE_DOWNLOAD.search(name):
            strays.append(f"{path}: a duplicate download, so a stale copy")
        elif name == "ledger-seed.csv":
            strays.append(f"{path}: Step 1's seed, renamed once and then "
                          "deleted every run")
        elif name == "ledger.csv" and path != LEDGER:
            strays.append(f"{path}: a ledger copy; the ledger lives in "
                          "root/ only")
    if strays:
        flag("strays", f"{count(len(strays), 'file')} to leave out", strays)
    else:
        ok("strays", "none")


def rows_of(data):
    return list(csv.reader(data.decode("utf-8", "replace").splitlines()))


def fixed(row):
    return tuple(row[i] for i in FIXED)


def loose(text):
    return " ".join(re.sub(r"[^\w\s]", " ",
                           text.casefold().replace("-", " ")).split())


def check_ledger(base, target, touched):
    if LEDGER not in touched:
        return skip("ledger", "unchanged")
    new = blob(target, LEDGER)
    if new is None:
        return flag("ledger", f"{LEDGER} is deleted")

    problems = []
    carriage_returns = new.count(b"\r")
    if carriage_returns:
        problems.append(f"{count(carriage_returns, 'carriage return')}: "
                        "the ledger stays LF, or every line differs from the "
                        "last copy")
    if new and not new.endswith(b"\n"):
        problems.append("no newline at the end of the file")
    lines = new.decode("utf-8", "replace").splitlines()
    unquoted = [n for n, text in enumerate(lines, 1)
                if not QUOTED.fullmatch(text)]
    if unquoted:
        problems.append(f"fields not all double-quoted on lines "
                        f"{short(unquoted)}")
    rows = rows_of(new)
    if not rows or rows[0] != HEADER:
        # Every field check below assumes the columns sit where the header
        # says; after a change of columns they would only report noise.
        problems.append("the header row is not the runbook's; its columns "
                        "were not checked")
        return flag("ledger", count(max(len(rows) - 1, 0), "row"), problems)
    body = list(enumerate(rows[1:], 2))
    wrong = [n for n, row in body if len(row) != len(HEADER)]
    if wrong:
        problems.append(f"not {len(HEADER)} fields on lines {short(wrong)}")
    good = [(n, row) for n, row in body if len(row) == len(HEADER)]
    statuses = [n for n, row in good if row[1] not in STATUSES]
    if statuses:
        problems.append(f"status not new, applied, rejected or skipped on "
                        f"lines {short(statuses)}")
    tiers = [n for n, row in good if row[5] not in TIERS]
    if tiers:
        problems.append(f"tier not 1, 2 or 3 on lines {short(tiers)}")

    summary = count(len(good), "row")
    old = blob(base, LEDGER)
    old_rows = rows_of(old) if old is not None else []
    if old_rows and old_rows[0] != HEADER:
        summary += ("; the last commit's ledger had other columns, so rows "
                    "were not compared")
    elif old_rows:
        before = [row for row in old_rows[1:] if len(row) == len(HEADER)]
        after = [row for _, row in good]
        lost = (collections.Counter(map(fixed, before))
                - collections.Counter(map(fixed, after)))
        if lost:
            problems.append(f"{count(sum(lost.values()), 'row')} lost or "
                            "altered since the last commit:")
            problems += [f"  {key[0]}  {key[1]} | {key[2]}"
                         for key in list(lost)[:8]]
        known = {fixed(row) for row in before}
        added = [row for row in after if fixed(row) not in known]
        seen = collections.Counter((loose(r[2]), loose(r[3])) for r in after)
        repeats = sorted({f"{r[2]} | {r[3]}" for r in added
                          if seen[(loose(r[2]), loose(r[3]))] > 1})
        if repeats:
            problems.append("appended rows repeating a company and role "
                            "already in the ledger:")
            problems += [f"  {text}" for text in repeats[:8]]

        was = {fixed(row): row for row in before}
        moves = collections.Counter()
        tier_edits = notes_edits = 0
        for row in after:
            old_row = was.get(fixed(row))
            if old_row is None:
                continue
            if old_row[1] != row[1]:
                moves[f"{old_row[1]} to {row[1]}"] += 1
            tier_edits += old_row[5] != row[5]
            notes_edits += old_row[6] != row[6]
        edits = [f"{n} {move}" for move, n in sorted(moves.items())]
        edits += [count(tier_edits, "tier edit")] if tier_edits else []
        edits += [count(notes_edits, "notes edit")] if notes_edits else []
        summary = (f"{len(before)} -> {count(len(after), 'row')}, "
                   f"{len(added)} appended; "
                   + (", ".join(edits) or "no rows edited"))

    if problems:
        flag("ledger", summary, problems)
    else:
        ok("ledger", summary + "; LF, quoted, statuses and tiers valid")


def split_appendix(runbook):
    found = re.search(r"^APPENDIX\b", runbook, re.M)
    if not found:
        return runbook, ""
    return runbook[:found.start()], runbook[found.start():]


def blocks(text):
    """The text between each pair of 79-dash rules: the prompts."""
    lines = text.split("\n")
    rules = [n for n, content in enumerate(lines) if content == RULE]
    return (["\n".join(lines[a + 1:b]) for a, b in zip(rules[0::2],
                                                       rules[1::2])],
            len(rules) % 2 == 1)


def opening(block):
    first = block.split("\n", 1)[0]
    return first[:40] + ("..." if len(first) > 40 else "")


def check_prompts(target, touched):
    if not touched & {RUNBOOK, GUIDE}:
        return skip("prompts", "runbook and quick guide unchanged")
    runbook, guide = blob(target, RUNBOOK), blob(target, GUIDE)
    if runbook is None or guide is None:
        return flag("prompts", "the runbook or the quick guide is missing")
    main, _ = split_appendix(runbook.decode("utf-8", "replace"))
    ours, open_ours = blocks(main)
    theirs, open_theirs = blocks(guide.decode("utf-8", "replace"))
    details = []
    if open_ours or open_theirs:
        details.append("a prompt rule without its closing rule")
    if len(ours) != len(theirs):
        details.append(f"the runbook has {len(ours)} prompts before its "
                       f"appendix, the quick guide {len(theirs)}")
    for number, (a, b) in enumerate(zip(ours, theirs), 1):
        if a != b:
            a_lines, b_lines = a.split("\n"), b.split("\n")
            at = next((n for n, pair in enumerate(zip(a_lines, b_lines))
                       if pair[0] != pair[1]),
                      min(len(a_lines), len(b_lines)))
            details.append(f"prompt {number} (\"{opening(a)}\") differs "
                           f"from its line {at + 1}")
    if details:
        flag("prompts", "the quick guide no longer mirrors the runbook",
             details)
    else:
        ok("prompts", f"all {len(ours)} prompts identical in the runbook "
                      "and the quick guide")


def check_width(target, touched):
    paths = [p for p in (RUNBOOK, GUIDE) if p in touched]
    if not paths:
        return skip("width", "runbook and quick guide unchanged")
    long = []
    for path in paths:
        data = blob(target, path)
        if data is None:
            continue
        for number, text in enumerate(
                data.decode("utf-8", "replace").split("\n"), 1):
            if len(text) > WIDTH:
                long.append(f"{path}:{number} is {len(text)} columns")
    if long:
        flag("width", f"{count(len(long), 'line')} past {WIDTH} columns",
             long[:8])
    else:
        ok("width", f"within {WIDTH} columns")


def appendix_parts(runbook):
    _, appendix = split_appendix(runbook)
    templates, _ = blocks(appendix)
    segments = re.search(r"^THE FOUR SEGMENTS\b", appendix, re.M)
    return {
        "sweep template": templates[0] if templates else "",
        "LinkedIn template": templates[1] if len(templates) > 1 else "",
        "segment definitions": appendix[segments.start():] if segments
        else "",
    }


def check_templates(base, target, touched):
    if RUNBOOK not in touched:
        return skip("templates", "runbook unchanged")
    old, new = blob(base, RUNBOOK), blob(target, RUNBOOK)
    if old is None or new is None:
        return skip("templates", "no earlier runbook to compare with")
    before = appendix_parts(old.decode("utf-8", "replace"))
    after = appendix_parts(new.decode("utf-8", "replace"))
    moved = [name for name in after if before[name] != after[name]]
    if not moved:
        return ok("templates", "appendix unchanged")
    stale, followed = [], []
    for name in moved:
        pattern = BUILT_FROM[name]
        carried = sum(fnmatch.fnmatch(path, pattern) for path in touched)
        if carried:
            followed.append(f"{name} changed, and "
                            f"{count(carried, pattern + ' file')} with it")
        else:
            stale.append(f"{name} changed, but no {pattern} file did: they "
                         "run the old text until patched or Step 1 re-runs")
    if stale:
        flag("templates", "live prompt files left behind the appendix",
             stale + followed)
    else:
        ok("templates", "appendix changes carried into the prompt files",
           followed)


def main(argv):
    if len(argv) == 3:
        base, target = argv[1], argv[2]
        described = f"{target} against {base}"
    elif len(argv) == 1:
        has_head = subprocess.run(["git", "rev-parse", "--verify", "-q",
                                   "HEAD"], capture_output=True)
        base = "HEAD" if has_head.returncode == 0 else EMPTY_TREE
        target = ""
        described = "staged changes against HEAD"
    else:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    changed = changes(base, target)
    touched = {path for _, path in changed}
    print(f"review: {described}, {len(changed)} paths")
    check_strays(changed)
    check_ledger(base, target, touched)
    check_prompts(target, touched)
    check_width(target, touched)
    check_templates(base, target, touched)
    if flagged:
        print(f"result: {len(flagged)} flagged ({', '.join(flagged)})")
        return 1
    print("result: nothing flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
