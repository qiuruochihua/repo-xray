# repo-xray

**X-ray an unfamiliar repository. Get an onboarding pack where every command
was actually run, every cited path actually exists, and the coverage
statement is true.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Format: SKILL.md](https://img.shields.io/badge/Format-SKILL.md-blue.svg)

An [Agent Skill](https://agentskills.io) for Claude Code and any agent that
reads `SKILL.md`. Point it at a local path or a GitHub URL — a repo you
inherited, a dependency you're evaluating, a project you want to contribute
to — and it produces `REPO_XRAY.md` in the repo root:

| Section | What you get |
|---|---|
| **1. Run it** | Install / run / test commands, each marked `VERIFIED` (executed in-session, with the observed result) or `UNVERIFIED` (with the reason). |
| **2. Architecture** | One Mermaid diagram + one page: entry points, main flow, core modules and what each owns, data stores, external services. |
| **3. Change index** | "To change X, touch Y, prove it with Z" — derived from the actual structure, only for intents this repo supports. |
| **4. Landmines** | Outdated dependencies, untested critical paths, generated files masquerading as source, hidden conventions — each with evidence. |
| **5. Reading path** | Exactly 5 files, in the order a newcomer should read them, one line each on why. |

Plus a header with the one thing most summaries fake: **how much of the
repo was actually read** — in full, sampled, or not opened, counted from
the inventory, not from memory.

## See a real one

[`examples/REPO_XRAY-itsdangerous.md`](examples/REPO_XRAY-itsdangerous.md) —
a Quick-mode x-ray of [pallets/itsdangerous](https://github.com/pallets/itsdangerous),
produced by following this skill. It caught a real onboarding snag (the
test suite doesn't run from a bare `pip install -e .`) and is deliberately
honest that its module notes come from the public API surface, not a full
read. That honesty is the product.

## Install

```bash
git clone https://github.com/qiuruochihua/repo-xray ~/.claude/skills/repo-xray
```

(Any skills directory your agent reads works the same way.)

## Use

> "x-ray this repo: ~/code/some-project"
>
> "Onboard me to https://github.com/some/project — deep mode."
>
> "Before you change anything in this codebase, x-ray it first."

Modes: **Quick** (default, ~15 min of agent work), **Deep** (traces the
main flows end-to-end, maps test coverage against core modules, checks
dependency freshness), and **monorepo** handling (root map + per-package
Quick scans).

## How it works

1. `scripts/inventory.py` (Python 3, stdlib only) counts the repo
   deterministically: files, languages, LOC, manifests, entry-point
   candidates, tests, CI, largest files, a depth-limited tree.
2. The agent verifies the run path (CI config is the most truthful source;
   README is the least), reads from the entry points outward, and drafts
   the pack from [`references/output-template.md`](references/output-template.md).
3. `scripts/verify_report.py` mechanically enforces the honesty contract
   before delivery: the five sections exist, **every backticked path in
   the report exists on disk**, and every command block carries a
   VERIFIED/UNVERIFIED marker. If the checker complains, the report gets
   fixed — not the checker.

Safety: the scan is read-only (the report is the only file written), and
SKILL.md treats running foreign install scripts as a risk decision, not a
default.

## 中文简介

给 AI 一个陌生仓库（本地路径或 GitHub 链接），它产出一份「上手包」
`REPO_XRAY.md`：① 真跑过的安装/运行/测试命令（跑不了的如实标注
UNVERIFIED 并写明原因）；② 一页架构图；③ 「想改 X 就动 Y」的改动索引；
④ 带证据的坑位清单；⑤ 精确到 5 个文件的第一天阅读顺序。头部还有一份
真实的覆盖声明：多少文件真读了、多少抽样、多少没打开——数字来自盘点
脚本，不靠记忆。交付前有校验脚本逐条核对报告里引用的路径是否真实
存在、命令是否都带验证标注。适合接手项目、评估依赖、给开源仓库提 PR
之前先把仓库看透。

## Repo layout

```
SKILL.md                    the skill itself
scripts/inventory.py        deterministic repo inventory (stdlib only)
scripts/verify_report.py    report honesty checker
references/output-template.md   the pack skeleton
examples/                   a real output, produced by the skill
```

## Contributing

Issues and PRs welcome — especially x-rays of well-known repos produced
with the skill (add them to `examples/`), and inventory support for more
ecosystems.

## License

MIT
