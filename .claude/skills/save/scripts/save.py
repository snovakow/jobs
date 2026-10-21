#!/usr/bin/env python3
"""Commit the files a pass writes, for /save.

    save.py save    commit them, once the commit review's checks pass
    save.py check   everything short of committing: the review, and the
                    message it would commit under

A pass's files are run/, root/ledger.csv, root/01-positioning.txt, the
root/02-*.txt prompt files and root/resume.pdf. They are staged in an index
of this program's own, so the review sees only them, and committed from it.
Every other change is /commit's and stays as it was, staged or not. The
working tree is never touched, and nothing is pushed. It always exits 0, so
/save can report what happened rather than fail to load.
"""

import csv
import io
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REVIEW = ROOT / ".claude" / "skills" / "commit" / "scripts" / "review.py"
LEDGER = "root/ledger.csv"
RESULTS = "run/03-results.txt"
TRIAGE = "run/05-triage.txt"
PASS = ("run", LEDGER, "root/01-positioning.txt", ":(glob)root/02-*.txt",
        "root/resume.pdf")
OTHER = (".", ":(exclude)run", f":(exclude){LEDGER}",
         ":(exclude)root/01-positioning.txt", ":(exclude,glob)root/02-*.txt",
         ":(exclude)root/resume.pdf")
# In the order the sweep runs them.
SEGMENTS = ("seg1", "seg3", "seg2", "seg4")
# What a commit message calls each search prompt.
PROMPTS = {"root/02-sweep.txt": "sweep", "root/02-linkedin.txt": "LinkedIn",
           "root/02-indeed.txt": "Indeed"}
# Each browser run's file, with the source codes its rows start with.
RUNS = (("run/04-linkedin.txt", "LinkedIn", r"li[1-4]b?|li[1-4][tr]"),
        ("run/04-indeed.txt", "Indeed", r"in[1-4][tr]"))


def git(*args, env=None, data=None):
    return subprocess.run(["git", *args], cwd=ROOT, env=env, input=data,
                          capture_output=True, text=True)


def listed(items):
    """Names joined for prose: a, b and c."""
    items = list(items)
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def plural(n, word, many=None):
    return f"{n} {word if n == 1 else many or word + 's'}"


def changed(spec):
    """The paths git status lists for these pathspecs."""
    out = git("status", "--porcelain", "--untracked-files=all", "--", *spec)
    return [l[3:] for l in out.stdout.splitlines() if l]


def present(env):
    """The pass's pathspecs that match a file, in the last commit or the
    working tree. git add refuses the whole command over one that matches
    nothing, as run/ does on a first setup, before any sweep."""
    return [spec for spec in PASS
            if git("ls-files", "--", spec, env=env).stdout
            or git("ls-files", "--others", "--exclude-standard", "--", spec,
                   env=env).stdout]


def ran(env, *args):
    """Run git on the save's own index, saying so if it fails."""
    done = git(*args, env=env)
    if done.returncode:
        print(f"Nothing saved: git {args[0]} failed: "
              f"{(done.stderr or done.stdout).strip()}")
    return not done.returncode


def blocked():
    """Why committing now would tangle something, or None."""
    found = git("rev-parse", "--git-dir").stdout.strip()
    gitdir = ROOT / found if found else ROOT / ".git"
    for name, what in (("MERGE_HEAD", "a merge"), ("rebase-merge", "a rebase"),
                       ("rebase-apply", "a rebase"),
                       ("CHERRY_PICK_HEAD", "a cherry-pick")):
        if (gitdir / name).exists():
            return f"{what} is in progress"
    if git("symbolic-ref", "-q", "HEAD").returncode:
        return "HEAD is detached"
    return None


def head(path):
    out = git("show", f"HEAD:{path}")
    return out.stdout if out.returncode == 0 else ""


def now(path):
    file = ROOT / path
    if not file.is_file():
        return ""
    return file.read_text(encoding="utf-8", errors="replace")


def rows_of(text, pattern):
    """Each table row's source codes, for rows made only of such codes."""
    rows = []
    for line in text.split("\n"):
        fields = line.split(" | ")
        codes = fields[0].split()
        if len(fields) > 2 and codes and all(re.fullmatch(pattern, c)
                                             for c in codes):
            rows.append(codes)
    return rows


def link_check(text):
    """(closed, moved) from the LINK CHECK block the file ends with."""
    lines = [l for l in text.split("\n") if l.strip()]
    for n in range(len(lines) - 1, -1, -1):
        if lines[n] == "LINK CHECK: NONE":
            return (0, 0) if n == len(lines) - 1 else None
        if lines[n] == "LINK CHECK:":
            rest = lines[n + 1:]
            if rest and all(l.startswith(("CLOSED: ", "MOVED: "))
                            for l in rest):
                return (sum(l.startswith("CLOSED: ") for l in rest),
                        sum(l.startswith("MOVED: ") for l in rest))
            return None
    return None


def ledger_rows(text):
    return [r for r in csv.reader(io.StringIO(text)) if r][1:]


def ledger_change(before, after):
    """Rows appended, and statuses, tiers and notes changed in earlier rows.
    The ledger only grows, so the earlier rows keep their places."""
    old, new = ledger_rows(before), ledger_rows(after)
    pairs = [(a, b) for a, b in zip(old, new) if len(a) == len(b) == 8]
    return (max(len(new) - len(old), 0),
            sum(a[1] != b[1] for a, b in pairs),
            sum(a[5] != b[5] for a, b in pairs),
            sum(a[6] != b[6] for a, b in pairs))


