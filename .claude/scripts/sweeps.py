"""What the sweep's files hold, read from git, for the programs that count
them: setup's SWEEPS block and /sweep's checks. It prints nothing itself.

A sweep's file is a committed copy of run/03-results.txt that does not end
with a LINK CHECK block: Step 2 commits it before the link check edits it.
A pass ends when its triage is committed, so a pass's sweep is the last such
copy committed in it, a continued sweep's included. A copy from before
root/02-sweep.txt last changed was found by another prompt, so none counts.

No one sweep reaches every target company in a segment's list, so thinness is
judged over a round: the latest passes that between them reached them all.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = "run/03-results.txt"
PROMPT = "root/02-sweep.txt"
TRIAGE = "run/05-triage.txt"
# In the order the sweep runs them.
SEGMENTS = ("seg1", "seg3", "seg2", "seg4")
TOKENS = ("OK", "RELOCATE", "UNCLEAR", "STALE", "UNVERIFIED")
# A segment with this many rows or fewer is short.
THIN = 3
# The three lines the COVERAGE block gives each segment, in its order.
KINDS = ("targets not reached", "boards not loaded", "keywords not searched")
ENTRY = re.compile(r"(seg[1-4]) (" + "|".join(KINDS) + r"):\s*(.*)", re.I)


def git(*args):
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return done.stdout if done.returncode == 0 else None


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


def rows(text):
    """The table's rows, each as its fields."""
    found = []
    for line in text.split("\n"):
        fields = line.split(" | ")
        codes = fields[0].split()
        if len(fields) >= 9 and codes and set(codes) <= set(SEGMENTS):
            found.append(fields)
    return found


def counts(text):
    """Each segment's rows. A row two segments found counts under each."""
    count = dict.fromkeys(SEGMENTS, 0)
    for fields in rows(text):
        for code in set(fields[0].split()):
            count[code] += 1
    return count


def tokens(fields):
    """The status tokens a row's location column starts with."""
    found = []
    for word in fields[3].split():
        if word not in TOKENS:
            break
        found.append(word)
    return found


def coverage(text):
    """What the file's last COVERAGE block says each segment's run did not
    get to, as {segment: {kind: [names]}}, or None when it has no block. A
    line the block leaves out is missing from its segment's dict."""
    lines = [l.strip() for l in text.split("\n")]
    heads = [n for n, l in enumerate(lines) if l.rstrip(":") == "COVERAGE"]
    if not heads:
        return None
    found = {code: {} for code in SEGMENTS}
    for line in lines[heads[-1] + 1:]:
        entry = ENTRY.fullmatch(line)
        if not entry:
            if line:
                break
            continue
        code, kind, names = entry.groups()
        code, kind, names = code.lower(), kind.lower(), names.strip(" .")
        found[code][kind] = [] if names.lower() == "none" else names_in(names)
    return found


def names_in(line):
    """A COVERAGE line's names, split at its semicolons, or at its commas
    when it has none, but never inside parentheses, where a reason can use
    either."""
    for mark in ";,":
        parts, depth, start = [], 0, 0
        for n, char in enumerate(line):
            depth += {"(": 1, ")": -1}.get(char, 0)
            if char == mark and depth <= 0:
                parts.append(line[start:n])
                start = n + 1
        if parts:
            parts.append(line[start:])
            return [part.strip() for part in parts if part.strip()]
    return [line.strip()] if line.strip() else []


def missing(cover):
    """The lines a COVERAGE block left out, such as seg1 boards not loaded."""
    return [f"{code} {kind}" for code in SEGMENTS for kind in KINDS
            if kind not in cover[code]]


def loose(name):
    """A name as COVERAGE blocks are compared: case, punctuation, spacing
    and any note in parentheses aside."""
    name = re.sub(r"\([^()]*\)", " ", name)
    return " ".join(re.sub(r"[^\w\s]", " ", name.casefold()).split())


def round_of(texts, code):
    """How many of these files, newest first, make the segment's last full
    round: the fewest latest passes, two at least, that between them reached
    every target company in its list, as their COVERAGE blocks say. None
    while no run of latest passes has. A file with no COVERAGE line for the
    segment reached nothing that anyone can tell. A company counts as not
    reached in an older file whose line holds its name's words, however
    that line separates its names, so a name with a comma in it, split
    apart on a line with no semicolons, still matches."""
    left = None
    for n, text in enumerate(texts, 1):
        cover = coverage(text)
        names = cover[code].get(KINDS[0]) if cover else None
        if names is not None:
            if left is None:
                left = {loose(name) for name in names} - {""}
            else:
                line = f" {loose(' '.join(names))} "
                left = {name for name in left if f" {name} " in line}
        if left is not None and not left and n >= 2:
            return n
    return None


def runs(text):
    """How many research runs the file's closing notes come from: the
    highest run number their CLOSING NOTES headings give, or 1."""
    numbers = [int(n) for line in text.split("\n")
               if line.strip().startswith("CLOSING NOTES")
               for n in re.findall(r"RUN (\d+)", line)]
    return max(numbers, default=1)


def thin(texts):
    """The segments short in every pass of their last full round, from these
    files, newest first."""
    found = []
    for code in SEGMENTS:
        size = round_of(texts, code)
        if size and all(counts(text)[code] <= THIN for text in texts[:size]):
            found.append(code)
    return found


def short(texts):
    """The segments short in the latest two of these files, newest first,
    whose round is not complete: their lists have not all been reached."""
    return [code for code in SEGMENTS if len(texts) >= 2
            and round_of(texts, code) is None
            and all(counts(text)[code] <= THIN for text in texts[:2])]


def passes():
    """The sweep's file of each pass since root/02-sweep.txt last changed,
    the newest pass first, as (date, commit, text, triaged), where triaged
    is False for the pass not triaged yet. None while root/02-sweep.txt has
    uncommitted changes."""
    if git("status", "--porcelain", "--", PROMPT):
        return None
    log = git("log", "--format=%x00%H %ad", "--date=short", "--name-only",
              "--", RESULTS, TRIAGE, PROMPT) or b""
    current = {"triaged": False, "file": None}
    groups = [current]
    for entry in log.decode().split("\x00")[1:]:
        head, *names = [l for l in entry.split("\n") if l.strip()]
        commit, date = head.split()
        if TRIAGE in names:
            current = {"triaged": True, "file": None}
            groups.append(current)
        if RESULTS in names and current["file"] is None:
            data = git("show", f"{commit}:{RESULTS}")
            text = data.decode("utf-8", "replace") if data else ""
            if text and not ends_with_link_check(text):
                current["file"] = (date, commit[:7], text)
        if PROMPT in names:
            break
    return [(*group["file"], group["triaged"]) for group in groups
            if group["file"]]


def counted():
    """Which passes count, in words for a note."""
    out = git("log", "-1", "--format=%ad", "--date=short", "--", PROMPT)
    date = out.decode().strip() if out else ""
    if not date:
        return f"passes after {PROMPT} is first committed"
    return f"passes since {PROMPT} last changed, on {date}"
