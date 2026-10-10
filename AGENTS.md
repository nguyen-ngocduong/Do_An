# Repository Guidelines

## Project Structure & Module Organization

- `notebook/`: Kaggle notebooks for CICIoT2023 exploration, processing, pilot sampling, DT/RF/XGBoost baselines, and recall improvement. `ciciot_preprocessing.py` contains preprocessing helpers; keep helpers synchronized with notebook exports.
- `docs/`: research papers and reference material.
- `output/`: downloaded Kaggle runs, metrics, plots, models, manifests, and handoff bundles, organized by run ID.
- `work_dir/`: contributor plans and evidence-backed checklists. Files follow `Ho_Ten_01_task.md`; smaller numbers indicate earlier priorities.

Dương owns data/models, Hải owns SHAP/LIME analysis, and Kiên owns integration/evaluation. Consult `work_dir/README.md` for dependencies.

## Build, Test, and Development Commands

There is no application build command. Perform processing and training on **Kaggle**, not locally. Local work covers editing, static checks, and artifact review.

- `python -m json.tool notebook/ciciot2023-do-an-recall-improvement.ipynb > /dev/null`: check notebook JSON syntax.
- `python -c 'import ast; from pathlib import Path; ast.parse(Path("notebook/ciciot_preprocessing.py").read_text())'`: parse helper code without executing it.
- Kaggle **Restart → Run All**: execute an experiment with its required inputs. Use the baseline-compatible environment and CPU configuration. Set `RESUME_FROM` to a saved recall-run directory containing `protocol.json` to continue checkpoints.

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` in Python modules; preserve existing notebook cell organization. No formatter or linter configuration is present. Use descriptive notebook names such as `ciciot2023-do-an-<stage>.ipynb`.

Keep class order fixed: Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based. Preserve feature order and recorded preprocessing; raw labels support mapping and traceability.

## Testing Guidelines

No standalone test framework or coverage target is configured. Existing checks run inside Kaggle: schema/classes, checksums, overlap audits, pipeline reload predictions, and CSV golden samples. Record which checks actually ran; static validation does not establish experiment completion. Any future unit tests should use `tests/test_<module>.py`.

Freeze candidates before confirmation. Disclose that baseline validation/test were previously viewed. Report per-class precision/recall/F1, macro-F1, confusion matrices, training/inference times, and hardware.

## Commit & Pull Request Guidelines

History uses short English/Vietnamese subjects; no enforced commit prefix exists. Describe the concrete change. PRs should include purpose, affected notebooks, protocol changes, validation performed, and relevant run IDs or metric comparisons.

Review `.gitignore` before staging: JSON, CSV, arrays, and model binaries are broadly excluded. Keep large artifacts in Kaggle outputs and never commit credentials. Tick checklist items only when supported by actual artifacts.