def describe(paths):
    """What a commit of these paths holds: (name, detail) pairs for its
    subject, and lines for its description."""
    names, parts, body = set(paths), [], []
    if RESULTS in names:
        text = now(RESULTS)
        block = link_check(text)
        if block == (0, 0):
            parts.append(("the link check", "nothing closed or moved"))
            body.append("Link check: LINK CHECK: NONE.")
        elif block:
            closed, moved = block
            parts.append(("the link check",
                          f"{closed} closed, {moved} moved"))
            body.append(f"Link check: {plural(closed, 'row')} cut as closed, "
                        f"{plural(moved, 'row')} moved to the employer's own "
                        "board.")
        else:
            rows = rows_of(text, r"seg[1-4]")
            parts.append(("the sweep's file", plural(len(rows), "row")))
            body.append("Sweep: " + ", ".join(
                f"{s} {sum(s in r for r in rows)}" for s in SEGMENTS) +
                ", a row two segments found counting under each.")
    for path, name, pattern in RUNS:
        if path in names:
            rows = plural(len(rows_of(now(path), pattern)), "row")
            parts.append((f"the {name} run", rows))
            body.append(f"{name} run: {rows}.")
    if LEDGER in names:
        appended, statuses, tiers, notes = ledger_change(head(LEDGER),
                                                         now(LEDGER))
        if TRIAGE in names:
            parts.append(("a triage", plural(appended, "row") + " appended"))
        elif appended:
            parts.append((plural(appended, "ledger row"), ""))
        edits = [plural(n, word) for n, word in
                 ((statuses, "status change"), (tiers, "tier change"),
                  (notes, "notes change")) if n]
        if edits:
            parts.append((listed(edits), ""))
        elif not appended and TRIAGE not in names:
            parts.append(("the ledger", ""))
        body.append(f"Ledger: {plural(appended, 'row')} appended; "
                    f"{plural(statuses, 'status', 'statuses')}, "
                    f"{plural(tiers, 'tier')} "
                    f"and {notes} notes changed in earlier rows.")
    elif TRIAGE in names:
        parts.append(("a triage", ""))
    step1 = sorted(p for p in names if p == "root/01-positioning.txt"
                   or re.fullmatch(r"root/02-[^/]*\.txt", p))
    prompts = [p for p in step1 if p != "root/01-positioning.txt"]
    if "root/01-positioning.txt" in names:
        parts.append(("Step 1's positioning read"
                      + (" and search prompts" if prompts else ""), ""))
        body.append("Step 1: " + listed(step1) + ".")
    elif prompts:
        # A prompt patched to match its template, with no Step 1 run.
        kinds = [PROMPTS.get(p, p) for p in prompts]
        parts.append(("the " + listed(kinds)
                      + (" prompt" if len(kinds) == 1 else " prompts"), ""))
        body.append("Search prompts: " + listed(prompts) + ".")
    if "root/resume.pdf" in names:
        parts.append(("the resume", ""))
        body.append("Resume: root/resume.pdf.")
    known = {RESULTS, TRIAGE, *(path for path, _, _ in RUNS)}
    rest = sorted(p for p in names if p.startswith("run/") and p not in known)
    if rest:
        parts.append((listed(rest), ""))
        body.append("Other run files: " + listed(rest) + ".")
    if not parts:
        parts.append((listed(sorted(names)), ""))
    return parts, body


def subject(parts):
    """The fullest subject that fits in 70 characters."""
    def with_detail(part):
        return f"{part[0]} ({part[1]})" if part[1] else part[0]
    tries = ["Save " + listed(with_detail(p) for p in parts),
             "Save " + listed(p[0] for p in parts),
             "Save " + with_detail(parts[0]) + " and more",
             "Save " + parts[0][0] + " and more"]
    for text in tries:
        if len(text) <= 70:
            return text
    return tries[-1][:70]


def save(commit):
    why = blocked()
    if why:
        print(f"Nothing saved: {why}. Finish it, then enter /save again.")
        return
    others = changed(OTHER)
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        if not ran(env, "read-tree", "HEAD"):
            return
        specs = present(env)
        if specs and not ran(env, "add", "-A", "--", *specs):
            return
        staged = git("diff", "--cached", "--name-only", env=env)
        paths = staged.stdout.splitlines()
        if not paths:
            print("Nothing to save: no pass file differs from the last "
                  "commit.")
            if others:
                print(f"Left for /commit: {listed(others)}.")
            return
        review = subprocess.run([sys.executable, str(REVIEW)], cwd=ROOT,
                                env=env, capture_output=True, text=True)
        print((review.stdout or review.stderr).rstrip())
        if review.returncode:
            print("\nNothing saved: the review flagged what is above. Fix "
                  "what it names, then enter /save again.")
            return
        parts, body = describe(paths)
        lines = [textwrap.fill(line, 72) for line in body]
        message = "\n".join([subject(parts), "", *lines,
                             "", "Saved with /save, after the commit "
                             "review's checks."]) + "\n"
        if not commit:
            print("\nWould commit " + listed(paths) + ":\n\n" + message)
            return
        done = git("commit", "-q", "-F", "-", env=env, data=message)
        if done.returncode:
            print("\nNothing saved: git commit failed: "
                  f"{(done.stderr or done.stdout).strip()}")
            return
    # The real index still holds the old entries for these paths: bring them
    # up to the new commit, which is what the working tree holds.
    git("reset", "-q", "--", *PASS)
    short = git("log", "-1", "--format=%h").stdout.strip()
    print(f"\nSaved {short}, with {listed(paths)}:\n\n{message}")
    if others:
        print(f"Left for /commit: {listed(others)}.")
    print("Nothing was pushed. To undo it, enter: git reset --soft HEAD~1")


if __name__ == "__main__":
    modes = {"save": True, "check": False}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        print(__doc__.strip())
    else:
        save(modes[sys.argv[1]])
