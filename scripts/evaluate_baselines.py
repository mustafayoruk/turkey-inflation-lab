"""Run the declared development-only CPI baseline comparison."""
import argparse
import csv
import hashlib
import io
import json
import math
import platform
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from prepare_cpi import SOURCE, parse_rate

METHODS = ("naive", "seasonal_naive", "trailing_mean_12")
LIMIT = 2 * 1024 * 1024


def month_number(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}", value):
        raise ValueError("Expected a YYYY-MM period.")
    parsed = datetime.strptime(value, "%Y-%m")
    return parsed.year * 12 + parsed.month


def validate_protocol(protocol):
    if protocol["target"] != "monthly_pct" or protocol["primary_metric"] != "MAE":
        raise ValueError("This runner implements monthly CPI and primary MAE only.")
    if protocol["evaluation_mode"] != "latest-vintage-pseudo-out-of-sample":
        raise ValueError("This snapshot cannot support real-time claims.")
    if protocol["methods"] != list(METHODS):
        raise ValueError("The declared three baselines must be evaluated together.")
    names = ("initial_training_start", "initial_training_end", "development_start",
             "development_end", "final_holdout_start", "final_holdout_end")
    start, train_end, dev_start, dev_end, final_start, final_end = [
        month_number(protocol[key]) for key in names]
    if not (train_end - start >= 11 and dev_start == train_end + 1
            and dev_end >= dev_start and final_start == dev_end + 1
            and final_end >= final_start):
        raise ValueError("Training, development and holdout periods must be consecutive.")
    covered = []
    for segment in protocol["subperiods"]:
        left, right = month_number(segment["start"]), month_number(segment["end"])
        if not dev_start <= left <= right <= dev_end:
            raise ValueError("Subperiod is outside development.")
        covered.extend(range(left, right + 1))
    if sorted(covered) != list(range(dev_start, dev_end + 1)):
        raise ValueError("Subperiods must partition development without gaps or overlap.")


def read_limited(path):
    with path.open("rb") as handle:
        data = handle.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("Input exceeds size limit.")
    return data


def load_snapshot(snapshot, protocol):
    manifest = json.loads(read_limited(snapshot / "manifest.json"))
    raw_csv = read_limited(snapshot / "cpi.csv")
    digest = hashlib.sha256(raw_csv).hexdigest()
    if digest != manifest["cpi_sha256"] or digest != protocol["expected_csv_sha256"]:
        raise ValueError("CSV hash does not match the snapshot and declared protocol.")
    raw_source = read_limited(snapshot / "source.html")
    if hashlib.sha256(raw_source).hexdigest() != manifest["source_sha256"]:
        raise ValueError("Source snapshot hash mismatch.")
    if manifest["source_url"] != SOURCE or manifest["vintage_status"] != "latest-vintage-only":
        raise ValueError("Unsupported source or vintage status.")
    reader = csv.DictReader(io.StringIO(raw_csv.decode("utf-8")))
    if reader.fieldnames != ["observation_period", "annual_pct", "monthly_pct"]:
        raise ValueError("Unexpected CSV schema.")
    rows = []
    previous = None
    for row in reader:
        period = row["observation_period"]
        number = month_number(period)
        if previous is not None and number != previous + 1:
            raise ValueError("Snapshot periods must be sorted, unique and contiguous.")
        previous = number
        value = float(parse_rate(row["monthly_pct"]))
        rows.append({"period": period, "monthly_pct": value})
    if (not rows or rows[0]["period"] != protocol["initial_training_start"]
            or rows[-1]["period"] != protocol["final_holdout_end"]):
        raise ValueError("Snapshot coverage does not match the declared experiment.")
    return rows, manifest


def predict(history):
    if len(history) < 12 or any(not math.isfinite(value) for value in history):
        raise ValueError("At least 12 finite historical observations are required.")
    return {
        "naive": history[-1],
        "seasonal_naive": history[-12],
        "trailing_mean_12": math.fsum(history[-12:]) / 12,
    }


def walk_forward(rows, protocol):
    periods = [row["period"] for row in rows]
    left = periods.index(protocol["development_start"])
    right = periods.index(protocol["development_end"])
    if left < 12:
        raise ValueError("Not enough pre-development history.")
    predictions = []
    for index in range(left, right + 1):
        history = [row["monthly_pct"] for row in rows[:index]]
        forecasts = predict(history)
        for method in METHODS:
            predictions.append({
                "target_period": rows[index]["period"],
                "origin_period": rows[index - 1]["period"],
                "method": method,
                "actual": rows[index]["monthly_pct"],
                "prediction": forecasts[method],
                "error": forecasts[method] - rows[index]["monthly_pct"],
            })
    return predictions


