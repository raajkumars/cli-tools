"""Tests for csv_stats.py — uses stdlib unittest.

Fixtures: normal CSV, empty file, non-numeric columns, missing file,
header-only CSV, and single-row CSV.

Run with:
    python3 -m unittest discover -s tests
or with pytest when available.
"""

import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "csv_stats.py"


def run(path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), path],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Fixture helpers (written to a per-test temp dir via setUp)
# ---------------------------------------------------------------------------

import tempfile
import os


class _TmpDir(unittest.TestCase):
    """Base that provides self.tmp_path as a temporary directory."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()


# ---------------------------------------------------------------------------
# Fixture 1 — Normal CSV
# ---------------------------------------------------------------------------


class TestNormalCsv(_TmpDir):
    """A well-formed CSV: two numeric columns, one string column."""

    def setUp(self):
        super().setUp()
        f = self.tmp_path / "normal.csv"
        f.write_text(
            textwrap.dedent("""\
                name,age,score
                Alice,30,88.5
                Bob,25,92.0
                Carol,35,76.0
            """)
        )
        self.csv_path = str(f)

    def test_exit_code_zero(self):
        result = run(self.csv_path)
        self.assertEqual(result.returncode, 0)

    def test_row_count(self):
        result = run(self.csv_path)
        self.assertIn("Rows: 3", result.stdout)

    def test_column_names_present(self):
        result = run(self.csv_path)
        self.assertIn("name", result.stdout)
        self.assertIn("age", result.stdout)
        self.assertIn("score", result.stdout)

    def test_numeric_stats_section_printed(self):
        result = run(self.csv_path)
        self.assertIn("Numeric column stats:", result.stdout)

    def test_age_min(self):
        result = run(self.csv_path)
        self.assertIn("25", result.stdout)

    def test_age_max(self):
        result = run(self.csv_path)
        self.assertIn("35", result.stdout)

    def test_string_column_not_in_stats(self):
        """'name' must not appear as a numeric stat row."""
        result = run(self.csv_path)
        lines = result.stdout.splitlines()
        if "Numeric column stats:" in lines:
            idx = lines.index("Numeric column stats:")
            stat_lines = lines[idx + 1 :]
            col_names = [
                l.strip().split()[0]
                for l in stat_lines
                if l.strip() and "---" not in l and "Min" not in l
            ]
            self.assertNotIn("name", col_names)


# ---------------------------------------------------------------------------
# Fixture 2 — Empty file (zero bytes)
# ---------------------------------------------------------------------------


class TestEmptyFile(_TmpDir):
    """A completely empty file should exit non-zero with an error message."""

    def setUp(self):
        super().setUp()
        f = self.tmp_path / "empty.csv"
        f.write_text("")
        self.csv_path = str(f)

    def test_exit_non_zero(self):
        result = run(self.csv_path)
        self.assertNotEqual(result.returncode, 0)

    def test_error_message_present(self):
        result = run(self.csv_path)
        combined = result.stdout.lower() + result.stderr.lower()
        self.assertIn("error", combined)


# ---------------------------------------------------------------------------
# Fixture 3 — Non-numeric columns only
# ---------------------------------------------------------------------------


class TestNonNumericCsv(_TmpDir):
    """CSV with all-string columns — no numeric stats should be printed."""

    def setUp(self):
        super().setUp()
        f = self.tmp_path / "strings.csv"
        f.write_text(
            textwrap.dedent("""\
                city,country,continent
                Paris,France,Europe
                Tokyo,Japan,Asia
                Cairo,Egypt,Africa
            """)
        )
        self.csv_path = str(f)

    def test_exit_code_zero(self):
        result = run(self.csv_path)
        self.assertEqual(result.returncode, 0)

    def test_row_count(self):
        result = run(self.csv_path)
        self.assertIn("Rows: 3", result.stdout)

    def test_no_numeric_stats(self):
        result = run(self.csv_path)
        self.assertIn("no fully-numeric columns", result.stdout)

    def test_column_names_present(self):
        result = run(self.csv_path)
        for col in ("city", "country", "continent"):
            self.assertIn(col, result.stdout)


# ---------------------------------------------------------------------------
# Fixture 4 — Missing file
# ---------------------------------------------------------------------------


class TestMissingFile(_TmpDir):
    """A path that does not exist should exit non-zero with a clear message."""

    def setUp(self):
        super().setUp()
        self.csv_path = str(self.tmp_path / "does_not_exist.csv")

    def test_exit_non_zero(self):
        result = run(self.csv_path)
        self.assertNotEqual(result.returncode, 0)

    def test_error_message_contains_filename(self):
        result = run(self.csv_path)
        combined = result.stdout + result.stderr
        self.assertTrue(
            "does_not_exist" in combined or "not found" in combined,
            msg=f"Expected filename or 'not found' in output: {combined!r}",
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases(_TmpDir):
    def _write(self, name: str, content: str) -> str:
        f = self.tmp_path / name
        f.write_text(content)
        return str(f)

    def test_header_only_no_data_rows(self):
        path = self._write("header_only.csv", "a,b,c\n")
        result = run(path)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Rows: 0", result.stdout)
        self.assertIn("no data rows", result.stdout)

    def test_single_row_min_equals_max_equals_mean(self):
        path = self._write("single.csv", "x,y\n10,20\n")
        result = run(path)
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        x_line = next((l for l in lines if l.strip().startswith("x")), None)
        self.assertIsNotNone(x_line, msg="Expected a stat line for column 'x'")
        self.assertGreaterEqual(
            x_line.count("10"), 3, msg="min/max/mean should all be 10"
        )

    def test_no_args_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout.lower() + result.stderr.lower()
        self.assertIn("usage", combined)


if __name__ == "__main__":
    unittest.main()
