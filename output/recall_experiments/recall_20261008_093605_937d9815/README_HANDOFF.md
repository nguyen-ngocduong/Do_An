# Recall study — recall_20261008_093605_937d9815

Primary (selected by tune only): C_2f13b00cf8811500. Precision floor: 30% each BruteForce/Web-Based. Recall target: 85% each, not guaranteed.
Status: complete. Baseline run: models_20261008_073827_d29a37c3. Validation/test previously viewed; grouped tune/confirm used to control this new search only.

Read search_results.csv / ablation_summary.csv, sampling/*, feature_selection/*, frozen_candidates.json, confirmation_summary.csv and old_test_summary.csv where present. Per-class metrics, recall CI95, confusion matrices, probability rows and sample IDs are in assessments/<split>/<trial>. Read target_met on confirmation, not only tune.

Pipeline:
```python
from recall_inference import predict_csv
predict_csv('handoff/C_2f13b00cf8811500', 'input.csv', 'predictions.csv')
```
Import recall_inference before joblib.load pipeline. predict uses tuned decision; predict_proba returns original model probabilities. Class order stays 0..7. For SHAP explain underlying estimator model.base_estimator on raw float32 selected feature order; report decision multipliers separately.

Use requirements_runtime.txt and protocol.json to reproduce. RESUME_FROM imports entire earlier output; source/version/protocol must match. Sampling/partition indices, trial checksums and frozen model hashes are saved. Golden samples exercise saved pipeline/CSV helper inside Kaggle. This is not an independent reproduction from raw CSV on another environment.

Limitations: finite rare support, dependence among duplicate/session samples, full-source-train preprocessing reused, validation/test previously viewed, feature projection overlap may reject SHAP subsets, precision/recall may vary across seeds. No fabricated target improvement. Do not reopen searches after confirmation to get prettier points. New unused data requires provenance and overlap audit; no fresh test acquired automatically.

Tasks: Dương owns sample/weight/tuning/decision and model artifacts; Hải owns SHAP/LIME analysis and interpreting raw output vs decision; Kiên owns integration, CSV checking, end-to-end benchmark and guidance. Six-to-eight-week reporting/demo follows the plan.
