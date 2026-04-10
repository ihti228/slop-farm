#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

DEFAULT_LOG_PATH = Path("tools/receipt-log/receipts.jsonl")
REQUIRED_FIELDS = ("timestamp", "agent", "action", "artifact", "summary")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_receipt_id(timestamp: str, agent: str, action: str, artifact: str, summary: str) -> str:
    payload = "\n".join([timestamp, agent, action, artifact, summary])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"rct_{digest}"


def build_receipt(
    agent: str,
    action: str,
    artifact: str,
    summary: str,
    source: str | None,
    session: str | None,
    host: str | None,
    parent_receipt: str | None,
) -> dict[str, Any]:
    timestamp = utc_now()
    receipt = {
        "receipt_id": make_receipt_id(timestamp, agent, action, artifact, summary),
        "timestamp": timestamp,
        "agent": agent,
        "action": action,
        "artifact": artifact,
        "summary": summary,
    }
    if source:
        receipt["source"] = source
    if session:
        receipt["session"] = session
    if host:
        receipt["host"] = host
    if parent_receipt:
        receipt["parent_receipt"] = parent_receipt
    return receipt


def append_receipt(
    log_path: Path,
    agent: str,
    action: str,
    artifact: str,
    summary: str,
    source: str | None,
    session: str | None,
    host: str | None,
    parent_receipt: str | None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    receipt = build_receipt(agent, action, artifact, summary, source, session, host, parent_receipt)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
    print(f"appended receipt {receipt['receipt_id']} to {log_path}")


def parse_receipts(log_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    receipts: list[dict[str, Any]] = []
    errors: list[str] = []

    if not log_path.exists():
        return receipts, errors

    with log_path.open("r", encoding="utf-8") as f:
        for i, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"[{i}] invalid json: {e}")
                continue
            if not isinstance(item, dict):
                errors.append(f"[{i}] expected object, got {type(item).__name__}")
                continue
            receipts.append(item)
    return receipts, errors


def validate_receipts(log_path: Path) -> int:
    if not log_path.exists():
        print(f"no receipts yet at {log_path}")
        return 0

    receipts, errors = parse_receipts(log_path)
    seen_ids: set[str] = set()

    for i, item in enumerate(receipts, start=1):
        missing = [field for field in REQUIRED_FIELDS if not item.get(field)]
        if missing:
            errors.append(f"[{i}] missing required fields: {', '.join(missing)}")

        receipt_id = item.get("receipt_id")
        if receipt_id:
            if receipt_id in seen_ids:
                errors.append(f"[{i}] duplicate receipt_id: {receipt_id}")
            seen_ids.add(receipt_id)

    if errors:
        print(f"validation failed for {log_path}", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"validated {len(receipts)} receipts in {log_path}")
    if receipts:
        with_ids = sum(1 for item in receipts if item.get("receipt_id"))
        with_source = sum(1 for item in receipts if item.get("source"))
        with_session = sum(1 for item in receipts if item.get("session"))
        with_host = sum(1 for item in receipts if item.get("host"))
        print(f"- receipt_id coverage: {with_ids}/{len(receipts)}")
        print(f"- source coverage:     {with_source}/{len(receipts)}")
        print(f"- session coverage:    {with_session}/{len(receipts)}")
        print(f"- host coverage:       {with_host}/{len(receipts)}")
    return 0


def list_receipts(log_path: Path) -> int:
    if not log_path.exists():
        print(f"no receipts yet at {log_path}")
        return 0

    receipts, errors = parse_receipts(log_path)
    for err in errors:
        print(err, file=sys.stderr)

    for i, item in enumerate(receipts, start=1):
        receipt_id = item.get("receipt_id", "-")
        print(f"[{i}] {item.get('timestamp')} | {item.get('agent')} | {item.get('action')} | {receipt_id}")
        print(f"    artifact: {item.get('artifact')}")
        print(f"    summary:  {item.get('summary')}")
        if item.get("source"):
            print(f"    source:   {item.get('source')}")
        if item.get("session"):
            print(f"    session:  {item.get('session')}")
        if item.get("host"):
            print(f"    host:     {item.get('host')}")
        if item.get("parent_receipt"):
            print(f"    parent:   {item.get('parent_receipt')}")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append-only collaboration receipt log")
    parser.add_argument("--log-path", default=str(DEFAULT_LOG_PATH), help="Path to JSONL receipt log")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Append a receipt")
    add_parser.add_argument("--agent", required=True)
    add_parser.add_argument("--action", required=True)
    add_parser.add_argument("--artifact", required=True)
    add_parser.add_argument("--summary", required=True)
    add_parser.add_argument("--source", help="Provenance for where this receipt came from (for example github_pr or local_run)")
    add_parser.add_argument("--session", help="Session or run identifier tied to this receipt")
    add_parser.add_argument("--host", help="Host or machine name where the action happened")
    add_parser.add_argument("--parent-receipt", help="Receipt ID this action extends or audits")

    subparsers.add_parser("list", help="List receipts")
    subparsers.add_parser("validate", help="Validate receipt log structure and provenance coverage")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    log_path = Path(args.log_path)

    if args.command == "add":
        append_receipt(
            log_path,
            args.agent,
            args.action,
            args.artifact,
            args.summary,
            args.source,
            args.session,
            args.host,
            args.parent_receipt,
        )
        return 0
    if args.command == "list":
        return list_receipts(log_path)
    if args.command == "validate":
        return validate_receipts(log_path)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
