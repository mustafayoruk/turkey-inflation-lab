# Turkey Inflation Lab

Reproducible Turkish CPI forecasting research for economic analysis and decision support.

**Current finding:** a small Ridge model slightly improves development MAE over the trailing average, but performs worse than last-month persistence during 2020–2023. Model complexity alone does not resolve inflation shocks.

## The decision

After a CPI release, can historical monthly inflation improve a forecast of the next published monthly CPI change? The intended first user is an analyst preparing an economic brief. Later budgeting and BI integrations are hypotheses, not validated customer demand. Headline CPI is not a firm's procurement basket.

## Results

Expanding-origin development evaluation, January 2015–December 2023, 108 paired months. Errors are in **percentage points**, not percent relative error. The January 2024–September 2026 final holdout remains unscored.

| Method | MAE ↓ | RMSE ↓ | Bias |
|---|---:|---:|---:|
| Last month | 1.2427 | **1.9463** | -0.0312 |
| Same month last year | 1.5235 | 2.7079 | -0.4028 |
| Trailing 12-month mean | 1.1692 | 2.0740 | -0.2348 |
| Ridge, 12 monthly lags | **1.1397** | 2.2001 | -0.4880 |

Ridge reduces overall MAE by 2.5% versus the trailing mean, but has more negative bias and larger RMSE. In 2020–2023 its MAE is 1.7227 versus 1.6027 for last-month persistence. These are development comparisons, without a statistical-superiority or live-performance claim.

## Inspect the evidence

- [CPI observations — CSV](data/published/research-v1/snapshot/cpi.csv): 261 months, January 2005–September 2026; source: TÜİK via TCMB.
- [Paired predictions — CSV](data/published/research-v1/results/predictions.csv): 432 rows, 108 months × 4 methods.
- [Metrics by period — CSV](data/published/research-v1/results/metrics.csv): MAE, RMSE and bias, including two predeclared subperiods.
- [Ridge tuning — CSV](data/published/research-v1/results/tuning.csv): 540 origin/alpha records; unsuccessful candidates are retained.
- [CSV dictionary](docs/CSV-SOZLUGU.md), [file checksums](data/published/research-v1/checksums.json), [run environment and code hashes](data/published/research-v1/results/manifest.json).
- [Ridge experiment design](docs/DENEY-002.md), [baseline design](docs/DENEY-001.md), [research source register](.agents/skills/inflation-research/references/sources.md).

## Reproduce

Python 3.12.14 was used. Parsing uses only the standard library; modelling uses scikit-learn 1.7.2. Dependencies are pinned in requirements.txt. Use a fresh output directory for each run.

```bash
python -m venv .venv
# Activate .venv using your shell's activation command.
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/evaluate_baselines.py --snapshot data/published/research-v1/snapshot --contract configs/baseline-development-v1.json --output reports/runs/baseline-rerun
python scripts/evaluate_ridge.py --snapshot data/published/research-v1/snapshot --contract configs/ridge-development-v1.json --output reports/runs/ridge-rerun
```

To verify extraction from the exact preserved source bytes:

```bash
python scripts/prepare_cpi.py --input data/published/research-v1/snapshot/source.html --retrieved-at 2026-10-24T21:27:45Z --output data/processed/reparsed
python scripts/export_research.py --snapshot data/published/research-v1/snapshot --run reports/runs/ridge-rerun --output data/published/research-rerun
```

The example retrieval time describes the preserved snapshot. A new download needs its actual retrieval time. Generated timestamps/runtime can differ on rerun; predictions should agree within floating-point tolerance with the pinned environment.

## Method and limits

The model uses 12 lagged monthly rates, a training-only StandardScaler/Ridge pipeline and chronological inner validation over five fixed alpha values. Each outer origin refits on previous observations only. The design was recorded before Ridge results were calculated. All four methods share the same targets.

This is **latest-vintage pseudo-out-of-sample** evaluation. Exact historical release times and first-release vintages have not been reconstructed. Previous-month availability is an explicit assumption. The complete source CSV includes the holdout, but no current scores or model selection use that period; there is no cryptographic blinding. Source base-year labels are inconsistent across page metadata; incompatible index levels are not spliced.

Local verification: 25 unit tests passed, plus the real 108-origin experiment (1,728 Ridge fits, one worker). No cloud CI, dashboard, API, forecast interval, live forecast or commercial acceptance is claimed.

## Roadmap and product direction

Next: identify publication-aware economic inputs, declare the next experiment before fitting, then validate a compact analyst report. Currency, producer prices and expectations are candidate research inputs, subject to availability and reuse checks. A future budgeting integration requires a firm's cost weights and a suitable forecast horizon.

[Vision and integration hypotheses](docs/VIZYON.md) · [Progress](docs/TAKIP.md) · [Data limitations](docs/VERI.md) · [Release evidence](docs/YAYIM-TAKVIMI.md)

## License and attribution

Original code and documentation: [MIT License](LICENSE). Third-party CPI observations, source HTML and their reproduction in outputs are excluded from that grant: see [data terms](data/LICENSE.md) and [DATA-NOTICE.md](DATA-NOTICE.md). Source: TÜİK, reproduced by TCMB; retrieved 24 October 2026. TCMB requires written permission for commercial use. This repository is a noncommercial research portfolio and is not affiliated with either agency.

---

**Author:** [Mustafa YÖRÜK](https://github.com/mustafayoruk)  
*Statistics Student @ Hacettepe University*
