# receipt-log/viewer

A standalone HTML timeline viewer for the receipt log.

Generates a single self-contained HTML file that renders receipts as a filterable,
sortable timeline — no server needed, no external dependencies.

## What it shows

- All receipts in chronological order
- Color-coded status dots: green (full provenance), yellow (partial), red (legacy)
- Filter buttons for each action type
- Full-text search across all receipt fields
- Provenance tags showing source, session, host, and parent receipt links
- Summary stats at the top: total receipts, agents, artifacts, provenance coverage %

## Usage

```bash
# From the repo root
python3 tools/receipt-log/viewer/build.py

# Custom paths
python3 tools/receipt-log/viewer/build.py path/to/receipts.jsonl output.html

# Then open the generated timeline.html in a browser
```

## Design notes

- **Single file output** — no CSS/JS assets to manage, just `timeline.html`
- **Dark mode** — matches the aesthetic of the broader Slop Farm project
- **Zero dependencies** — pure Python for build, vanilla HTML/CSS/JS for output
- **Append-only friendly** — re-run the builder any time the JSONL grows
- **Works offline** — no CDN links, no APIs, everything is self-contained

## Why this exists

Issue #10 asks for "a tiny renderer that turns the JSONL log into a readable timeline."
This is that renderer — small, real, and immediately usable by another agent or human
who wants to understand what happened in the log without reading raw JSONL.

## Future directions

- Link parent_receipt IDs to their anchor entries (clickable cross-references)
- Add time-range filtering (last 7 days, last 30 days)
- Export filtered subsets as new JSONL files
- Artifact-centric view (group all receipts for one artifact)