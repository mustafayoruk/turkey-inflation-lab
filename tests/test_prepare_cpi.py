import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_cpi import HEADERS, MAX_BYTES, parse_cpi, prepare_snapshot


def table(rows, headers=HEADERS):
    header = "<tr>" + "".join("<th>" + cell + "</th>" for cell in headers) + "</tr>"
    body = "".join("<tr>" + "".join("<td>" + cell + "</td>" for cell in row) + "</tr>"
                   for row in rows)
    return "<table><thead>" + header + "</thead><tbody>" + body + "</tbody></table>"


TEST_TMP = Path(__file__).resolve().parents[1] / 'work' / 'test-tmp'
TEST_TMP.mkdir(parents=True, exist_ok=True)


class CPIContractTests(unittest.TestCase):
    def test_reference_months_sorted_and_negative_rates_preserved(self):
        html = table([("02-2025", "40.0", "-0,25"), ("01-2025", "42.0", "5.03")])
        rows = parse_cpi(html)
        self.assertEqual([r["observation_period"] for r in rows], ["2025-01", "2025-02"])
        self.assertEqual(rows[1]["monthly_pct"], "-0.25")

    def test_semantic_headers_prevent_annual_monthly_swap(self):
        headers = (HEADERS[0], HEADERS[2], HEADERS[1])
        rows = parse_cpi(table([("01-2025", "5.03", "42.0")], headers))
        self.assertEqual(rows[0]["monthly_pct"], "5.03")
        self.assertEqual(rows[0]["annual_pct"], "42.0")

    def test_duplicate_month_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            parse_cpi(table([("01-2025", "42", "5"), ("01-2025", "42", "5")]))

    def test_missing_month_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            parse_cpi(table([("01-2025", "42", "5"), ("03-2025", "38", "2")]))

    def test_invalid_rates_and_dates_rejected(self):
        for rate in ("NaN", "inf", "1e3", "", "-100", "<script>x</script>"):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                parse_cpi(table([("01-2025", "42", rate)]))
        for date in ("13-2025", "01-0000", "2025-01"):
            with self.subTest(date=date), self.assertRaises(ValueError):
                parse_cpi(table([(date, "42", "5")]))

    def test_empty_ambiguous_and_changed_schema_rejected(self):
        good = table([("01-2025", "42", "5")])
        for html in ("", table([]), good + good, good.replace(HEADERS[2], "unknown")):
            with self.subTest(html=html), self.assertRaises(ValueError):
                parse_cpi(html)

    def test_oversized_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "limit"):
            parse_cpi(" " * (MAX_BYTES + 1))

    def test_snapshot_provenance_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
            root = Path(folder)
            source = root / "input.html"
            raw = table([("01-2025", "42", "5")]).encode("utf-8")
            source.write_bytes(raw)
            output = root / "snapshot"
            quality = prepare_snapshot(source, output, "2025-02-01T12:00:00Z")
            self.assertEqual(quality["observations"], 1)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["source_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertIsNone(manifest["released_at"])
            self.assertEqual(manifest["vintage_status"], "latest-vintage-only")
            self.assertEqual((output / "source.html").read_bytes(), raw)
            with (output / "cpi.csv").open(newline="") as handle:
                self.assertEqual(next(csv.DictReader(handle))["monthly_pct"], "5")
            with self.assertRaises(FileExistsError):
                prepare_snapshot(source, output, "2025-02-01T12:00:00Z")

    def test_bad_retrieval_time_does_not_write_output(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
            root = Path(folder)
            source = root / "input.html"
            source.write_text(table([("01-2025", "42", "5")]), encoding="utf-8")
            for value in ("2025-02-01", "2099-01-01T00:00:00Z"):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    prepare_snapshot(source, root / "snapshot", value)
            self.assertFalse((root / "snapshot").exists())


if __name__ == "__main__":
    unittest.main()
