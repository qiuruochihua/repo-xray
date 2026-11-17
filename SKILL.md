---
name: repo-xray
description: Produce a verified onboarding pack ("x-ray") for an unfamiliar code repository — a local path or a GitHub URL. Use when the user says "x-ray this repo", "onboard me to this codebase", "explain this repository", "I inherited this project", "how do I run/change this code", or before making changes to a codebase the agent does not already know. The pack contains: run instructions that were actually executed (or honestly marked UNVERIFIED), a one-page architecture map, a change index ("to change X, touch Y"), a landmines list, and a first-day reading path. Never invent commands, paths, or coverage.
license: MIT
metadata:
  version: 1.0.0
---

# repo-xray

X-ray an unfamiliar repository and hand back a pack a competent engineer can
start working from within the hour. The pack's value is its honesty: every
command was run or is labelled UNVERIFIED, every cited path exists, and the
coverage statement says exactly what was and was not read.

## The pack (fixed section order)

1. **Run it** — install / configure / run / test commands, each marked
   `VERIFIED` (executed in this session, with the observed result) or
   `UNVERIFIED` (with the reason: needs secrets, a service, a GUI, a platform
   you don't have…).
2. **Architecture** — one Mermaid diagram + at most one page of prose: entry
   points, the main flow, the core modules and what each owns, data stores,
   external services.
3. **Change index** — a table mapping common change intents to the files to
   touch: "add an endpoint", "change auth", "add a model/table", "change
   config", "add a background job", … Only rows the repo actually supports.
4. **Landmines** — outdated or unmaintained dependencies, critical paths with
   no test coverage, generated files that look hand-written, hidden
   conventions, single points of failure. Each with the evidence you saw.
5. **Reading path** — exactly 5 files, in dependency order, each with one
   line on why it unlocks the next.

Plus a header block: repo, commit, date, depth mode, and a **coverage
statement** ("Read in full: 38 files. Sampled: 12. Not opened: vendored and
generated code, ~2,900 files.").

## Ground rules (the honesty contract)

- **Never invent.** A command, path, module responsibility, or dependency
  status you did not observe does not go in the pack. Guesses are labelled
  `GUESS` or left out.
- **Verify or label.** Run the commands you recommend whenever the
  environment allows. If you cannot run one, it is `UNVERIFIED` with a
  concrete reason — never silently presented as working.
- **Read-only by default.** The only file you create in the target repo is
  the report (`REPO_XRAY.md`). Do not fix bugs, reformat, or "improve"
  anything you find; landmines are reported, not repaired.
- **Running foreign code is a risk decision.** Prefer static reading.
  When you do run install/build/test commands: use the project's own
  documented commands, prefer flags that skip lifecycle scripts where the
  ecosystem supports it (e.g. `npm ci --ignore-scripts` for a first pass),
  never run anything that needs production credentials, and say in the pack
  what you executed.
- **Coverage is a claim — make it true.** Count files from the inventory,
  not from memory. If you sampled, say what you sampled and why.

## Depth modes

- **Quick** (default): inventory + manifests + entry points + main flow +
  run verification. Target ~15 minutes of agent work. Right for "can I use
  this / how does it run".
- **Deep** (on request: "deep x-ray", "we're adopting this", "audit"):
  additionally trace the two or three most important flows end-to-end, map
  test coverage against core modules, and check dependency freshness
  against the ecosystem registry when network access allows.
- **Monorepos**: x-ray the workspace root as a map (packages, shared
  tooling, how they depend on each other), then Quick-x-ray each package
  the user cares about (default: the ones with entry points, max 5) as
  sub-sections.

Ask which mode only when the repo is huge (>5,000 code files) or a
monorepo with many packages; otherwise default to Quick and say so.

## Workflow

### 0. Locate and bound the repo

- Local path: use as-is. GitHub URL: `git clone --depth 1 <url>` into a
  scratch directory, and record the commit (`git rev-parse --short HEAD`).
- Record size signals first (file count from step 1). If the repo is huge,
  switch to the large-repo strategy below before reading anything.

### 1. Inventory (deterministic — run the script)

Run `scripts/inventory.py <repo>` (Python 3, stdlib only). It prints:
file/language counts, a depth-limited tree, manifest & config files,
entry-point candidates, test locations and counts, CI files, docs, and the
largest files. Paste nothing raw into the pack; use it to aim your reading.

If Python is unavailable, reproduce the same inventory with shell tools
(`find`, `wc -l`) — the pack must still be built from counted facts.

### 2. Verify the run path

- Derive candidate commands from manifests, README, and CI config — CI is
  the most truthful source; README is the least.
- Execute in order: install → build (if any) → test (or a smoke subset) →
  run (briefly, with a timeout; a server that starts and logs its port is
  `VERIFIED` for startup).
- Record exact results: versions, pass counts, the first blocking error
  verbatim when something fails. A failing test suite is a finding, not a
  dead end: report "install VERIFIED, tests FAIL (3 of 41, first failure:
  …)".
- Anything requiring secrets, paid services, a display, or another OS:
  `UNVERIFIED` + reason + what the user would need to check it.

### 3. Read the architecture

- Start from the entry points the inventory found. Trace the main flow:
  what starts, what it calls, where requests/jobs/data enter and leave.
- Identify the core modules (usually 5–12): for each, one line — what it
  owns, what it depends on. A module you cannot characterise from reading
  it does not get a confident line; mark it `GUESS` or omit it.
- Note data stores and external services from config and client code, not
  from the README's marketing list.
- Draw the Mermaid diagram from what you traced — boxes you didn't verify
  don't appear.

### 4. Build the change index

Derive rows from the actual structure: where routes/handlers register,
where models/schemas live, where config is loaded, where jobs are defined,
where tests for each area sit. Each row: intent → primary files → the test
that proves the change. If a "standard" area doesn't exist (no background
jobs, no API), the row doesn't appear — an absent row is information.

