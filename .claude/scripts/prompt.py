#!/usr/bin/env python3
"""Print what a playbook step runs from, for the command that runs it.

    prompt.py LABEL          the prompt of the section headed LABEL, such as
                             "STEP 4" or "DIFF CHECK"
    prompt.py --file PATH    a file in the repository, such as
                             root/02-linkedin.txt

A section's heading is a line that is LABEL alone, or LABEL followed by an
em dash, before the playbook's APPENDIX. Its prompt is the text between the
first pair of 79-dash rules after it, as review.py reads them, before the
next STEP heading. Paths resolve from the repository root, so the working
directory does not matter. Anything not found exits 1, which aborts the
command that asked for it rather than letting it run without its prompt.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK = ROOT / "root" / "00-playbook.txt"
RULE = "-" * 79


def fail(message):
    print(f"prompt.py: {message}", file=sys.stderr)
    sys.exit(1)


def main_part():
    """The playbook's lines before its appendix, which holds templates."""
    text = PLAYBOOK.read_text(encoding="utf-8")
    found = re.search(r"^APPENDIX\b", text, re.M)
    return (text[:found.start()] if found else text).split("\n")


def prompt(label):
    lines = main_part()
    start = next((n for n, line in enumerate(lines)
                  if line == label or line.startswith(label + " —")), None)
    if start is None:
        fail(f'no heading "{label}" in {PLAYBOOK.relative_to(ROOT)}')
    end = next((n for n in range(start + 1, len(lines))
                if lines[n].startswith("STEP ")), len(lines))
    rules = [n for n in range(start + 1, end) if lines[n] == RULE]
    if len(rules) < 2:
        fail(f'"{label}" has no prompt')
    return "\n".join(lines[rules[0] + 1:rules[1]])


def repository_file(path):
    target = (ROOT / path).resolve()
    if ROOT not in target.parents or not target.is_file():
        fail(f"no file {path} in the repository")
    return target.read_text(encoding="utf-8").rstrip("\n")


def main(argv):
    args = argv[1:]
    if len(args) == 2 and args[0] == "--file":
        text = repository_file(args[1])
    elif len(args) == 1 and not args[0].startswith("--"):
        text = prompt(args[0])
    else:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
