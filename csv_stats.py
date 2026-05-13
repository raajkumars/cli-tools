#!/usr/bin/env python3
"""csv_stats.py — Print row count, column names, and numeric column statistics.

Usage:
    python3 csv_stats.py <file.csv>

Exits non-zero on missing file or invalid CSV.
Stdlib only: csv, statistics.
"""

import csv
import statistics
import sys


def parse_csv(path: str) -> tuple[list[str], list[dict]]:
    """Read CSV and return (headers, rows). Raises on bad input."""
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or has no header row")
            headers = list(reader.fieldnames)
            rows = list(reader)
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")
    except PermissionError:
        raise SystemExit(f"error: permission denied: {path}")
    except csv.Error as exc:
        raise SystemExit(f"error: invalid CSV ({exc}): {path}")
    return headers, rows


def collect_numerics(headers: list[str], rows: list[dict]) -> dict[str, list[float]]:
    """Return a dict of column -> list of float values for columns that are fully numeric."""
    numeric: dict[str, list[float]] = {}
    for col in headers:
        values: list[float] = []
        for row in rows:
            raw = row.get(col, "").strip()
            try:
                values.append(float(raw))
            except ValueError:
                values = []
                break
        if values:
            numeric[col] = values
    return numeric


def format_stat(value: float) -> str:
    """Format a float cleanly — no trailing zeros for whole numbers."""
    return f"{value:g}" if value == int(value) else f"{value:.4f}"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 csv_stats.py <file.csv>")

    path = sys.argv[1]
    headers, rows = parse_csv(path)

    row_count = len(rows)
    print(f"Rows: {row_count}")
    print(f"Columns ({len(headers)}): {', '.join(headers)}")

    if row_count == 0:
        print("(no data rows — skipping numeric stats)")
        return

    numeric = collect_numerics(headers, rows)

    if not numeric:
        print("(no fully-numeric columns found)")
        return

    print("\nNumeric column stats:")
    col_w = max(len(c) for c in numeric)
    header_line = f"  {'Column':<{col_w}}  {'Min':>12}  {'Max':>12}  {'Mean':>12}"
    print(header_line)
    print("  " + "-" * (col_w + 42))
    for col, values in numeric.items():
        mn = format_stat(min(values))
        mx = format_stat(max(values))
        me = format_stat(statistics.mean(values))
        print(f"  {col:<{col_w}}  {mn:>12}  {mx:>12}  {me:>12}")


if __name__ == "__main__":
    main()