def summarize(predictions, subperiods, methods=METHODS):
    segments = [{"name": "all_development", "start": predictions[0]["target_period"],
                 "end": predictions[-1]["target_period"]}] + subperiods
    results = []
    for segment in segments:
        for method in methods:
            errors = [row["error"] for row in predictions if row["method"] == method
                      and segment["start"] <= row["target_period"] <= segment["end"]]
            if not errors:
                raise ValueError("Empty evaluation segment.")
            results.append({
                "segment": segment["name"], "method": method, "n": len(errors),
                "mae": math.fsum(abs(error) for error in errors) / len(errors),
                "rmse": math.sqrt(math.fsum(error * error for error in errors) / len(errors)),
                "bias": math.fsum(errors) / len(errors),
            })
    return results


def report_markdown(protocol, results):
    lines = [
        "# İlk tahmin karşılaştırması — geliştirme dönemi", "",
        "## Karar ihtiyacı",
        "Karmaşık model için referans hata düzeyini belirlemek. Bu sonuçlar ürün veya nihai test kabulü değildir.", "",
        "## Önceden belirlenen tasarım",
        "- İlk tarihçe: " + protocol["initial_training_start"] + "–" + protocol["initial_training_end"],
        "- Geliştirme: " + protocol["development_start"] + "–" + protocol["development_end"],
        "- Ayrılmış nihai dönem: " + protocol["final_holdout_start"] + "–"
        + protocol["final_holdout_end"] + "; skorlanmadı.",
        "- Hedef: bir sonraki aylık TÜFE yüzde değişimi; hata birimi yüzde puan.",
        "- Birincil ölçüt MAE; RMSE büyük hatalara duyarlılık, bias ise tahmin−gerçekleşen ortalaması.", "",
        "## Sonuçlar",
        "| Dönem | Yöntem | Ay | MAE | RMSE | Bias |",
        "|---|---|---:|---:|---:|---:|",
    ]
    labels = {"naive": "Son ay", "seasonal_naive": "Geçen yıl aynı ay",
              "trailing_mean_12": "Son 12 ay ortalaması"}
    for row in results:
        segment = str(row["segment"]).replace("|", " ").replace("\n", " ")
        lines.append(f"| {segment} | {labels[row['method']]} | {row['n']} | "
                     f"{row['mae']:.4f} | {row['rmse']:.4f} | {row['bias']:.4f} |")
    overall = [row for row in results if row["segment"] == "all_development"]
    best = min(overall, key=lambda row: row["mae"])
    lines += [
        "", "## Ekonomik yorum",
        f"Geliştirme MAE'si en düşük geçici referans: {labels[best['method']]}.",
        "Alt dönemler takvim bölmeleridir; otomatik ekonomik rejim sınıflandırması değildir.",
        "Yöntem sıralamasının değişmesi, tek ortalama skorun yanında dönem duyarlılığına bakmayı gerektirir.",
        "İstatistiksel anlamlılık veya gelecekte üstünlük iddiası kurulmadı.", "",
        "## Kullanım ve sınırlar",
        "Bu deney güncel veri sürümüyle zaman sıralı geliştirme değerlendirmesidir "
        "(latest-vintage pseudo-out-of-sample). Tarihsel yayım saatleri ve revizyonlar doğrulanmadı.",
        "Her origin'de önceki ayın TÜFE'sinin bilindiği varsayıldı; gerçek yayım zamanı uydurulmadı.",
        "Nihai dönemin hedefleri skorlanmadı, tarihçeye alınmadı ve yöntem seçimi için kullanılmadı.",
        "Kurumsal bütçe veya satın alma kararına doğrudan uygulanmış sonuç yok.",
        "Sıradaki kabul: aynı geliştirme origin'lerinde küçük bir Ridge modeli; nihai test ayrı tutulacak.",
    ]
    return "\n".join(lines) + "\n"


def run(snapshot, contract_path, output):
    started = time.perf_counter()
    raw_contract = read_limited(contract_path)
    protocol = json.loads(raw_contract)
    validate_protocol(protocol)
    rows, source = load_snapshot(snapshot, protocol)
    predictions = walk_forward(rows, protocol)
    results = summarize(predictions, protocol["subperiods"])
    manifest = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": hashlib.sha256(raw_contract).hexdigest(),
        "source_csv_sha256": source["cpi_sha256"],
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": platform.python_version(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluation_mode": protocol["evaluation_mode"],
        "holdout_scored": False,
        "elapsed_compute_seconds": time.perf_counter() - started,
        "methods": list(METHODS),
    }
    output.mkdir(parents=True, exist_ok=False)
    with (output / "predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    (output / "metrics.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "report.md").write_text(report_markdown(protocol, results), encoding="utf-8")
    (output / "protocol.json").write_bytes(raw_contract)
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.snapshot, args.contract, args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, "Baseline run failed: " + str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
