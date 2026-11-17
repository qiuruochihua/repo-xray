# repo-xray

**接手一个陌生代码仓库时，先给它拍张 X 光。**

你有没有过这种经历：打开一个没见过的项目，几百个文件摆在面前，不知道从哪儿看起——它到底是做什么的？怎么跑起来？想改一个小功能，该动哪个文件？哪里藏着不能碰的坑？

repo-xray 就是为这一刻准备的。你把仓库交给它，它会通读整个项目，产出一份《上手包》（`REPO_XRAY.md`），把上面这些问题一次答清：

1. **怎么跑起来**——每条命令都实际运行验证过；跑不通的会标明原因，不糊弄。
2. **结构长什么样**——一页架构图加一段白话说明，看懂各部分怎么配合。
3. **想改东西动哪里**——「改 X → 动 Y → 用 Z 验证」的改动索引，照着做就行。
4. **哪里有坑**——带出处证据的地雷清单，动手之前先避雷。
5. **先看哪几个文件**——恰好 5 个文件的阅读路线，按依赖顺序排好，看完就懂个七八成。

它是一个给 Muse 用的 Skill（技能包），只读扫描你的仓库，只写出这一份报告，不动任何代码。

*An X-ray for unfamiliar codebases: repo-xray reads a repo and produces a verified onboarding pack — how to run it, how it's structured, where to make changes, what to watch out for, and the 5 files to read first.*

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
