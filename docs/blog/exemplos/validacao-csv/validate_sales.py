"""Validate a small sales CSV without changing the source file (Python 3.11+)."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TextIO

FIELDS = ("sale_id", "date", "amount_brl")
MAX_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 100_000


def validate(stream: TextIO, *, delimiter: str = ",", decimal_separator: str = ".") -> dict:
    """Return diagnostics; record numbers exclude the header. No values are rewritten.

    All occurrences of a duplicated nonempty ID are flagged. A structurally
    malformed CSV stops processing and sets complete=False. Data rule errors do
    not stop inspection. This bounded, in-memory tutorial is not a large-file engine.
    """
    if delimiter not in (",", ";", "\t"):
        raise ValueError("Delimiter must be comma, semicolon or tab.")
    if decimal_separator not in (".", ","):
        raise ValueError("Decimal separator must be dot or comma.")
    issues: list[dict] = []
    records: list[tuple[int, int, str]] = []
    count = 0
    complete = True

    def issue(record: int, line: int, field: str, code: str, message: str) -> None:
        issues.append(dict(record=record, line_end=line, field=field, code=code, message=message))

    def result() -> dict:
        return {"valid": complete and not issues, "complete": complete,
                "records_checked": count, "issue_count": len(issues), "issues": issues}

    reader = csv.reader(stream, delimiter=delimiter, strict=True)
    amount_pattern = re.compile(r"-?[0-9]+(?:" + re.escape(decimal_separator) + r"[0-9]{1,2})?")
    try:
        header = next(reader, None)
        if header != list(FIELDS):
            issue(0, reader.line_num, "header", "schema", "Expected exactly: sale_id, date, amount_brl, in this order.")
            complete = False
            return result()
        for raw in reader:
            if count >= MAX_RECORDS:
                issue(count + 1, reader.line_num, "file", "record_limit", "Record limit exceeded; remaining records not checked.")
                complete = False
                break
            count += 1
            if len(raw) != len(FIELDS):
                issue(count, reader.line_num, "row", "column_count", "Expected three columns; record not checked further.")
                continue
            sale_id, sold_on, amount = (value.strip() for value in raw)
            records.append((count, reader.line_num, sale_id))
            if not sale_id:
                issue(count, reader.line_num, "sale_id", "required", "Sale ID is required.")
            if not sold_on:
                issue(count, reader.line_num, "date", "required", "Date is required.")
            else:
                try:
                    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", sold_on):
                        raise ValueError("format")
                    date.fromisoformat(sold_on)
                except ValueError:
                    issue(count, reader.line_num, "date", "invalid_date", "Use a real calendar date in YYYY-MM-DD format.")
            if not amount:
                issue(count, reader.line_num, "amount_brl", "required", "Amount is required.")
            elif not amount_pattern.fullmatch(amount):
                issue(count, reader.line_num, "amount_brl", "invalid_amount", "Use plain decimal notation, no thousands separator, and at most two decimal places.")
            elif Decimal(amount.replace(decimal_separator, ".")) <= 0:
                issue(count, reader.line_num, "amount_brl", "non_positive", "This example accepts positive paid sales only.")
    except csv.Error:
        issue(count + 1, reader.line_num, "file", "malformed_csv", "CSV parsing failed; remaining records not checked.")
        complete = False

    frequencies = Counter(sale_id for _, _, sale_id in records if sale_id)
    for record, line, sale_id in records:
        if sale_id and frequencies[sale_id] > 1:
            issue(record, line, "sale_id", "duplicate_id", "ID occurs more than once; all occurrences are flagged.")
    issues.sort(key=lambda item: (item["record"], item["field"], item["code"]))
    if count == 0 and complete:
        issue(0, reader.line_num, "file", "empty_dataset", "Expected at least one sales record.")
    return result()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--delimiter", choices=[",", ";", "\t"], default=",")
    parser.add_argument("--decimal-separator", choices=[".", ","], default=".")
    parser.add_argument("--output", type=Path, help="New JSON report path; existing files and links are never overwritten.")
    args = parser.parse_args(argv)
    try:
        source = args.csv_path.resolve()
        if args.output and args.output.resolve() == source:
            raise ValueError("Report path cannot overwrite the source CSV.")
        if not source.is_file():
            raise ValueError("Input must be an existing regular file.")
        if source.stat().st_size > MAX_BYTES:
            raise ValueError("Input exceeds the 10 MiB tutorial limit.")
        with source.open(encoding="utf-8-sig", newline="") as stream:
            report = validate(stream, delimiter=args.delimiter, decimal_separator=args.decimal_separator)
        report["source"] = source.name
        payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            # Exclusive creation also rejects hard links and dangling symlinks.
            # Checking only resolved path names cannot detect a hard-link alias.
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(payload)
        sys.stdout.write(payload)
        return 0 if report["valid"] else 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot validate file: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
