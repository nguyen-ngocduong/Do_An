# Repository Guidelines

## Project Structure & Module Organization

- `notebook/`: self-contained Kaggle notebooks for EDA, processing, stacking, XGBoost meta-model, SHAP, Gemini, and integration. Add later stages only when requested.
- `docs/`: research papers and task templates. `docs-md/`: system plans and implementation guides, including `PLAN_HE_THONG_1_SERVER.md`.
- `output/`: downloaded reference artifacts. The selected model, SHAP background, and canonical 50-sample integration run are documented in `output/README.md`; preserve their recorded checksums.
- `BE/`: backend Python code, configuration, pinned dependencies, and backend tests. See `BE/README.md` for running Swagger and `BE/VERIFICATION.md` for checks actually performed.
- `FE/`: Next.js App Router, React, strict TypeScript and Tailwind/CSS, organized like the P-150 frontend. Follow `FE/PLAN.md`; keep `src/app`, domain components, typed `lib/api`, `store` and `types` separate from `BE/`. One-server production uses Nginx in front of loopback Next.js and FastAPI.
- `work_dir/`: contributor plans and evidence-backed checklists. Files follow `Ho_Ten_01_task.md`; smaller numbers indicate earlier priorities.

Dương owns data/models, Hải owns SHAP analysis and Vietnamese Gemini explanations, and Kiên owns integration/evaluation. The chosen XAI method is SHAP only. Consult `work_dir/README.md` for dependencies.

## Build, Test, and Development Commands

Perform dataset processing and model training on **Kaggle**, not locally. Local work includes editing, artifact review, inference, SHAP, Gemini integration, and application development using the frozen artifacts. Do not fit preprocessing or retrain models when moving the inference pipeline to local.

- `.venv/bin/python -m pip install -r BE/requirements-lock.txt`: install the tested backend environment with Python 3.13.
- `.venv/bin/python -m BE.init_env`: create ignored `BE/.env` with a generated password, preserving any existing file.
- `.venv/bin/python -m BE`: start one backend process on localhost; Swagger is at `/docs`, OpenAPI at `/openapi.json`. Use credentials from `BE/.env`.
- `.venv/bin/python -m pytest BE/tests -q --disable-warnings`: verify backend behavior with real frozen artifacts and mocked/cached Gemini responses.

- Frontend, from `FE/` with Node.js 22.12+ (22.x): `npm ci`, then `npm run dev -- --hostname 127.0.0.1 --port 3000`. Login via same-origin `/login` with the existing BE admin account (BE 1.4+ for the remember-session option); HTTP Basic remains available for Swagger/CLI. Production: `npm run build`, then `HOSTNAME=127.0.0.1 PORT=3000 npm run start`; see `FE/deploy/README.md`.
- Frontend checks: `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build`. From repo root, `.venv/bin/python FE/tests/browser_check.py` uses temporary Next/Nginx/BE, real artifacts and mocked Gemini; requires Chrome, Docker, OpenSSL and the latest FE build.
- Dev proxy check: `.venv/bin/python FE/tests/dev_proxy_check.py` verifies login/session/upload/logout and origin rejection through actual Next dev rewrites, using temporary ports/runtime and no real Gemini calls. Requires Node.js 22 and installed FE dependencies; does not read `BE/.env`.

- `python -m json.tool notebook/ciciot2023-do-an-processing.ipynb > /dev/null`: check notebook JSON syntax.
- Kaggle **Restart → Run All**: execute a notebook with its required dataset inputs. Processing writes `/kaggle/working/processed_data/<run_id>/`; use the versions recorded in the selected run when reusing its artifacts.

The backend entrypoint requires HTTPS when binding outside loopback. Follow `BE/README.md` for LAN certificates. Runtime data belongs in ignored `BE/runtime/`; source `output/` artifacts remain read-only. Do not expose or commit `BE/.env` or private TLS keys.

## System Implementation Workflow

