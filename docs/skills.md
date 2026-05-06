# Codex Skills Index

This directory is the active personal skills library for Codex. Use this index to
route requests, identify overlap, and decide what should be kept active,
consolidated, or archived later.

Last audit: 2026-04-27.

## Routing Rules

- Prefer the most specific skill that matches the user's requested job.
- Treat `.system/` skills as platform/system skills; do not rename or archive them.
- Treat `gstack/.*/skills/` as generated multi-client exports, not hand-maintained
  active skills.
- Treat `gsd-` skills as a secondary workflow suite, not part of the general
  top-level skill set.
- Treat top-level skills as active user-facing entries unless marked as legacy in
  this README.
- Do not delete skills directly. Move only after confirming a migration target and
  keeping an archive note.

## Recommended Categories

### Skill Management

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `.system/skill-creator` | Create or update Codex skills with valid metadata, resources, and validation. | create a skill, update a skill, improve SKILL.md | System |
| `.system/skill-installer` | Install skills from curated lists or GitHub repos. | install skill, list installable skills | System |
| `.system/plugin-creator` | Scaffold Codex plugin directories and marketplace metadata. | create plugin, scaffold plugin | System |
| `adapt-skill` | Customize or fork an existing skill for a private workflow. | adapt skill, remix skill, personalize a community skill | Active |
| `book-to-skills` | Convert books, manuals, SOPs, or knowledge bases into a skill map and downstream skill specs. | turn a book into skills, distill manual into skills | Active |
| `book2skill` in `cangjie-skill/` | Legacy book-to-skill workflow with corrupted body text. | explicit old book2skill/cangjie request only | Migrate to `book-to-skills` |

### OpenAI, Runtime, And Media Tools

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `.system/openai-docs` | Answer OpenAI product/API questions from official docs. | OpenAI API docs, latest model, Responses API | System |
| `.system/imagegen` | Generate or edit bitmap images. | make an image, edit this image | System |
| `make-pdf` | Turn Markdown into publication-quality PDF output. | make a PDF, export publication | Active |
| `feishu-report-kb` | Convert Feishu daily reports or exported DOCX reports into reusable KB artifacts. | Feishu report, daily report to knowledge base | Active |

### Academic And Long-Form Knowledge

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `academic-paper` | Write, revise, format, or check academic papers. | write paper, revise manuscript, citation check | Active |
| `academic-paper-reviewer` | Simulate multi-perspective academic peer review. | review my paper, referee report, editorial review | Active |
| `academic-pipeline` | Orchestrate research-to-publication workflow across research, writing, review, and revision. | full paper workflow, research to paper | Active |
| `dbs-diagnosis` | Diagnose dontbesilent business models and business questions. | business model diagnosis, diagnose my business | Active |

### Design And Frontend Experience

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `claritas-html-designer` | Build high-fidelity HTML artifacts, prototypes, and UI explorations. | HTML prototype, clickable artifact | Active |
| `claude-design` | Legacy/alternate HTML-first design artifact workflow. | high-fidelity design, design artifact | Review overlap |
| `design-consultation` | Research product context and propose design direction/system. | design consultation, how should this look | Active |
| `design-shotgun` | Generate multiple design variants and compare them. | design variants, shotgun designs | Active |
| `design-html` | Finalize approved mockups into production-quality HTML/CSS. | finalize design, generate HTML | Active |
| `design-review` | Audit visual quality, spacing, hierarchy, interaction, and AI slop. | design review, this looks off | Active |
| `plan-design-review` | Review a plan from a designer's-eye perspective before execution. | review design plan, plan design critique | Active |

