---
name: inflation-research
description: Design, implement, and review inflation and economic time-series data science workflows, with publication-aware evaluation, reproducibility, and decision-focused reporting. Use for data, forecasting, statistical interpretation, or optimization tasks in Turkey Inflation Lab; not for unrelated application work.
---

# Inflation Research

Apply to this project's economic research and supporting code. Support the user's chosen question; do not turn every task into a literature review or require approval for routine implementation choices.

## Frame the decision
Before a new experiment, state target, units, forecast horizon, information cutoff, intended user/decision, primary metric, baselines, and what evidence would change the conclusion. Keep predictive, causal, and scenario questions separate. Refer to docs/VIZYON.md for integration hypotheses; they are not validated demand.

Report in Turkish for a business analyst: value/decision first, economic reasoning next, then technical changes and measured evidence, limits, and next acceptance. Do not hide code progress or lead with implementation detail.

## Information and economic validity
- Keep reference period, release timestamp, retrieval timestamp and data vintage distinct. In point-in-time evaluation, use only features and labels actually available by each cutoff; revised historical values are not automatically available then.
- If publication/vintage history is absent, label the experiment latest-vintage pseudo-out-of-sample and document which availability assumptions remain unverified. Do not manufacture timestamps or claim a live backtest.
- Record units, monthly versus annual rates, adjustment status, methodology/base changes and transformations. Do not splice incompatible index levels. Compound monthly rates when constructing longer-horizon rates; do not sum them as an exact annual measure.
- High inflation, negative monthly values and structural breaks are not automatic data errors. Justify exclusion and report sensitivity.
- Headline CPI is not a company's procurement basket or every household's inflation. Scenario integration requires matching horizon, weights and cost drivers.
- Correlation, feature importance and SHAP do not identify policy effects. Require an identification design and its assumptions before causal claims.

## Evaluation rules
For forecasting/model selection, read references/methods.md. For paper rationale or a new method, consult references/sources.md.
- Recreate the proposed deployment timing using expanding or rolling origins. Random temporal splits are not the default for this forecast task; other domains may justify a different design.
- Fit imputation, scaling, feature selection and tuning on each training fold only. Respect label availability for overlapping horizons; set gaps from the information contract, not arbitrary habit.
- Lock final holdout and primary selection metric before looking at candidate results. Log unsuccessful trials and specification changes; do not repeatedly tune against final test.
- Compare all candidates on identical origins/targets with naive and seasonal-naive baselines. MAE/RMSE in percentage points are the initial project convention, not universal best metrics; align selection with the forecast's intended decision.
- Do not use MAPE as the primary measure for near-zero or negative monthly inflation. Report horizon/period-specific errors and sample sizes. In-sample R² is not out-of-sample forecasting accuracy.
- Do not infer stationarity or normality from failure to reject. Diagnostics inform model/uncertainty choices; they do not mechanically force transformations or test switching.
- If inference is requested, account for serial dependence and multiplicity. Choose HAC, block resampling or another method for its assumptions; avoid iid error bars on dependent losses. No automatic significance testing for every comparison.
- Separate predictive intervals from confidence intervals. Temporal dependence and regime changes can invalidate ordinary exchangeable conformal claims. For interval methods, state assumptions, calibration window, nominal coverage, empirical coverage and width; long-run guarantees do not mean conditional coverage in every month.

## Scientific software and efficient iteration
Read references/software.md when implementing or profiling.
- Preserve a source snapshot and hash, data dictionary and environment/code/config identity. Each run must identify the actual sample, cutoff policy, seed where relevant, parameters and outputs.
- Separate parsing/validation, transformations, training/evaluation and reporting. A notebook may explain results; critical calculations must be rerunnable without hidden notebook state.
- Validate missing/duplicate periods, numeric/schema errors and availability violations. Test failure cases and independently known calculations, not implementation wording.
- Start with the smallest readable pipeline. Add a dependency or service only when a current requirement justifies it; record actual versions when added.
- Cache only deterministic work keyed by source hash plus transformation/config/code identity. Reuse fold preprocessing only when its training membership is identical; never share future-fitted transformations.
- Set an explicit experiment/time budget proportionate to the task; record trials and runtime. Profile before parallelization; bound workers and avoid nested parallelism. No claimed speedup without same-input timing and equivalent scientific outputs.
- Optimize retrieval/parsing and redundant transformations before widening model search. Vectorize measured hotspots when readability and data semantics remain sound.
- Do not silently download huge models, add paid services, run external production writes, publish data, or alter unrelated projects. This skill does not grant new permissions.

## Sources and completion
Use original papers, official statistical agencies and maintainer docs. Distinguish peer-reviewed papers, working papers, preprints and documentation; record date/version and reading depth. Search for relevant recent work when choosing a new method or when prior evidence may be stale, not on every edit. A result in another country is a hypothesis here, not a transfer guarantee.
A source supports a rule only within its assumptions. Local compute budgets and tool choices are project conventions; do not call them scientific laws.

Deliver a reproducible result or state exactly what could not be verified. Passing a schema validator is not empirical model validation. Update docs/TAKIP.md with the evidence for the completed slice.
