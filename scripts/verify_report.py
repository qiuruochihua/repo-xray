#!/usr/bin/env python3
"""repo-xray report checker: enforce the honesty contract mechanically.

Usage: python3 verify_report.py <REPO_XRAY.md> <repo-root>

Checks:
  1. The five pack sections exist (Run it / Architecture / Change index /
     Landmines / Reading path).
  2. Every backticked token that looks like a repo-relative path exists
     on disk under <repo-root>.
  3. Every fenced command block inside "Run it" is preceded (within the
     previous 8 lines — a Status paragraph may wrap) by a Status:
     VERIFIED / UNVERIFIED line.

Exit code 0 = clean. Problems are printed one per line; fix them, don't
argue with the checker.
"""
import os
import re
import sys

REQUIRED_SECTIONS = ["run it", "architecture", "change index", "landmines", "reading path"]

PATHISH = re.compile(r"^[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-+@]+)+/?$|^[A-Za-z0-9_\-]+\.[A-Za-z0-9]{1,6}$")
SKIP_TOKENS = {"REPO_XRAY.md"}  # the report cites itself


def looks_like_path(tok):
    if " " in tok or "*" in tok or "<" in tok or ">" in tok or tok.startswith(("http", "-", "—")):
        return False
    if tok in SKIP_TOKENS:
        return False
    return bool(PATHISH.match(tok))


def main():
    if len(sys.argv) != 3:
        print("usage: verify_report.py <REPO_XRAY.md> <repo-root>", file=sys.stderr)
        return 2
    report_path, root = sys.argv[1], sys.argv[2]
    with open(report_path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    problems = []

    lowered = text.lower()
    for sec in REQUIRED_SECTIONS:
        if not re.search(rf"^#+\s+.*{re.escape(sec)}", lowered, re.M):
            problems.append(f"missing section: {sec}")

    for tok in sorted(set(re.findall(r"`([^`]+)`", text))):
        tok = tok.strip()
        if looks_like_path(tok) and not os.path.exists(os.path.join(root, tok)):
            problems.append(f"cited path does not exist: {tok}")

    in_run = False
    fence_open = False
    for i, line in enumerate(lines):
        if re.match(r"^##\s", line):
            in_run = "run it" in line.lower()
            fence_open = False
            continue
        if in_run and line.strip().startswith("```"):
            if not fence_open:
                context = "\n".join(lines[max(0, i - 8):i])
                if not re.search(r"Status:\s*(VERIFIED|UNVERIFIED)", context):
                    problems.append(
                        f"command block at line {i + 1} has no Status: VERIFIED/UNVERIFIED marker")
            fence_open = not fence_open

    if problems:
        print("repo-xray report check FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("repo-xray report check passed: sections present, cited paths exist, commands labelled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
