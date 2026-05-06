# Current Project Mission

Build the Creator Source Passport MVP.

Before coding, read:

- docs/PROJECT_CONTEXT.md
- README.md
- package.json
- pyproject.toml
- docker-compose.yml
- .env.example

Use docs/PROJECT_CONTEXT.md as the source of truth.

Do not build:

- generic GEO SaaS
- full CMS
- full social media scheduler
- WeChat/Zhihu automation bot
- payment system
- team permission system

Focus only on:

- Source Passport model
- canonical source page
- AI-readable markdown assets
- llms.txt / sitemap / robots / schema
- platform variants
- visible source anchor
- AI retrieval monitor
- revision suggestions


\## Git Safety Rules



Before making changes:

\- Run `git status`.

\- If this is not a Git repository, stop and ask the user to initialize Git.

\- Work on a branch named `codex-\*` when possible.

\- Do not run `git init` automatically unless explicitly requested.

\- Do not run `git add .` blindly.

\- Do not commit automatically unless explicitly requested.

\- Do not run `git reset --hard` or `git clean -fd` unless explicitly requested.

\- Do not delete files unless explicitly requested.



Before major edits:

\- Check current branch.

\- Check changed files.

\- Avoid modifying `.env`, secrets, databases, uploads, logs, or user data.



After finishing:

\- Report `git status`.

\- Summarize created, modified, and deleted files.

\- Tell the user which verification commands passed or failed.



\## Branch Rule



For non-trivial tasks, create or use a branch named `codex-auto` or `codex-\[task-name]`.

Do not merge back to main/master automatically.



\## gstack workflow for Codex



Use gstack skills automatically for non-trivial project work.



Routing rules:



\- Simple typo or tiny edit: do not use gstack.

\- New product idea or large feature: use gstack autoplan first.

\- Architecture/database/API change: use gstack plan-eng-review.

\- UI, landing page, dashboard, or visual design: use gstack plan-design-review, then design-html if needed.

\- Existing bug with unclear cause: use gstack investigate before fixing.

\- Before finishing a branch: use gstack review.

\- If the project has a running web app or staging URL: use gstack qa.

\- Before release or PR: use gstack ship.

\- Security-sensitive work: use gstack cso or guard.

\- Risky file operations: use gstack careful/guard.



Default project loop:



1\. Understand the project.

2\. Use gstack autoplan for medium/large tasks.

3\. Implement the smallest approved plan.

4\. Run tests/build/lint.

5\. Use gstack review.

6\. Fix review issues.

7\. Use gstack qa if browser testing applies.

8\. Use gstack ship only when the branch is ready.



Do not ask the user before using gstack unless the operation is destructive, requires secrets, deploys to production, or changes external accounts.



\## gstack Acceptance Criteria



Use gstack to plan, build, review, and verify this project.



Final result must satisfy:



1\. The project can be installed and started locally.

2\. The main user workflow works end-to-end.

3\. The UI is usable, clean, and not just placeholder content.

4\. The backend/API/data flow is connected if required.

5\. No unrelated refactor or unnecessary feature expansion.

6\. No secrets, databases, uploads, or user files are deleted.

7\. Build/test/lint must be run before completion.

8\. Use gstack review before final summary.

9\. If there is a web UI, use gstack QA or browser testing to verify the core flow.

10\. Final summary must include changed files, verification results, and remaining risks.





