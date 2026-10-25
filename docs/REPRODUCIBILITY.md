# Reproduction and validation

## Run as a single notebook in Google Colab

Open the badge above, then choose **Runtime → Run all** on a CPU runtime. Or download [turkey_inflation_lab.ipynb](notebooks/turkey_inflation_lab.ipynb) and upload that single file to Colab/Jupyter.

The notebook embeds the frozen source snapshot, CSV data, declared protocol, analysis code and reference outputs. No repository clone, separate CSV upload, Drive mount or GitHub token is needed. Package installation may require internet and a session restart; Python 3.12.14 was used locally. This is the saved research snapshot, not an automatically refreshed data feed. Its input data retains the agency terms in DATA-NOTICE.md; it is not all covered by MIT.

It covers source validation, all four methods, period metrics, economic interpretation and CSV/ZIP export. The nine code cells were executed sequentially in a fresh local Python namespace, all 432 predictions matched the published study within 1e-10 tolerance, and the notebook passed nbformat 5.10.4 validation. Saved outputs are from that local run. Hosted acceptance on 25 October 2026: CPU runtime, Python 3.13.16, the same pinned dependencies; after installation and one session restart, Run all completed, all 432 predictions matched the reference, and the CSV/manifest ZIP was generated. If installation requests a restart, choose Runtime → Restart session and run all again. The result ZIP carries source attribution and data-use terms.

The notebook is generated from the canonical scripts to prevent method drift. To regenerate and verify it locally:

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_notebook.py
python scripts/verify_notebook.py --input notebooks/turkey_inflation_lab.ipynb --output notebooks/turkey_inflation_lab.ipynb
```

See [Google's Colab guide](https://research.google.com/colaboratory/intl/en-GB/faq.html) for uploading notebooks and runtime behavior.

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

Local verification: 29 unit tests passed, plus the real 108-origin experiment (1,728 Ridge fits, one worker). No cloud CI, dashboard, API, forecast interval, live forecast or commercial acceptance is claimed.


## Rebuild diagnostic figures

```bash
python -m pip install -r requirements-dev.txt
python scripts/plot_diagnostics.py --input data/published/research-v1/results --output reports/figures/your-new-run
```

Plots are descriptive analysis of existing development predictions. They do not fit a new model or score the final holdout. The figure manifest records input/code hashes and the plotting-library version. SVG files are published; PNG files are generated for local visual checks.