### Browser, QA, And Deployment

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `browse` | Headless browser navigation, screenshots, page inspection, and dogfooding. | open URL, inspect page, take screenshot | Active |
| `gstack` | Router/source skill for gstack browser QA capabilities. | browse this page, navigate to URL | Source/router |
| `open-gstack-browser` | Launch visible GStack Browser with sidebar. | open gstack browser, launch real browser | Active |
| `connect-chrome` | Compatibility alias for old connect-chrome wording. | connect chrome | Alias |
| `setup-browser-cookies` | Import real Chromium cookies for authenticated browser testing. | import cookies, login to test site | Active |
| `qa-only` | Browser QA report without fixing bugs. | QA report, test this site without changes | Active |
| `qa` | Browser QA plus iterative source fixes. | QA this app, find and fix bugs | Active |
| `benchmark` | Detect performance regressions and capture web vitals. | benchmark page, performance regression | Active |
| `canary` | Post-deploy live monitoring for errors and regressions. | canary check, watch deploy | Active |
| `devex-review` | Test developer onboarding and docs in a browser. | developer experience audit, try onboarding | Active |
| `setup-deploy` | Configure deployment settings for land-and-deploy. | setup deploy, configure deployment | Active |
| `ship` | Prepare code for PR: tests, review, changelog, commit, push, PR. | ship it, create PR, push | Active |
| `land-and-deploy` | Merge, wait for CI/deploy, and verify production. | land and deploy, merge and verify | Active |
| `landing-report` | Read-only queue dashboard for workspace-aware shipping. | landing report, version slots | Active |
| `document-release` | Update docs after shipped code changes. | update docs after release | Active |

### Engineering Review, Debugging, Safety, And Quality

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `investigate` | Systematic debugging and root-cause analysis. | debug this, investigate error | Active |
| `review` | Pre-landing PR/code review. | review this PR, check my diff | Active |
| `codex` | Use Codex CLI for review/challenge/implementation modes. | codex review, second opinion | Active |
| `cso` | Infrastructure-first security audit. | security audit, is this secure | Active |
| `health` | Code quality dashboard using local project tools. | health check, code quality dashboard | Active |
| `careful` | Warn before destructive commands. | careful mode, destructive command guard | Active |
| `guard` | Full safety mode: destructive warnings plus edit-scope boundaries. | guard mode, lock it down | Active |
| `freeze` | Restrict edits to a directory. | freeze edits, only edit this folder | Active |
| `unfreeze` | Clear an edit freeze. | unfreeze, unlock edits | Active |

### Planning, Product, And Retrospectives

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `office-hours` | YC-style startup/product evaluation and hard questions. | office hours, is this worth building | Active |
| `plan-ceo-review` | Founder/CEO-style review of scope, ambition, and product strategy. | CEO review, think bigger | Active |
| `plan-eng-review` | Engineering manager review of architecture, data flow, tests, and execution. | engineering plan review | Active |
| `plan-devex-review` | Developer experience review of a plan. | devex plan review | Active |
| `autoplan` | Sequential CEO/design/eng/DX review pipeline. | auto-review plan, review everything | Active |
| `plan-tune` | Tune question sensitivity and interaction preferences. | stop asking me, tune questions | Active |
| `retro` | Weekly engineering retrospective from commits and work patterns. | weekly retro, what did we ship | Active |
| `learn` | Manage gstack learnings across sessions. | show learnings, prune learnings | Active |
| `context-save` | Save working context for future sessions. | save context, save my work | Active |
| `context-restore` | Restore saved working context. | restore context, where was I | Active |
| `pair-agent` | Pair a remote AI agent with the browser. | pair agent, remote browser agent | Active |
| `setup-gbrain` | Install and initialize gbrain memory/sync. | setup gbrain, connect gbrain | Active |
| `gstack-upgrade` | Upgrade gstack installation. | upgrade gstack | Active |

### Secondary: GSD Project Workflow

GSD skills form a coherent project-planning system. Keep the `gsd-` prefix; it
prevents collisions with general-purpose skills.