### 5. Hunt landmines

Check, with evidence:
- **Dependencies**: lockfile age, packages whose manifest version is far
  behind the ecosystem (Deep mode: check the registry), dependencies with
  no releases in years, duplicated libraries doing the same job.
- **Coverage gaps**: core modules (from step 3) with no corresponding
  tests. Name the module and the missing test area — "payments/ has no
  tests" is a landmine; "coverage is low" is not.
- **Generated vs hand-written**: generated files without headers, checked-in
  build output, vendored code that invites editing.
- **Hidden conventions**: codegen steps, required env files, "do not edit"
  headers, ordering dependencies, magic constants with no explanation.
- **Single points of failure**: the one file everything imports, the
  un-owned script in CI, the bus-factor-one subsystem (from git history:
  `git shortlog -sn` when available).

### 6. Choose the reading path

Five files, ordered so each makes the next readable: entry point → core
flow → central model/state → the trickiest module → the test that shows
intended behaviour. One line each: what this file teaches you.

### 7. Assemble and self-verify

- Write the report from `references/output-template.md` to
  `<repo>/REPO_XRAY.md` (for a cloned repo, alongside the clone if the user
  prefers the original untouched — default: in the repo root, it's the
  point of the pack).
- Run `scripts/verify_report.py <repo>/REPO_XRAY.md <repo>`: it checks the
  five sections exist, every backticked path in the report exists on disk,
  and every command block in "Run it" carries a VERIFIED/UNVERIFIED
  marker. Fix every complaint before delivering — do not argue with the
  checker.
- Deliver in chat: a five-line summary (what it is, how to run it, the
  scariest landmine, coverage) + where the pack was written.

## Large-repo strategy (>~5,000 code files)

- Inventory first; read manifests, CI, docs index, and entry points only.
- Follow reachability from entry points; read the modules on the main
  flows fully, sample the rest by largest-file and most-imported signals
  (`git log --name-only` frequency is a good importance proxy).
- Skip, and name as skipped: vendored code, generated code, fixtures,
  snapshot files, migrations history beyond the latest, asset pipelines.
- The coverage statement must give real numbers: files read in full /
  sampled / not opened, out of the counted total.

## Failure modes

| Situation | Do this |
|---|---|
| Install fails | Report the verbatim first error + your read of the cause as a landmine; mark downstream commands UNVERIFIED (blocked by install). |
| Tests fail out of the box | Report counts and the first failure; this is a headline finding, not a reason to stop. |
| Repo has no tests | Landmine #1, and the change index loses its "proving test" column entries — say so per row. |
| Repo has no README / docs | Say so; derive everything from code and CI, and lower confidence labels accordingly. |
| Needs a service (DB, queue…) | If a compose file or test container exists, use it; otherwise UNVERIFIED with the exact service and version the config expects. |
| Private repo you can't clone | Ask for a local path or an archive; do not reconstruct from the web page listing. |

## Quality bar (check before delivering)

- [ ] Every command in "Run it" was executed here, or is marked UNVERIFIED
      with a reason.
- [ ] `verify_report.py` passes: five sections, all cited paths exist.
- [ ] The diagram contains only modules you actually read or traced.
- [ ] Every landmine names evidence (a file, a version, a missing test).
- [ ] Coverage statement numbers come from the inventory, not from memory.
- [ ] Reading path is exactly 5 files, in an order a newcomer can follow.
- [ ] Nothing in the target repo changed except the added report.
