#!/usr/bin/env python3
"""repo-xray inventory: deterministic facts about a repository.

Usage: python3 inventory.py <repo-path> [--json]

Stdlib only. Skips VCS internals, dependency folders, and build output.
Prints a Markdown summary by default (paste-ready facts for the agent),
or JSON with --json.
"""
import json
import os
import sys
from collections import Counter

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", "target", ".next", ".nuxt", ".tox", "coverage",
    ".mypy_cache", ".pytest_cache", ".idea", ".vscode", "vendor",
    "Pods", ".dart_tool", "out", "bin", "obj",
}

CODE_EXTS = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
    ".c": "C", ".h": "C/C++", ".cpp": "C++", ".cc": "C++", ".cs": "C#",
    ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
    ".sh": "Shell", ".sql": "SQL", ".html": "HTML", ".css": "CSS",
    ".scss": "CSS", ".vue": "Vue", ".svelte": "Svelte", ".lua": "Lua",
    ".r": "R", ".jl": "Julia", ".ex": "Elixir", ".erl": "Erlang",
    ".hs": "Haskell", ".ml": "OCaml", ".dart": "Dart", ".pl": "Perl",
}

MANIFESTS = {
    "package.json", "pyproject.toml", "setup.py", "requirements.txt",
    "Pipfile", "Cargo.toml", "go.mod", "Gemfile", "composer.json",
    "pom.xml", "build.gradle", "build.gradle.kts", "*.csproj", "*.sln",
    "mix.exs", "pubspec.yaml", "Package.swift", "CMakeLists.txt",
    "Makefile", "Dockerfile", "docker-compose.yml", "compose.yml",
    ".env.example", "flake.nix", "deno.json",
}

CI_FILES = {
    ".github/workflows", ".gitlab-ci.yml", ".circleci", "Jenkinsfile",
    ".travis.yml", "azure-pipelines.yml",
}

ENTRY_NAMES = {
    "main.py", "__main__.py", "app.py", "manage.py", "main.go", "main.rs",
    "main.ts", "main.js", "index.ts", "index.js", "server.ts", "server.js",
    "app.ts", "app.js", "Program.cs", "Application.java", "main.rb",
}

TEST_HINTS = ("test", "spec")


def is_test(path):
    parts = path.replace("\\", "/").split("/")
    base = parts[-1].lower()
    return (
        any(p.lower() in ("tests", "test", "__tests__", "spec") for p in parts[:-1])
        or base.startswith("test_") or base.endswith("_test.go")
        or ".test." in base or ".spec." in base or base.endswith("_test.py")
        or base.endswith("_spec.rb")
    )


def count_lines(path, cap=300000):
    try:
        n = 0
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                n += chunk.count(b"\n")
                if n > cap:
                    return cap
        return n
    except OSError:
        return 0


def walk(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            files.append(rel)
    return files


def tree_lines(root, files, max_depth=3, max_lines=220):
    entries = {}  # rel path -> is_dir
    deep_counts = Counter()
    for rel in files:
        parts = rel.split(os.sep)
        if len(parts) > max_depth:
            deep_counts[os.sep.join(parts[:max_depth])] += 1
            for i in range(1, max_depth + 1):
                entries[os.sep.join(parts[:i])] = True
        else:
            for i in range(1, len(parts)):
                entries[os.sep.join(parts[:i])] = True
            entries[rel] = False
    lines = []
    for path in sorted(entries):
        depth = path.count(os.sep)
        label = path.split(os.sep)[-1] + ("/" if entries[path] else "")
        if entries[path] and deep_counts.get(path):
            label += f"  (+{deep_counts[path]} files deeper)"
        lines.append("  " * depth + label)
        if len(lines) >= max_lines:
            lines.append("… (tree truncated)")
            break
    return lines


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if not args:
        print("usage: inventory.py <repo-path> [--json]", file=sys.stderr)
        return 2
    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    files = walk(root)
    code = [f for f in files if os.path.splitext(f)[1].lower() in CODE_EXTS]
    lang_files = Counter()
    lang_loc = Counter()
    loc_by_file = {}
    for rel in code:
        ext = os.path.splitext(rel)[1].lower()
        lang = CODE_EXTS[ext]
        n = count_lines(os.path.join(root, rel))
        lang_files[lang] += 1
        lang_loc[lang] += n
        loc_by_file[rel] = n

    manifests = sorted(f for f in files
                        if os.path.basename(f) in MANIFESTS
                        or os.path.basename(f).endswith((".csproj", ".sln")))
    ci = sorted(f for f in files
                if any(f == c or f.startswith(c + os.sep) for c in CI_FILES))
    entries = sorted(f for f in code
                     if os.path.basename(f) in ENTRY_NAMES
                     or "/cmd/" in "/" + f.replace(os.sep, "/"))
    tests = [f for f in code if is_test(f)]
    docs = sorted(f for f in files
                  if os.path.splitext(f)[1].lower() in (".md", ".rst")
                  and "node_modules" not in f)
    largest = sorted(loc_by_file.items(), key=lambda kv: -kv[1])[:10]

    data = {
        "root": root,
        "total_files": len(files),
        "code_files": len(code),
        "total_loc": sum(loc_by_file.values()),
        "languages": [
            {"language": lang, "files": lang_files[lang], "loc": lang_loc[lang]}
            for lang, _ in lang_loc.most_common()
        ],
        "manifests": manifests,
        "ci": ci,
        "entry_candidates": entries,
        "test_files": len(tests),
        "test_locations": sorted({os.path.dirname(t) or "." for t in tests})[:12],
        "docs": docs[:20],
        "largest_files": [{"path": p, "loc": n} for p, n in largest],
        "tree": tree_lines(root, files),
    }

    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    out = []
    out.append(f"# Inventory: {root}")
    out.append(f"- Total files (excl. skipped dirs): {data['total_files']}")
    out.append(f"- Code files: {data['code_files']} · counted LOC: {data['total_loc']}")
    out.append("- Languages by LOC: " + ", ".join(
        f"{d['language']} {d['loc']} ({d['files']} files)" for d in data["languages"][:8]))
    out.append(f"- Manifests/config: {', '.join(manifests) or 'none found'}")
    out.append(f"- CI: {', '.join(ci) or 'none found'}")
    out.append(f"- Entry-point candidates: {', '.join(entries) or 'none found'}")
    out.append(f"- Test files: {len(tests)} · locations: {', '.join(data['test_locations']) or 'none'}")
    out.append(f"- Docs: {', '.join(docs[:10]) or 'none'}")
    out.append("- Largest files: " + ", ".join(
        f"{d['path']} ({d['loc']})" for d in data["largest_files"][:5]))
    out.append("\n## Tree (depth ≤3)\n```")
    out.extend(data["tree"])
    out.append("```")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
