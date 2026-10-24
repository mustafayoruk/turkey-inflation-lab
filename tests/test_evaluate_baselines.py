import copy
import csv
import hashlib
import io
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_baselines import (METHODS, load_snapshot, predict, run, summarize,
                                validate_protocol, walk_forward)
from prepare_cpi import SOURCE

TMP = Path(__file__).resolve().parents[1] / "work" / "baseline-tests"
TMP.mkdir(parents=True, exist_ok=True)


def rows():
    return [{"period": f"{2020 + index // 12:04d}-{index % 12 + 1:02d}",
             "monthly_pct": float(index + 1)} for index in range(30)]


def contract():
    return {
        "protocol_id": "synthetic-test", "target": "monthly_pct",
        "primary_metric": "MAE", "methods": list(METHODS),
        "evaluation_mode": "latest-vintage-pseudo-out-of-sample",
        "initial_training_start": "2020-01", "initial_training_end": "2020-12",
        "development_start": "2021-01", "development_end": "2021-12",
        "final_holdout_start": "2022-01", "final_holdout_end": "2022-06",
        "subperiods": [{"name": "first", "start": "2021-01", "end": "2021-06"},
                       {"name": "second", "start": "2021-07", "end": "2021-12"}],
    }


def snapshot(root, protocol):
    folder = root / "source"
    folder.mkdir()
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["observation_period", "annual_pct", "monthly_pct"])
    for row in rows():
        writer.writerow([row["period"], "0", row["monthly_pct"]])
    data = stream.getvalue().encode()
    raw = b"synthetic source, not official CPI data"
    digest = hashlib.sha256(data).hexdigest()
    protocol["expected_csv_sha256"] = digest
    (folder / "cpi.csv").write_bytes(data)
    (folder / "source.html").write_bytes(raw)
    manifest = {"source_url": SOURCE, "vintage_status": "latest-vintage-only",
                "cpi_sha256": digest, "source_sha256": hashlib.sha256(raw).hexdigest()}
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    path = root / "protocol.json"
    path.write_text(json.dumps(protocol), encoding="utf-8")
    return folder, path


class BaselineTests(unittest.TestCase):
    def test_hand_calculated_forecasts_and_first_origin(self):
        self.assertEqual(predict(list(range(1, 13))),
                         {"naive": 12, "seasonal_naive": 1, "trailing_mean_12": 6.5})
        forecasts = walk_forward(rows(), contract())
        self.assertEqual(len(forecasts), 36)
        self.assertEqual(forecasts[0]["target_period"], "2021-01")
        self.assertEqual(forecasts[0]["origin_period"], "2020-12")
        self.assertEqual(forecasts[0]["prediction"], 12)
        self.assertEqual(forecasts[0]["actual"], 13)

    def test_future_observation_does_not_change_earlier_predictions(self):
        original = rows()
        modified = copy.deepcopy(original)
        modified[20]["monthly_pct"] = 9999
        before = walk_forward(original, contract())
        after = walk_forward(modified, contract())
        before = [r for r in before if r["target_period"] < "2021-09"]
        after = [r for r in after if r["target_period"] < "2021-09"]
        self.assertEqual(before, after)

    def test_current_target_is_not_in_its_own_predictors(self):
        modified = rows()
        modified[12]["monthly_pct"] = -99
        original = walk_forward(rows(), contract())[:3]
        changed = walk_forward(modified, contract())[:3]
        self.assertEqual([r["prediction"] for r in original],
                         [r["prediction"] for r in changed])

    def test_holdout_values_have_no_effect_on_development(self):
        modified = rows()
        for row in modified[24:]:
            row["monthly_pct"] = 99999
        self.assertEqual(walk_forward(rows(), contract()), walk_forward(modified, contract()))
        self.assertTrue(all(r["target_period"] < "2022-01"
                            for r in walk_forward(modified, contract())))

    def test_metrics_match_independent_arithmetic(self):
        predictions = [{"method": method, "target_period": f"2021-{index + 1:02d}",
                        "error": error}
                       for index, error in enumerate([-1, 2, -3]) for method in METHODS]
        results = summarize(predictions, [])
        for row in results:
            self.assertEqual(row["n"], 3)
            self.assertAlmostEqual(row["mae"], 2)
            self.assertAlmostEqual(row["rmse"], math.sqrt(14 / 3))
            self.assertAlmostEqual(row["bias"], -2 / 3)

    def test_invalid_protocol_boundaries_and_real_time_claim_rejected(self):
        for key, value in [("final_holdout_start", "2021-12"),
                           ("development_start", "2021-02"),
                           ("evaluation_mode", "real-time"),
                           ("methods", ["naive"])]:
            protocol = contract()
            protocol[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_protocol(protocol)
        protocol = contract()
        protocol["subperiods"][1]["start"] = "2021-06"
        with self.assertRaises(ValueError):
            validate_protocol(protocol)

    def test_short_or_nonfinite_history_rejected(self):
        for history in ([1] * 11, [float("nan")] * 12, [float("inf")] * 12):
            with self.assertRaises(ValueError):
                predict(history)

    def test_snapshot_tampering_rejected_before_outputs(self):
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            root = Path(tmp)
            protocol = contract()
            folder, path = snapshot(root, protocol)
            with (folder / "cpi.csv").open("ab") as handle:
                handle.write(b"\n")
            with self.assertRaisesRegex(ValueError, "hash"):
                run(folder, path, root / "output")
            self.assertFalse((root / "output").exists())

    def test_source_tampering_rejected(self):
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            root = Path(tmp)
            protocol = contract()
            folder, _ = snapshot(root, protocol)
            (folder / "source.html").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Source"):
                load_snapshot(folder, protocol)

    def test_end_to_end_manifest_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            root = Path(tmp)
            protocol = contract()
            folder, path = snapshot(root, protocol)
            output = root / "output"
            result = run(folder, path, output)
            self.assertEqual(len(result), 9)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertFalse(manifest["holdout_scored"])
            self.assertEqual(manifest["protocol_sha256"],
                             hashlib.sha256(path.read_bytes()).hexdigest())
            with (output / "predictions.csv").open() as handle:
                predictions = list(csv.DictReader(handle))
            self.assertEqual(len(predictions), 36)
            self.assertEqual(max(r["target_period"] for r in predictions), "2021-12")
            self.assertEqual((output / "protocol.json").read_bytes(), path.read_bytes())
            with self.assertRaises(FileExistsError):
                run(folder, path, output)


if __name__ == "__main__":
    unittest.main()
