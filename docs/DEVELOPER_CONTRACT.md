# Developer Contract – AI Trading Copilot

This document defines how development on the "AI Trading Copilot" repository must be done.

It applies to:
- Human developers
- AI coding assistants (Codex, Gemini, ChatGPT, etc)

## 1. Objectives

- Keep the codebase stable and production ready.
- Make small, incremental changes rather than large rewrites.
- Ensure that all changes are testable and traceable.
- Preserve the existing architecture and configuration model.

## 2. Branching and version control

- Use Git for all work.
- Create a new branch for each feature or bug fix.
  - Example: `feature/news-filter`, `bugfix/equity-nan`.
- Never work directly on `main` / `master`.
- Tag important milestones:
  - `v1.0-baseline` for the first working skeleton.
  - `v1.1`, `v1.2` etc for releases.

## 3. Files and ownership

Treat files in three groups:

1. Frozen by default  
   - `docs/` (all specs and strategy documents)
   - `config/config.yaml`
   - `data/` (CSV source data)
   - `mt4/AICopilotEA.mq4`
   - Any file explicitly labelled "FROZEN" in a comment

   Only change these when:
   - You have a clear design reason, and
   - The change is documented in a commit message or a short RFC.

2. Controlled core  
   - `src/v1_0/core/*.py`
   - `src/v1_0/api/server.py`
   - `src/v1_0/api/schemas.py`

   These define the heart of the system. Changes here must be:
   - Small
   - Fully understood
   - Backward compatible wherever possible

3. Flexible layer  
   - `smoke_test.py`
   - `backtest_example.py`
   - `backtest_portfolio.py`
   - `dashboard/index.html`
   - Utility scripts under `scripts/` (if present)
   - New modules added under `src/v1_0/...`

   These are safer places for experiments and incremental improvements.

## 4. Change process

For each change:

1. Clarify scope  
   - Write a 1–3 line description of what you are changing and why.  
   - If needed, add a short design note in `docs/rfcs/` (for bigger changes).

2. Identify files to touch  
   - List specific files you expect to modify.  
   - If AI is involved, tell it clearly:  
     - "You may only change: X, Y, Z."

3. Implement change  
   - Keep the change as small as possible.  
   - Avoid refactoring unrelated code.

4. Run checks  
   - Ensure these commands still work:
     - `python smoke_test.py`
     - `python backtest_example.py`
     - `python backtest_portfolio.py`
     - `uvicorn main:app --reload` (for API changes)
   - If any fail, fix them before merging.

5. Commit with meaningful message  
   - Example: `feat: add /equity/portfolio endpoint with cached curve`  
   - Example: `fix: stabilise dashboard equity chart for single-point series`

## 5. AI usage rules

When using AI to write code:

- Always provide:
  - Project context
  - Clear scope
  - File boundaries
- Use the master system prompt: `docs/MASTER_PROMPT_AI_DEV.md`.
- Review AI-produced code carefully:
  - Check imports and names.
  - Verify that no unexpected files were changed.
  - Remove any placeholder comments.

If AI output is too large or touches too many areas, reduce the scope and re-ask.

## 6. Testing discipline

Minimum baseline for any change:

- `python smoke_test.py` must run without errors.
- `python backtest_example.py` must run and produce output.
- `python backtest_portfolio.py` must run and produce output.
- If you changed the API or dashboard:
  - `uvicorn main:app --reload` must start.
  - `/signal/latest`, `/equity/portfolio` and `/dashboard` must respond.

Over time, automated tests (pytest) can be added; they will then also become mandatory.

## 7. Documentation

- Keep `README.md` high level and accurate.
- Keep `docs/` as the detailed specification:
  - PRD
  - Strategy rules
  - AI dev master prompt
  - This developer contract
- For larger changes, add short RFC files:
  - `docs/rfcs/NN-feature-name.md`

## 8. Behaviour expectations

- Small, frequent commits over large, rare ones.
- Avoid cleverness if it harms readability.
- Keep public APIs stable.
- Prefer configuration over hard-coded constants where it makes sense.
