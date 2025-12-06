# dev_contract – Development Framework for Human and AI Developers

This document defines a reusable development framework that can be applied to any software project, regardless of language or stack.

Use it as:
- An onboarding guide for new developers.
- A ruleset when collaborating with AI coding tools.
- A checklist for keeping projects stable and maintainable.

## 1. Core principles

1. Small changes  
   Make incremental, focused changes rather than big rewrites.

2. Single responsibility per change  
   Each change should have one clear purpose.

3. Source of truth  
   Specification and code in the repository are the authority, not memory or chat history.

4. Explicit constraints  
   Always define what is allowed and what is forbidden for a given task.

5. Test before trust  
   Every change must be verifiable through tests, scripts or manual checks.

## 2. Files and ownership model

In any project, classify files into three groups:

1. Frozen  
   - Architectural docs, legal contracts, core configuration.
   - Only change with strong justification and clear review.
   - Usually under `docs/`, `config/`, `infra/`.

2. Core  
   - Main application logic, core modules, entry points.
   - Changes here must be:
     - Well designed.
     - Compatible with existing callers.
     - Commented and reviewed.

3. Flexible  
   - Scripts, utilities, experimental features, dashboards.
   - Safer area for iteration, PoCs, and non-critical improvements.

Document this classification in the project README or a `DEV_NOTES.md` so everyone knows where they can safely work.

## 3. Standard development workflow

For any feature or bug fix:

1. Define the change  
   - One sentence: what you are changing, and why.  
   - If complex, write a short design note in `docs/rfcs/`.

2. Create a branch  
   - Example: `feature/<short-name>` or `bugfix/<short-name>`.

3. Identify allowed files  
   - List which files you intend to modify.  
   - Treat this list as a constraint, especially with AI tools.

4. Implement in small steps  
   - Build the smallest viable version first.  
   - Avoid refactoring unrelated code or modules.

5. Run checks  
   - Unit tests (if exist).  
   - Integration or smoke tests.  
   - Linting or formatting tools.  
   - Basic manual checks on key entry points.

6. Commit and document  
   - Use meaningful commit messages.  
   - Update docs only when behaviour or interfaces change.

## 4. Using AI coding tools under this framework

When using any AI assistant:

1. Provide context  
   - Project name  
   - Stack and frameworks  
   - High level goal  
   - Current file layout (brief)

2. Specify boundaries  
   - Which files it may change.  
   - Which files it must not touch.  
   - Whether it may introduce new dependencies.

3. Keep tasks small  
   - One endpoint, one function, one small module at a time.  
   - If the AI suggests a larger refactor, explicitly decline and break it into steps.

4. Demand full files for changed modules  
   - Ask the AI to show full file contents for each file it modifies.  
   - This makes it easier to paste into editors and review.

5. Always review and test  
   - Treat AI code as draft, not as verified solution.  
   - Run tests and manual checks after applying changes.

## 5. Versioning and releases

1. Tag important milestones  
   - Use semantic or simple versioning:
     - `v1.0.0`, `v1.1.0`, etc  
     - Or `v1.0-baseline`, `v1.1-feature-x`

2. Keep a changelog  
   - Summarise user-visible changes and breaking changes.

3. Stabilise before release  
   - Freeze new features.  
   - Focus on bug fixes and polishing until tests are clean.

## 6. Onboarding a new developer

For any new developer on any project:

1. Give them:
   - Project `README.md`  
   - Relevant docs in `docs/`  
   - This `dev_contract` document

2. Ask them to:
   - Summarise the architecture in their own words.  
   - Identify frozen vs core vs flexible areas.  
   - Make a very small, non-critical change as a first task.

3. Review early work closely  
   - Ensure they follow branching, testing and commit discipline.  
   - Correct misunderstandings early.

## 7. Minimum expectations

Under this framework, any developer (human or AI) is expected to:

- Respect file ownership and boundaries.
- Limit the scope of each change.
- Keep tests passing.
- Maintain and improve documentation as behaviour evolves.
- Communicate clearly and briefly in commit messages and PR descriptions.
