"""Validate a saved TCMB CPI table and produce a local, auditable snapshot."""
import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

SOURCE = "https://tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Main%2BMenu/Istatistikler/Enflasyon%2BVerileri"
HEADERS = ("Ay-Yıl", "TÜFE (Yıllık % Değişim)", "TÜFE (Aylık % Değişim)")
MAX_BYTES = 2 * 1024 * 1024


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if self.table is not None:
                raise ValueError("Nested tables are not supported.")
            self.table = []
        elif self.table is not None:
            if tag == "tr":
                self.row = []
            elif tag in ("td", "th"):
                self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            if self.row is None:
                raise ValueError("Cell outside a row.")
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.cell is not None:
                raise ValueError("Unclosed table cell.")
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            if self.row is not None:
                raise ValueError("Unclosed table row.")
            self.tables.append(self.table)
            self.table = None


def parse_rate(value):
    if len(value) > 32 or not re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", value):
        raise ValueError("Invalid percentage value.")
    number = Decimal(value.replace(",", "."))
    if not number.is_finite() or number <= -100:
        raise ValueError("CPI percentage change must be finite and greater than -100.")
    return format(number, "f")


def parse_cpi(html):
    if len(html.encode("utf-8")) > MAX_BYTES:
        raise ValueError("HTML exceeds the input limit.")
    parser = TableParser()
    parser.feed(html)
    parser.close()
    if parser.table is not None:
        raise ValueError("Unclosed table.")
    candidates = []
    for table in parser.tables:
        for index, row in enumerate(table):
            if len(row) == 3 and set(row) == set(HEADERS):
                candidates.append((row, table[index + 1:]))
                break
    if len(candidates) != 1:
        raise ValueError("Expected exactly one CPI table with the required headers.")
    header, body = candidates[0]
    positions = [header.index(name) for name in HEADERS]
    records = {}
    for row in body:
        if not row:
            continue
        if len(row) != 3:
            raise ValueError("Unexpected CPI row width.")
        period, annual, monthly = [row[index] for index in positions]
        if not re.fullmatch(r"\d{2}-\d{4}", period):
            raise ValueError("Expected an MM-YYYY reference period.")
        date = datetime.strptime(period, "%m-%Y")
        key = date.strftime("%Y-%m")
        if key in records:
            raise ValueError("Duplicate observation period: " + key)
        records[key] = {
            "observation_period": key,
            "annual_pct": parse_rate(annual),
            "monthly_pct": parse_rate(monthly),
        }
    if not records:
        raise ValueError("CPI table has no observations.")
    ordered = [records[key] for key in sorted(records)]
    months = [int(row["observation_period"][:4]) * 12
              + int(row["observation_period"][5:]) for row in ordered]
    if any(right - left != 1 for left, right in zip(months, months[1:])):
        raise ValueError("Missing observation month.")
    return ordered


def prepare_snapshot(source, output, retrieved_at):
    retrieved = datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
    if retrieved.tzinfo is None or retrieved.utcoffset() is None:
        raise ValueError("retrieved-at must include a timezone.")
    if retrieved > datetime.now(timezone.utc):
        raise ValueError("retrieved-at cannot be in the future.")
    with source.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("HTML exceeds the input limit.")
    rows = parse_cpi(raw.decode("utf-8-sig"))
    quality = {
        "status": "passed",
        "observations": len(rows),
        "first_period": rows[0]["observation_period"],
        "last_period": rows[-1]["observation_period"],
        "duplicate_periods": 0,
        "missing_months": 0,
        "negative_monthly_rates": sum(Decimal(row["monthly_pct"]) < 0 for row in rows),
        "release_timestamps_verified": False,
        "historical_vintages_available": False,
        "limitations": [
            "Snapshot of current table, not a historical point-in-time dataset.",
            "Header/base-year and HTML summary discrepancy requires metadata review.",
            "Public redistribution terms have not been verified.",
        ],
    }
    manifest = {
        "source_url": SOURCE,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "retrieved_at": retrieved.isoformat(),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "parser_version": "1",
        "python_version": sys.version.split()[0],
        "vintage_status": "latest-vintage-only",
        "released_at": None,
        "target": "monthly_pct",
        "unit": "percent change; forecast errors will be percentage points",
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "source.html").write_bytes(raw)
    with (output / "cpi.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "quality.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Write the manifest last; consumers must require it before using a snapshot.
    manifest["cpi_sha256"] = hashlib.sha256((output / "cpi.csv").read_bytes()).hexdigest()
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return quality


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--retrieved-at", required=True)
    args = parser.parse_args()
    try:
        quality = prepare_snapshot(args.input, args.output, args.retrieved_at)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, "Preparation failed: " + str(exc) + "\n")
    print(json.dumps(quality, ensure_ascii=False))


if __name__ == "__main__":
    main()