| Skill | Use | Trigger examples |
| --- | --- | --- |
| `gsd-new-project` | Initialize a project with deep context and `PROJECT.md`. | new GSD project |
| `gsd-new-milestone` | Start a new milestone cycle. | new milestone |
| `gsd-progress` | Check project progress and route next action. | GSD progress |
| `gsd-next` | Advance to the next logical GSD step. | next GSD step |
| `gsd-do` | Route freeform text to the right GSD command. | do this with GSD |
| `gsd-help` | Show available GSD commands. | GSD help |
| `gsd-settings` | Configure GSD workflow toggles. | GSD settings |
| `gsd-set-profile` | Switch GSD model profile. | set GSD profile |
| `gsd-new-workspace` | Create isolated workspace and planning copy. | new GSD workspace |
| `gsd-list-workspaces` | List active GSD workspaces. | list workspaces |
| `gsd-remove-workspace` | Remove a GSD workspace and worktrees. | remove workspace |
| `gsd-workstreams` | Manage parallel workstreams. | workstream status |
| `gsd-discuss-phase` | Gather phase context before planning. | discuss phase |
| `gsd-list-phase-assumptions` | Surface assumptions before planning. | list assumptions |
| `gsd-research-phase` | Research implementation for a phase. | research phase |
| `gsd-plan-phase` | Create detailed `PLAN.md` with verification loop. | plan phase |
| `gsd-review` | Request cross-AI peer review of phase plans. | review GSD plan |
| `gsd-plan-milestone-gaps` | Create phases for milestone audit gaps. | plan gaps |
| `gsd-analyze-dependencies` | Suggest phase dependency entries. | analyze dependencies |
| `gsd-add-phase` | Add phase to current milestone. | add phase |
| `gsd-insert-phase` | Insert urgent decimal phase. | insert phase |
| `gsd-remove-phase` | Remove future phase and renumber. | remove phase |
| `gsd-execute-phase` | Execute phase plans with wave parallelization. | execute phase |
| `gsd-fast` | Execute trivial task inline. | GSD fast |
| `gsd-quick` | Execute quick task with GSD guarantees. | GSD quick |
| `gsd-autonomous` | Run remaining phases autonomously. | autonomous GSD |
| `gsd-add-tests` | Generate tests for completed phase UAT. | add phase tests |
| `gsd-validate-phase` | Fill validation gaps after completion. | validate phase |
| `gsd-verify-work` | Conversational UAT validation. | verify work |
| `gsd-secure-phase` | Verify threat mitigations. | secure phase |
| `gsd-ui-phase` | Generate `UI-SPEC.md` design contract. | UI phase |
| `gsd-ui-review` | Retroactive frontend visual audit. | UI review |
| `gsd-docs-update` | Generate or update docs from codebase. | update docs |
| `gsd-map-codebase` | Produce codebase maps under `.planning/codebase/`. | map codebase |
| `gsd-debug` | Debug with persistent state across resets. | GSD debug |
| `gsd-forensics` | Post-mortem failed GSD workflows. | GSD forensics |
| `gsd-health` | Diagnose and repair planning directory health. | GSD health |
| `gsd-audit-uat` | Cross-phase outstanding UAT audit. | audit UAT |
| `gsd-audit-milestone` | Audit milestone completion before archive. | audit milestone |
| `gsd-complete-milestone` | Archive milestone and prepare next version. | complete milestone |
| `gsd-cleanup` | Archive accumulated phase directories. | GSD cleanup |
| `gsd-milestone-summary` | Generate milestone summary for onboarding/review. | milestone summary |
| `gsd-ship` | Create PR and prepare for merge after verification. | GSD ship |
| `gsd-pr-branch` | Create clean PR branch without planning commits. | PR branch |
| `gsd-update` | Update GSD to latest version. | update GSD |
| `gsd-reapply-patches` | Reapply local modifications after GSD update. | reapply patches |
| `gsd-add-backlog` | Add idea to backlog parking lot. | add backlog |
| `gsd-review-backlog` | Promote backlog items. | review backlog |
| `gsd-add-todo` | Capture task as todo. | add todo |
| `gsd-check-todos` | List/select pending todos. | check todos |
| `gsd-note` | Capture, list, or promote notes. | note this |
| `gsd-plant-seed` | Capture future idea with trigger conditions. | plant seed |
| `gsd-thread` | Manage persistent context threads. | GSD thread |
| `gsd-pause-work` | Create handoff when pausing. | pause work |
| `gsd-resume-work` | Resume from previous session. | resume work |
| `gsd-session-report` | Generate session report and token estimate. | session report |
| `gsd-stats` | Show project statistics and timeline. | GSD stats |
| `gsd-profile-user` | Generate developer behavioral profile. | profile user |
| `gsd-join-discord` | Join GSD community. | join GSD Discord |

