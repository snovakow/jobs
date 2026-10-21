#!/usr/bin/env python3
"""The mechanical checks around a triage, and the counts item 2b reads,
printed for /triage to act on.

    checks.py inputs   before ranking: whether the ledger is committed, and
                       which result files this pass wrote, with their
                       closing blocks
    checks.py sources  before ranking: the ledger's rows counted by the
                       search that found them, since that search's prompt
                       file last changed
    checks.py ledger   after writing: what the triage did to the ledger
                       since its last commit

A pass rewrites the file of every run it makes, so a result file belongs to
this pass when it differs from its copy in the last commit that changed
run/05-triage.txt. It only reads; it changes nothing.
"""

import collections
import csv
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LEDGER = "root/ledger.csv"
TRIAGE = "run/05-triage.txt"
RUNS = (("Sweep", "run/03-results.txt", "Step 2B"),
        ("LinkedIn", "run/04-linkedin.txt", "Step 3"),
        ("Indeed", "run/04-indeed.txt", "Step 3B"))
# Each prompt file and the searches it runs, in the order SOURCES lists them.
PROMPTS = (("root/02-sweep.txt", ("seg1", "seg2", "seg3", "seg4")),
           ("root/02-linkedin.txt", ("li1", "li1b", "li2", "li3", "li4")),
           ("root/02-indeed.txt", ("in1", "in2", "in3", "in4")))
STATUSES = {"new", "applied", "closed", "skipped"}
QUOTED = re.compile(r'"(?:[^"]|"")*"(?:,"(?:[^"]|"")*")*')
RESTORE = ("in a new thread on Haiku at low effort, enter: Restore "
           "root/ledger.csv and run/05-triage.txt from their last commit.")


def git(*args):
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return done.stdout if done.returncode == 0 else None


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


def without(path, base):
    """How to put back the copy of path the last triage read, which reads as
    not run this pass. Step 4 saves the pass before triage, so the file's own
    last commit already holds this pass's copy."""
    if base and git("cat-file", "-e", f"{base.decode()}:{path}") is not None:
        return ("in a new thread on Haiku at low effort, enter: Restore "
                f"{path} as it was in commit {base.decode()[:7]}.")
    return f"delete {path}."


def capture_verdict(text):
    """The CAPTURE CHECK line the file ends its block with, or None."""
    lines = text.split("\n")
    found = [l for l in lines if l.startswith("CAPTURE CHECK: ")]
    return found[-1] if found else None


def inputs():
    print("INPUTS")
    todo = []
    if git("status", "--porcelain", "--", LEDGER):
        line("Ledger", "root/ledger.csv has uncommitted changes", "stop")
        todo.append("If they are your status edits, enter /save. If a "
                    "triage already added rows this pass, " + RESTORE +
                    " Then run Step 4 again.")
    else:
        line("Ledger", "committed", "ok")
    base = (git("log", "-1", "--format=%H", "--", TRIAGE) or b"").strip()
    skipped = []
    for name, path, step in RUNS:
        file = ROOT / path
        if not file.is_file():
            line(name, "not run this pass", "skip")
            skipped.append(name)
            continue
        data = file.read_bytes()
        if base and git("show", f"{base.decode()}:{path}") == data:
            line(name, "not run this pass", "skip")
            skipped.append(name)
            continue
        text = data.decode("utf-8", "replace")
        if name == "Sweep":
            if ends_with_link_check(text):
                line(name, "this pass, link-checked", "read")
            else:
                line(name, "this pass, but no LINK CHECK block", "stop")
                todo.append(f"Run {step}, then run Step 4 again.")
            continue
        verdict = capture_verdict(text)
        if verdict:
            short = verdict.replace("CAPTURE CHECK: ", "capture check ")
            line(name, f"this pass, {short.split(' — ')[0]}", "read")
        else:
            line(name, "this pass, but no CAPTURE CHECK block", "stop")
            todo.append(f"In {step}'s thread, enter /capture, then run "
                        f"Step 4 again. To triage without {name} this pass, "
                        + without(path, base) + " Then run Step 4 again.")
    for n, item in enumerate(todo or ["nothing"]):
        note("To do" if n == 0 else "", item)
    if skipped:
        note("Note", "A run you did make shows as not run this pass if its "
             "/capture never wrote the file: enter /capture in its "
             "thread, then run Step 4 again.")


def counted_from(path):
    """How many ledger rows there were when path last changed, or None when
    path has uncommitted changes. The ledger only grows, so every row past
    that count was found by the prompt as it now stands."""
    if git("status", "--porcelain", "--", path):
        return None
    commit = (git("log", "-1", "--format=%H", "--", path) or b"").strip()
    data = git("show", f"{commit.decode()}:{LEDGER}") if commit else None
    if not data:
        return 0
    return max(len(data.decode("utf-8", "replace").splitlines()) - 1, 0)


