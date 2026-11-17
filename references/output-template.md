# REPO_XRAY.md — output template

Copy this skeleton into `<repo>/REPO_XRAY.md` and fill it from evidence.
Delete sections' placeholder text; keep the section order and headings —
predictability is the point. Every command block must be preceded by a
status line: `Status: VERIFIED — <what you observed>` or
`Status: UNVERIFIED — <reason>`.

---

```markdown
# X-Ray: <repo name>

- **Repository:** <path or URL> @ <short commit>
- **Scanned:** <YYYY-MM-DD> · **Mode:** Quick | Deep
- **Stack (observed):** <languages, frameworks, runtimes — from manifests>
- **Coverage:** Read in full: <N> files · Sampled: <N> · Not opened: <N>
  (<what was skipped and why>) · Total counted: <N> code files

## 1. Run it

### Install
Status: VERIFIED — <e.g. "completed in 40s, node v20.11">
​```
<command>
​```

### Run
Status: VERIFIED — <e.g. "listens on :8080, GET /health → 200">
​```
<command>
​```

### Test
Status: VERIFIED — <e.g. "41 passed, 3 failed; first failure: …">
​```
<command>
​```

## 2. Architecture

​```mermaid
flowchart LR
  A[<entry>] --> B[<core module>]
  B --> C[(<data store>)]
​```

<One page max. Entry points, main flow, core modules and what each owns,
data stores, external services. Only what was read or traced.>

## 3. Change index

| To change… | Touch | Prove it with |
|---|---|---|
| <intent> | `path/to/file` | `path/to/test` |

## 4. Landmines

1. **<short name>** — <what, where, and the evidence: file, version,
   missing test>. <What it costs the next person.>

## 5. Reading path

1. `path` — <what this file teaches you>
2. `path` — <…>
3. `path` — <…>
4. `path` — <…>
5. `path` — <…>
```

Notes for the filler:

- **Header numbers come from `scripts/inventory.py` output**, never from
  memory.
- "Run it" may add rows (Build, Migrate, Seed) when the repo has them, and
  must drop rows it doesn't (a library has no Run — say "library: no
  runnable entry point" instead of inventing one).
- The change index only lists intents this repo supports. Typical rows:
  add an endpoint/page, change auth, add or change a data model, change
  configuration, add a background job/CLI command, change the build.
- A landmine without evidence doesn't make the list. "Few tests" is not a
  landmine; "`src/billing/` (named core in §2) has no test files" is.
- Reading path: entry point first, tests last is a good default shape.