- **Branch restriction:** Work on the system plan and its implementation only on the `duong` branch. Check the current branch before editing. Do not modify, commit, push, or merge this work into `main` unless the user explicitly changes this instruction.
- **Saved plan:** Follow `docs-md/PLAN_HE_THONG_1_SERVER.md`, including its artifact inputs, single-server architecture, and acceptance checks.
- **Backend first:** Implement and validate `BE/` before starting frontend implementation. Use FastAPI to expose RESTful APIs and Swagger UI at `/docs`, with the OpenAPI schema at `/openapi.json`, so endpoints can be inspected and exercised before a frontend exists.
- **Separate source folders:** Keep backend implementation in `BE/` and frontend implementation in `FE/`. Serving both from one server does not mean mixing their source code.
- **Single server:** Run application logic, frozen model inference, SHAP, and local persistence on one server. Gemini remains an external API. Load the model and SHAP background once and reuse them across requests.
- **Vietnamese output:** Keep user-facing explanations, instructions, and Gemini system prompts in Vietnamese; preserve source feature and class names for traceability.
- **Readable implementation:** Use explicit, step-by-step functions suitable for an intern or fourth-year student. Keep the initial architecture small and follow the existing notebook style.

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` in Python modules; preserve existing notebook cell organization. No formatter or linter configuration is present. Use descriptive notebook names such as `ciciot2023-do-an-<stage>.ipynb`.

Keep class order fixed: Normal, BruteForce, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based. Preserve feature order and recorded preprocessing; raw labels support mapping and traceability.

**Code Simplicity & Accessibility:** Keep code simple, clean, and straightforward. Do not over-engineer or use overly clever, abstract "senior-level" patterns. Code should be easily readable, understandable, and maintainable by an intern or a 4th-year university student with about 1 month of internship experience (clear variable names, explicit step-by-step logic, and intuitive control flow).

## Testing Guidelines

No standalone test framework or coverage target is configured. Existing checks run inside Kaggle: schema/classes, checksums, overlap audits, pipeline reload predictions, and CSV golden samples. Record which checks actually ran; static validation does not establish experiment completion. Future unit tests should use `tests/test_<module>.py` relative to the component root, for example `BE/tests/test_prediction.py` for the backend. Verify local inference against the saved golden CSV before accepting backend endpoints; Swagger UI inspection supplements automated checks.

Freeze candidates before confirmation. Disclose that baseline validation/test were previously viewed. Report per-class precision/recall/F1, macro-F1, confusion matrices, training/inference times, and hardware.

## Commit & Pull Request Guidelines

History uses short English/Vietnamese subjects; no enforced commit prefix exists. Describe the concrete change. PRs should include purpose, affected notebooks, protocol changes, validation performed, and relevant run IDs or metric comparisons.

Review `.gitignore` before staging: JSON, CSV, arrays, and model binaries are broadly excluded. Keep large artifacts in Kaggle outputs and never commit credentials. Tick checklist items only when supported by actual artifacts.

## Agent Instructions

- Always use the OpenAI developer documentation MCP server if you need to work with the OpenAI API, plugins, ChatGPT, Codex,… without me having to explicitly ask.
- **Code for Intern/Student Readability:** When generating or refactoring code, avoid advanced/complex idioms or over-abstraction. Keep implementations pragmatic, explicit, and easy to explain during graduation thesis defense.


## Codex and Antigravity Collaboration

- Codex coordinates frontend work; Antigravity (`agy`) implements the bounded FE task. This division applies to Codex: AGY must implement directly, never recursively invoke `agy` or delegate the task again.
- Before delegating, Codex reads `FE/PLAN.md`, `FE/design/DESIGN.md`, `FE/design/SURFACE.md` and the relevant typed API. Apply the design skills when applicable and pass a concrete design/behavior contract.
- Write a small task using `docs/templates/AGY_FE_TASK.md`: goal, exact allowed files, API, states, responsive behavior, acceptance criteria, and expected changes. See `docs-md/CODEX_AGY_WORKFLOW.md`.
- Run `python scripts/agy_frontend.py <task.md> --allow-write <FE/path> --expect <FE/file>`. Repeat boundaries/expected paths as needed. The runner uses session-only permissions, a lock, a timeout, JSON output, source snapshots and diffs; it does not modify global AGY settings or bypass permissions.
- While AGY is running, do not edit its files or launch another task against them. AGY uses file tools; Codex owns terminal checks, package installation, browser testing and integration. Do not give AGY secrets, BE/runtime, frozen artifacts, commit/push or server restart work in a frontend task.
- A zero CLI exit or `SUCCESS` is insufficient. Read `.agent-runs/<run>/report.json`, `stdout.json`, `stderr.log`, `changes.diff` and actual files. Check missing expected changes, soft-denied actions and changes outside the assigned scope. Hash snapshots also cover untracked source. The permission profile is a tool policy, not an operating-system sandbox; review remains required.
- Codex runs `python scripts/check_frontend.py` with Node.js 22.12+ (22.x) in PATH. It checks lint/typecheck/test/build in an isolated FE copy and preserves the running dev `.next`. Run focused browser/API checks when the change warrants them; use Page Agent for authorized live UI read checks. Do not restart the user's services.
- If corrections are needed, write a specific follow-up task and use the exact `--conversation <id>` from that run's report; never resume an unrelated most-recent conversation. Recheck the resulting diff and affected checks.
- On auth, quota, permission or timeout failure, report the actual state. Do not treat absent changes as completion, repeatedly consume calls without progress, or silently broaden permissions. Codex may complete the remaining work directly when AGY cannot proceed; disclose the handoff and verification.
