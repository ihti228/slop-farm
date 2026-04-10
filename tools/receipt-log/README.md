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

It supports three operations:
- `add` — append one collaboration receipt to a JSONL file
- `list` — print the receipts back out
- `validate` — check that the log is structurally sound and report provenance coverage

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
