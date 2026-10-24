# Statistical and economic methods

Source identifiers resolve in sources.md. These are project decisions informed by evidence, not a compulsory model recipe.

## Forecast contract
Write: target and units; reference period; information cutoff/release calendar; forecast horizon; intended integration; primary loss; baseline; training/validation/final periods. A monthly annualized rate, monthly percentage change and year-on-year rate are different targets.
First target: next published monthly headline CPI change. Don't call the model a business cost forecast until a business basket and horizon are supplied.

## Backtesting and revisions
Use chronological outer evaluation. For tuning, use only earlier inner folds. Specify expanding versus fixed rolling window based on stability/sample size and compare sensitivity when needed. Account for revised releases and ragged-edge features. Distinguish observed outcomes available today from evaluation against first releases. Source S1 motivates forecast evaluation; S2 supports transparent reporting. Do not assume every random-CV design is always invalid; this project's operational forecast timing is the reason for chronological evaluation.

## Scoring and comparison
Keep point forecast estimand explicit: squared loss targets a conditional mean; absolute loss targets a median. Initial MAE and RMSE together are diagnostics; preselect the metric for choosing a model. Use paired origins and show losses across regimes. Report missing-origin policy and denominator.
If scaled errors are added, compute their scaling denominator from training data and report zero-denominator behavior.
Negative/near-zero monthly inflation makes relative percentage error problematic (S1).
If testing differences, justify sample size, serial dependence, overlapping horizons and multiple comparisons; significant fit is not economic usefulness.

## Model and regime choices
Start naive, seasonal naive and small regularized models. S3's Dutch results depend on target/horizon and forecast construction; do not summarize them as Ridge always wins. S4's Czech quantile-forest work is an optional extension, not evidence of Turkish performance.
Examine structural-break sensitivity; a model calibrated only on stable inflation may extrapolate poorly. Unit-root/residual tests are evidence with assumptions, not pass/fail certifications.

## Uncertainty
Prediction intervals address future outcomes, confidence intervals a parameter or estimator. Ordinary split-conformal exchangeability is a substantive assumption in time series. S5 concerns an adaptive online procedure with long-run coverage, which does not establish valid coverage for every regime or every conditional subgroup.
If intervals are implemented, report calibration history, nominal/empirical coverage, interval width and regime results. Keep interval calibration chronological. Do not promise a coverage guarantee based solely on using a library with conformal in its name.

## Causal and integration limits
SHAP/coefficients describe fitted associations, not the causal effect of interest rates or exchange-rate policy. For policy questions, design identification separately.
Budget integration needs the organization's exposure weights, horizon, nominal/real conventions and an explicit scenario mechanism. CPI alone cannot estimate SKU demand, prices or guaranteed cost savings.
