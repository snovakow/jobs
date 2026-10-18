#!/usr/bin/env python3
"""The mechanical checks around a triage, printed for /triage to act on.

    checks.py inputs   before ranking: whether the ledger is committed, and
                       which result files this pass wrote, with their
                       closing blocks
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
STATUSES = {"new", "applied", "closed", "skipped"}
QUOTED = re.compile(r'"(?:[^"]|"")*"(?:,"(?:[^"]|"")*")*')
RESTORE = ("enter: Restore root/ledger.csv and run/05-triage.txt from their "
           "last commit.")


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
        todo.append("If they are your status edits, enter /commit. If a "
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
            todo.append(f"In {step}'s conversation, enter /capture, then run "
                        f"Step 4 again. To triage without {name} this pass, "
                        f"enter: Restore {path} from its last commit. Then "
                        "run Step 4 again.")
    for n, item in enumerate(todo or ["nothing"]):
        note("To do" if n == 0 else "", item)
    if skipped:
        note("Note", "A run you did make shows as not run this pass if its "
             "/capture never wrote the file: enter /capture in its "
             "conversation, then run Step 4 again.")


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
    note("To do", "In this conversation, enter: Fix the ledger rows the "
         "checks name." if problems else "nothing")


if __name__ == "__main__":
    modes = {"inputs": inputs, "ledger": ledger}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    modes[sys.argv[1]]()
