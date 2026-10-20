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
PLAYBOOK = "root/00-playbook.txt"

HEADER = ["first_seen", "status", "company", "role", "source", "tier",
          "notes", "url"]
# Set when a row is appended and never changed after. Status, tier and
# notes are the fields a person edits.
FIXED = (0, 2, 3, 4, 7)
STATUSES = {"new", "applied", "closed", "skipped"}
TIERS = {"1", "2", "3"}
QUOTED = re.compile(r'"(?:[^"]|"")*"(?:,"(?:[^"]|"")*")*')

RULE = "-" * 79

# Which live prompt files each part of the playbook's appendix is copied into.
BUILT_FROM = {
    "sweep template": "root/02-sweep.txt",
    "LinkedIn template": "root/02-linkedin.txt",
    "Indeed template": "root/02-indeed.txt",
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
        if name == "ledger.csv" and path != LEDGER:
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
        problems.append("the header row is not the playbook's; its columns "
                        "were not checked")
        return flag("ledger", count(max(len(rows) - 1, 0), "row"), problems)
    body = list(enumerate(rows[1:], 2))
    wrong = [n for n, row in body if len(row) != len(HEADER)]
    if wrong:
        problems.append(f"not {len(HEADER)} fields on lines {short(wrong)}")
    good = [(n, row) for n, row in body if len(row) == len(HEADER)]
    statuses = [n for n, row in good if row[1] not in STATUSES]
    if statuses:
        problems.append(f"status not new, applied, closed or skipped on "
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


def split_appendix(playbook):
    found = re.search(r"^APPENDIX\b", playbook, re.M)
    if not found:
        return playbook, ""
    return playbook[:found.start()], playbook[found.start():]


def blocks(text):
    """The text between each pair of 79-dash rules: the prompts."""
    lines = text.split("\n")
    rules = [n for n, content in enumerate(lines) if content == RULE]
    return (["\n".join(lines[a + 1:b]) for a, b in zip(rules[0::2],
                                                       rules[1::2])],
            len(rules) % 2 == 1)


def appendix_parts(playbook):
    _, appendix = split_appendix(playbook)
    templates, _ = blocks(appendix)
    segments = re.search(r"^THE FOUR SEGMENTS\b", appendix, re.M)
    return {
        "sweep template": templates[0] if templates else "",
        "LinkedIn template": templates[1] if len(templates) > 1 else "",
        "Indeed template": templates[2] if len(templates) > 2 else "",
        "segment definitions": appendix[segments.start():] if segments
        else "",
    }


def check_templates(base, target, touched):
    if PLAYBOOK not in touched:
        return skip("templates", "playbook unchanged")
    old, new = blob(base, PLAYBOOK), blob(target, PLAYBOOK)
    if old is None or new is None:
        return skip("templates", "no earlier playbook to compare with")
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
    check_templates(base, target, touched)
    if flagged:
        print(f"result: {len(flagged)} flagged ({', '.join(flagged)})")
        return 1
    print("result: nothing flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
