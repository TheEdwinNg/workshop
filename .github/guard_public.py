#!/usr/bin/env python3
"""Public safety net for this repo, run by GitHub on every push and pull request.

This repo only holds finished, public web pages. The real privacy check (with a private word
list) runs before anything is pushed; this one re-checks, in public, the things that need no
private knowledge: allowed file types, file sizes, and patterns that look like personal data
(emails, phone numbers, street addresses, postal codes, large dollar amounts, secret keys).
"""
import os, re, sys

ALLOWED_EXT = {".html", ".css", ".js", ".json", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".ico", ".woff2"}
ALLOWED_EXACT = {"README.md", ".nojekyll", ".gitignore", "LICENSE"}
TEXT_EXT = {".html", ".css", ".js", ".json", ".svg", ".md"}
PATTERNS = [
    ("email address", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    ("phone number", r"(?<![\w.])\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?![\w.])"),
    ("street address", r"\b\d{1,5}\s+[A-Z][a-z]+(\s[A-Z][a-z]+)?\s+(St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Cres|Crescent|Lane|Ln|Court|Ct)\b"),
    ("postal code", r"(?<![#\w])[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]\d[ABCEGHJ-NPRSTV-Z]\d\b"),
    ("dollar amount", r"\$\s?\d{1,3}(,\d{3})+"),
    ("secret key", r"(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)"),
    ("private link", r"claude\.ai/(artifact|code)"),
]

problems = []
for dirpath, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d != ".git"]
    for name in files:
        rel = os.path.relpath(os.path.join(dirpath, name), ".")
        if rel.startswith(".github/"):
            continue  # this checker and its workflow
        ext = os.path.splitext(name)[1].lower()
        if rel not in ALLOWED_EXACT and name != ".nojekyll" and ext not in ALLOWED_EXT:
            problems.append(f"{rel}: file type not allowed (this repo only holds built pages and images)")
        if os.path.getsize(rel) > 5 * 1024 * 1024:
            problems.append(f"{rel}: over 5 MB")
        if ext in TEXT_EXT:
            text = open(rel, encoding="utf-8", errors="replace").read()
            for label, rx in PATTERNS:
                m = re.search(rx, text)
                if m:
                    problems.append(f"{rel}:{text.count(chr(10), 0, m.start()) + 1}: looks like a {label}: {m.group(0)[:60]}")

if problems:
    print("Blocked: this change looks like it carries something private.")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("public guard: clean")
