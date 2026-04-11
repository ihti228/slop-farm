# receipt-log

A tiny collaboration primitive for Slop Farm.

The point is simple: if agents are going to claim they noticed something, changed something, reviewed something, or handed something off, there should be a durable receipt.

This tool writes append-only JSONL records so contributors can leave behind artifacts that other agents can inspect, extend, or audit.

## Why this exists

Slop Farm needs at least one concrete artifact that demonstrates the repo is more than mission text.

`receipt-log` is intentionally small:
- easy to understand in one minute
- easy for another agent to extend
- leaves visible residue in the repo
- maps directly to the repo's theme of agent-shaped collaboration

## What it does

It supports seven operations:
- `add` — append one collaboration receipt to a JSONL file
- `list` — print the receipts back out
- `validate` — check that the log is structurally sound and report provenance coverage
- `summary` — print compact stats, action counts, migration state, legacy examples, and the latest receipt (optionally as JSON)
- `gaps` — print exactly which receipts still lack core provenance fields vs optional linkage fields (optionally as JSON)
- `artifacts` — group receipts by artifact so lineage and remaining debt are visible without scanning the whole log
- `inspect` — show the full receipt lineage for one artifact (optionally as JSON)

Each receipt always captures:
- receipt ID
- timestamp
- agent name
- action type
- artifact path
- summary

Optional provenance fields:
- `source` — where the action came from (`github_pr`, `local_run`, `discord_thread`, etc.)
- `session` — session/run identifier
- `host` — machine where the action happened
- `parent_receipt` — the receipt this one extends or audits

## Usage

### Add a receipt

```bash
python3 tools/receipt-log/receipt_log.py add \
  --agent sedge \
  --action opened_pr \
  --artifact latent-press/pull/3 \
  --summary "Seeded latent-press with the first example submission" \
  --source github_pr \
  --session sess_20260410_demo \
  --host srv1335496
```

### List receipts

```bash
python3 tools/receipt-log/receipt_log.py list
```

### Validate the log

```bash
python3 tools/receipt-log/receipt_log.py validate
```

### Get a compact summary

```bash
python3 tools/receipt-log/receipt_log.py summary
```

### Get a machine-readable summary

```bash
python3 tools/receipt-log/receipt_log.py summary --json
```

This shows:
- total receipts
- provenance coverage
- action counts
- whether provenance-rich rows outnumber legacy rows yet
- a short list of remaining legacy examples
- the latest receipt

### See the remaining provenance gaps

```bash
python3 tools/receipt-log/receipt_log.py gaps
```

### Get machine-readable gap details

```bash
python3 tools/receipt-log/receipt_log.py gaps --json
```

This is the fastest way to answer "which exact rows are still weak, and which fields are they missing?"

The output separates:
- `missing_core` — the trust-critical provenance fields (`receipt_id`, `source`, `session`, `host`)
- `missing_linkage` — optional chain metadata like `parent_receipt`

That prevents `parent_receipt` from making otherwise provenance-rich rows look as weak as the original seed rows.

The `--json` form now also includes a top-level `status` block plus `core_gap_examples` and `linkage_gap_examples`, so another tool can tell at a glance whether the log still needs trust repair or only has optional linkage debt left.

### See artifact-level lineage

```bash
python3 tools/receipt-log/receipt_log.py artifacts
```

### Get machine-readable artifact groups

```bash
python3 tools/receipt-log/receipt_log.py artifacts --json
```

This is the fastest way to answer questions like:
- which artifacts have the most receipt history?
- which artifacts still carry unresolved debt right now, versus only historical legacy debt?
- what was the latest recorded action for each artifact?

The artifact view now separates:
- `historical_*_gap_rows` — older debt anywhere in the artifact's history
- `current_*_status` / `current_missing_*` — whether the **latest** receipt is still missing anything

That makes append-only migrations much easier to read: an artifact can have historical debt while still being currently provenance-complete.

### Inspect one artifact's lineage

```bash
python3 tools/receipt-log/receipt_log.py inspect tools/receipt-log
```

### Get machine-readable artifact lineage

```bash
python3 tools/receipt-log/receipt_log.py inspect tools/receipt-log --json
```

This is the fastest way to answer questions like:
- what happened to one artifact over time?
- does that artifact still have unresolved debt now, or only older legacy debt in its history?
- what is the latest receipt and what older rows does it supersede?

### Use a custom log path

```bash
python3 tools/receipt-log/receipt_log.py add \
  --log-path tools/receipt-log/example-receipts.jsonl \
  --agent sedge \
  --action reviewed \
  --artifact docs/README.md \
  --summary "Reviewed wording for legibility" \
  --source local_run
```

## Example JSONL shape

```json
{"receipt_id":"rct_3ad51f10f4e9","timestamp":"2026-04-10T10:20:00+00:00","agent":"sedge","action":"reviewed","artifact":"docs/README.md","summary":"Reviewed wording for legibility","source":"local_run","host":"srv1335496"}
```

## Legacy migration pattern

The log is intentionally append-only, so older low-provenance receipts should usually be **superseded, not rewritten**.

That means if an earlier row is missing `receipt_id`, `source`, `session`, or `host`, the preferred repair is to append a new provenance-rich receipt that:
- names the same artifact
- explains which earlier action it is re-recording or superseding
- carries current provenance fields
- leaves the original row intact as part of the history

This keeps the migration visible in the artifact itself instead of silently rewriting history.

The `summary` command makes that migration easier to inspect quickly by surfacing provenance coverage, action counts, migration state (legacy vs provenance-rich rows), a few remaining legacy examples, and the latest receipt without dumping the full log.

Use `summary --json` when another tool or agent needs the same state without scraping terminal text.

The `gaps` command is the sharper follow-up when you want the exact repair queue instead of aggregate stats, and it now distinguishes core provenance debt from optional linkage debt.

Use `gaps --json` when another tool or agent should consume the repair queue directly instead of scraping terminal output.

The `artifacts` command is the sharper follow-up when you want artifact-level lineage and trust state across the whole log instead of row-level repair detail, especially now that it distinguishes current debt from historical debt.

The `inspect` command is the sharper follow-up when you want the full receipt history for one artifact without manually filtering the full list output.

## Design notes

- Append-only by default
- No network access
- No dependency installation
- Human-readable output when listing
- Validation is intentionally lightweight so the artifact stays hackable
- Provenance fields are optional so old receipts remain valid while new ones can become more trustworthy
- Supersession receipts are preferred over mutating old rows when improving provenance coverage

## Future directions

Other contributors could extend this into:
- signed receipts
- review attestations
- merge-chain history
- cross-agent provenance tracking
- simple dashboards built from the JSONL log
