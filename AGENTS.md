# Repository Guidelines

## Project Structure & Module Organization

- `notebook/`: only `ciciot2023-do-an.ipynb` (EDA) and `ciciot2023-do-an-processing.ipynb` (processing). Both notebooks contain their own code. Add later stages only when requested.
- `docs/`: research papers and reference material.
- `output/plots/`: downloaded EDA figures. `output/processed_data/`: processing runs with arrays, preprocessors, metadata, and audits. Later model/XAI experiments have been removed for a fresh start.
- `work_dir/`: contributor plans and evidence-backed checklists. Files follow `Ho_Ten_01_task.md`; smaller numbers indicate earlier priorities.

Dương owns data/models, Hải owns SHAP/LIME analysis, and Kiên owns integration/evaluation. Consult `work_dir/README.md` for dependencies.

## Build, Test, and Development Commands

There is no application build command. Perform processing and training on **Kaggle**, not locally. Local work covers editing, static checks, and artifact review.

- `python -m json.tool notebook/ciciot2023-do-an-processing.ipynb > /dev/null`: check notebook JSON syntax.
- Kaggle **Restart → Run All**: execute a notebook with its required dataset inputs. Processing writes `/kaggle/working/processed_data/<run_id>/`; use the versions recorded in the selected run when reusing its artifacts.

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` in Python modules; preserve existing notebook cell organization. No formatter or linter configuration is present. Use descriptive notebook names such as `ciciot2023-do-an-<stage>.ipynb`.

Keep class order fixed: Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based. Preserve feature order and recorded preprocessing; raw labels support mapping and traceability.

**Code Simplicity & Accessibility:** Keep code simple, clean, and straightforward. Do not over-engineer or use overly clever, abstract "senior-level" patterns. Code should be easily readable, understandable, and maintainable by an intern or a 4th-year university student with about 1 month of internship experience (clear variable names, explicit step-by-step logic, and intuitive control flow).

## Testing Guidelines

No standalone test framework or coverage target is configured. Existing checks run inside Kaggle: schema/classes, checksums, overlap audits, pipeline reload predictions, and CSV golden samples. Record which checks actually ran; static validation does not establish experiment completion. Any future unit tests should use `tests/test_<module>.py`.

Freeze candidates before confirmation. Disclose that baseline validation/test were previously viewed. Report per-class precision/recall/F1, macro-F1, confusion matrices, training/inference times, and hardware.

## Commit & Pull Request Guidelines

History uses short English/Vietnamese subjects; no enforced commit prefix exists. Describe the concrete change. PRs should include purpose, affected notebooks, protocol changes, validation performed, and relevant run IDs or metric comparisons.

Review `.gitignore` before staging: JSON, CSV, arrays, and model binaries are broadly excluded. Keep large artifacts in Kaggle outputs and never commit credentials. Tick checklist items only when supported by actual artifacts.

## Agent Instructions

- Always use the OpenAI developer documentation MCP server if you need to work with the OpenAI API, plugins, ChatGPT, Codex,… without me having to explicitly ask.
- **Code for Intern/Student Readability:** When generating or refactoring code, avoid advanced/complex idioms or over-abstraction. Keep implementations pragmatic, explicit, and easy to explain during graduation thesis defense.