### OpenClaw Nested Skills

These live under `gstack/openclaw/skills/` and should stay namespaced.

| Skill | Use | Trigger examples | Status |
| --- | --- | --- | --- |
| `gstack-openclaw-ceo-review` | Challenge a plan or proposal from CEO/founder perspective. | OpenClaw CEO review | Active nested |
| `gstack-openclaw-investigate` | Debug and root-cause errors under OpenClaw workflow. | OpenClaw investigate | Active nested |
| `gstack-openclaw-office-hours` | Brainstorm and evaluate product ideas. | OpenClaw office hours | Active nested |
| `gstack-openclaw-retro` | Engineering retrospective for OpenClaw/gstack history. | OpenClaw retro | Active nested |

## Duplicate And Migration Findings

| Finding | Impact | Recommendation |
| --- | --- | --- |
| Top-level gstack skills duplicate `gstack/<skill>/SKILL.md` source copies. | Codex sees duplicate names and may list the same trigger twice. | Pick one active namespace. Prefer top-level skills for user-facing routing, keep `gstack/<skill>` as source/vendor copy, or move one set to archive after confirming gstack update behavior. |
| Hidden `gstack/.agents`, `.cursor`, `.factory`, `.kiro`, `.openclaw`, `.opencode`, `.slate` contain repeated generated SKILL.md files. | Large scan noise; not useful for manual indexing. | Treat as generated exports. Do not edit manually; regenerate from gstack tooling if needed. |
| `connect-chrome` and `open-gstack-browser` had identical `name: open-gstack-browser`. | Name collision and broad trigger overlap. | `connect-chrome` is now a compatibility alias; route normal launch requests to `open-gstack-browser`. |
| `cangjie-skill/` has `name: book2skill` and corrupted Chinese body text. | Hard to maintain; overlaps with `book-to-skills`. | Keep the requested name, but migrate new work to `book-to-skills`. Archive only after old artifacts are checked. |
| `claude-design` overlaps with `claritas-html-designer` and design/gstack skills. | Potentially broad design triggers. | Keep both for now, but define `claritas-html-designer` as the preferred HTML artifact builder and review whether `claude-design` still adds unique workflows. |
| `guard`, `careful`, `freeze`, and `unfreeze` overlap on safety/edit scope. | Related but distinct safety controls can trigger together. | Keep all. Use `careful` for destructive warnings, `freeze/unfreeze` for path scope, `guard` for combined mode. |
| `academic-pipeline`, `academic-paper`, and `academic-paper-reviewer` overlap. | Pipeline may trigger when only writing or reviewing is needed. | Keep all. Use pipeline only for end-to-end research-to-publication workflows. |

## Frontmatter Hygiene Backlog

Several skills contain additional YAML keys such as `version`, `triggers`,
`allowed-tools`, `metadata`, and `preamble-tier`. Codex primarily uses `name` and
`description` for triggering, but existing gstack/GSD generators may depend on the
extra keys. Do not bulk-remove them without checking the owning generator.

Recommended future pass:

1. Normalize top-level active skills to exact folder/name alignment except explicit
   aliases such as `connect-chrome`.
2. Move noisy trigger lists out of frontmatter only if the owning runtime supports it.
3. Regenerate `agents/openai.yaml` for hand-maintained skills whose description
   changed.
4. Archive only after a dry-run confirms the skill no longer appears in Codex's
   active skill list.
