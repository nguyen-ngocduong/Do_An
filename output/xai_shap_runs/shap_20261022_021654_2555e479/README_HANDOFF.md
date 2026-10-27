# SHAP explanation output

Model: XGB_d4_n200
Source XGBoost run: xgb_meta_20261021_092334_9024562d
Data run: 20261021_052521_96f61f19
SHAP run: shap_20261022_021654_2555e479

## Read the results

- explanation_summary.csv: predicted class/probability, true class, timing and additivity errors.
- top5_all_cases.csv: top features for the predicted class of every selected sample.
- selected_cases.csv: validation row index, original label, source row and class mapping.
- cases/<case_id>/waterfall.png: SHAP contributions to the predicted-class probability.
- cases/<case_id>/explanation.json: structured prediction + top features, ready for later integration.
- cases/<case_id>/explanation.txt: numerical explanation without an LLM.
- cases/<case_id>/shap_values.npz: all original features and all 8 class contributions.
- cases/<case_id>/comparison_features.csv: contributions to predicted-class vs comparison-class probability gap.
- protocol.json, source_artifacts.json, requirements.txt: scope, seeds, background, versions, hardware and checksums.
- reload_checks.json: the checks actually executed by this notebook.

The large model bundle is reused from the Kaggle input, not copied into this output.
model_reference.json records its run/path/checksum. Keep the saved source XGBoost version.

## Interpretation

Values are in probability units, not log-odds. A SHAP value of +0.01 means a +1 percentage-point
contribution relative to the chosen background for the class being explained.
Positive/negative contributions do not prove the effect of increasing/decreasing a feature.
Top 5 follows absolute SHAP values and retains their signs. The other features are still included
in the saved arrays and the waterfall's grouped row.

Background is 32 uniform random train rows. The masking operation may create
feature combinations not observed in real traffic. These are model explanations relative to that
background, not causal evidence. Additivity is checked; SHAP convergence/stability is not claimed.

Validation/test were previously viewed. This is local explanation of an already frozen model,
not new independent model evaluation. No model fitting, test inference, LIME or LLM calls.

## Explain other samples

Use the notebook's MANUAL_VAL_INDICES for validation rows after processing, starting at 0.
Or change CORRECT_PER_CLASS/WRONG_PER_CLASS/MAX_CASES before Restart -> Run All.
Increase background/budget only when needed; they affect runtime and the explanation reference.
Use the recorded versions when reproducing the same run.