def search_of(code):
    """The search a source code names; an Indeed set counts both passes."""
    return code[:3] if re.fullmatch(r"in[1-4][tr]", code) else code


def listed(items):
    """Names joined for prose: a, b and c."""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def sources():
    print("SOURCES")
    file = ROOT / LEDGER
    text = file.read_text(encoding="utf-8") if file.is_file() else ""
    rows = list(csv.reader(l for l in text.split("\n") if l))[1:]
    counts = collections.defaultdict(collections.Counter)
    starts = collections.defaultdict(list)
    for path, names in PROMPTS:
        start = counted_from(path)
        starts[start].append(path.split("/")[-1])
        if start is None:
            continue
        for number, row in enumerate(rows, 1):
            if number <= start or len(row) != 8:
                continue
            found = {search_of(code) for code in row[4].split()}
            for name in found.intersection(names):
                counts[name]["rows"] += 1
                counts[name]["tier " + row[5]] += 1
                counts[name][row[1]] += 1
    print(f"  {'Search':<10} {'Rows':>4} {'Tier 1':>7} {'Tier 2':>7} "
          f"{'Tier 3':>7} {'Applied':>8}")
    for _, names in PROMPTS:
        for name in names:
            c = counts[name]
            print(f"  {name:<10} {c['rows']:>4} {c['tier 1']:>7} "
                  f"{c['tier 2']:>7} {c['tier 3']:>7} {c['applied']:>8}")
    groups = [(f"ledger lines {start + 2} to {len(rows) + 1}"
               if start < len(rows) else "no rows yet")
              + f" for {listed(files)}"
              for start, files in starts.items() if start is not None]
    note("From", ("; ".join(groups) + ": the rows appended since each "
                  "prompt file last changed, by line number with the header "
                  "as line 1. " if groups else "") +
         "A row several searches found counts under each, and an Indeed "
         "set counts both passes.")
    if None in starts:
        note("Note", f"{listed(starts[None])} has uncommitted changes, so "
             "its searches count nothing until it is committed.")


def loose(text):
    return " ".join(re.sub(r"[^\w\s]", " ",
                           text.casefold().replace("-", " ")).split())


def ledger():
    print("LEDGER")
    before = (git("show", f"HEAD:{LEDGER}") or b"").decode("utf-8")
    if not before:
        line("Ledger", "no committed ledger to compare with", "ok")
        note("To do", "nothing")
        return
    after_bytes = (ROOT / LEDGER).read_bytes()
    after = after_bytes.decode("utf-8", "replace")
    old, new = before.split("\n"), after.split("\n")
    problems = []
    if after_bytes.count(b"\r"):
        problems.append("it has carriage returns; every line must be LF")
    kept = new[:len(old) - 1] == old[:-1] if old[-1] == "" else False
    if not kept:
        lost = collections.Counter(old) - collections.Counter(new)
        count = sum(n for l, n in lost.items() if l)
        rows = "row" if count == 1 else "rows"
        line("Ledger", f"{count} earlier {rows} changed or removed", "problem")
        note("To do", RESTORE[0].upper() + RESTORE[1:] +
             " Then run Step 4 again.")
        return
    added = [l for l in new[len(old) - 1:] if l]
    rows = list(csv.reader(l for l in old if l))[1:]
    keys = collections.Counter((loose(r[2]), loose(r[3])) for r in rows
                               if len(r) == 8)
    for n, text in enumerate(added, len(old)):
        fields = next(csv.reader([text]))
        if not QUOTED.fullmatch(text) or len(fields) != 8:
            problems.append(f"line {n} is not 8 double-quoted fields")
            continue
        if fields[1] != "new":
            problems.append(f"line {n} has status {fields[1]}, not new")
        if fields[5] not in {"1", "2", "3"}:
            problems.append(f"line {n} has tier {fields[5]}")
        key = (loose(fields[2]), loose(fields[3]))
        if keys[key]:
            problems.append(f"line {n} repeats {fields[2]} | {fields[3]}")
        keys[key] += 1
    summary = (f"{len(rows)} rows before, {len(rows) + len(added)} after: "
               f"{len(added)} added, none changed or removed")
    line("Ledger", summary, "problem" if problems else "ok")
    for problem in problems:
        note("", problem)
    note("To do", "In this thread, enter: Fix the ledger rows the "
         "checks name." if problems else "nothing")


if __name__ == "__main__":
    modes = {"inputs": inputs, "sources": sources, "ledger": ledger}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    modes[sys.argv[1]]()
