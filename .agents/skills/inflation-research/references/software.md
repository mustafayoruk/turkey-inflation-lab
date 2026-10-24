# Scientific software and optimization

S2 (REFORMS, 2024) motivates recording data, code, environment and rerun instructions. S6 (Wilson et al., 2017) provides foundational research-computing organization. Current API behavior comes from maintainer documentation, not old papers.

## First slice
Use Python 3.12+ standard library for saved HTML parsing and CSV/JSON outputs. No model/dataframe dependency is needed yet. Add pandas/scikit-learn/DuckDB only when the next slice actually uses them and record versions/lock strategy then.

## Artifact contract
Keep downloaded bytes immutable per snapshot. Record origin URL, actual retrieval timestamp, hash, parser version and limitations. Record complete outputs and don't replace an existing run silently.
Store original and processed data separately. Research input is untrusted: bound read size; parse without executing HTML; reject schema ambiguities, duplicate periods, missing months and non-finite rates. Avoid secrets and unrelated user files in artifacts.

## Verification
Use synthetic fixtures for deterministic edge cases plus an actual downloaded source for integration. Distinguish these proofs. Parsing a table does not establish its historical release times or model validity.
Test valid negative inflation, decimal separators, changed column order, empty/ambiguous tables, bad dates/rates, duplicates and gaps. Inspect final CSV/provenance and source metadata caveats.

## Optimization
Measure run time and dataset dimensions before optimizing. Reuse unchanged source parsing by hash; reuse transformations only under the same training window/config/code. Fold leakage is not an acceptable optimization.
Keep small experiment logs. Bound search and local workers; don't fit a large model zoo on one monthly series for appearance.
Compare pre/post timings on the same data and configuration, also comparing predictions/metrics or defined numerical tolerances. Report speed and statistical changes separately.

## Implementation references
- Python HTMLParser 3.12: https://docs.python.org/3.12/library/html.parser.html — maintainer docs; newer optional parameters must not be assumed in 3.12.
- scikit-learn common pitfalls: https://scikit-learn.org/stable/common_pitfalls.html — maintainer docs; training-only preprocessing and Pipeline. Verify installed version before implementation.
- Codex skill discovery: https://learn.chatgpt.com/docs/build-skills — project skill lives in .agents/skills; AGENTS.md routes to it in this repository. Current chat also reads it explicitly.
