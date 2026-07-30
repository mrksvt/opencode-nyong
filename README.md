# Katalog Skill OpenCode

Kumpulan lengkap skill yang tersedia di mesin ini untuk OpenCode. Skill adalah modul panduan khusus yang bisa dimuat saat dibutuhkan, memberikan instruksi langkah demi langkah untuk tugas tertentu.

## Cara Memuat Skill

```python
skill(name="skill-name")
```

Contoh:

```python
skill(name="systematic-debugging")
skill(name="compose-animations")
```

Skill bisa juga dipanggil via slash command di CLI:

```
/systematic-debugging
/compose-animations
```

---

## Daftar Isi

1. [Development & Code Quality](#1-development--code-quality)
2. [Kotlin / Android / Jetpack Compose (chrisbanes-skills)](#2-kotlin--android--jetpack-compose-chrisbanes-skills)
3. [Design & Visual](#3-design--visual)
4. [Documents & Content](#4-documents--content)
5. [Web & Deployment](#5-web--deployment)
6. [AI / MCP / LLM](#6-ai--mcp--llm)
7. [Project Management](#7-project-management)
8. [Visualization & Analysis](#8-visualization--analysis)
9. [Utilities](#9-utilities)

---

## 1. Development & Code Quality

### ask-questions-if-underspecified

Clarify requirements before implementing. Use when serious doubts arise.

`/home/mrksvt/.config/opencode/skills/ask-questions-if-underspecified/SKILL.md`

### code-security-auditor

Perform pre-execution security audits of untrusted codebases through static analysis. Use when analyzing a codebase for potential malicious behavior, supply chain risks, or security vulnerabilities before local execution.

`/home/mrksvt/.config/opencode/skills/code-security-auditor/SKILL.md`

### receiving-code-review

Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable.

`/home/mrksvt/.config/opencode/skills/receiving-code-review/SKILL.md`

### staff-engineer-review

Performs deep code review of pull requests as a Staff+ level engineer. Use when reviewing PRs, evaluating implementation against plans, assessing architectural decisions, code quality.

`/home/mrksvt/.config/opencode/skills/staff-engineer-review/SKILL.md`

### systematic-debugging

Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes.

`/home/mrksvt/.config/opencode/skills/systematic-debugging/SKILL.md`

### test-driven-development

Use when implementing any feature or bugfix, before writing implementation code.

`/home/mrksvt/.agents/skills/test-driven-development/SKILL.md`

### verification-before-completion

Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims.

`/home/mrksvt/.config/opencode/skills/verification-before-completion/SKILL.md`

### writing-plans

Use when you have a spec or requirements for a multi-step task, before touching code.

`/home/mrksvt/.config/opencode/skills/writing-plans/SKILL.md`

---

## 2. Kotlin / Android / Jetpack Compose (chrisbanes-skills)

Skill dari paket [chrisbanes-skills](https://github.com/chrisbanes/skills). Untuk tugas Kotlin/Android/Compose yang terlalu luas untuk satu skill, muat `using-chrisbanes-skills` dulu.

### compose-animations

Use when writing or reviewing Jetpack Compose motion: visibility enter/exit, animating one property toward a target, color or size transitions, multiple properties from one state, switching composable content, or choosing between AnimatedVisibility, animate*AsState, rememberTransition, AnimatedContent, and Crossfade.

`chrisbanes-skills package`

### compose-focus-navigation

Use when writing or reviewing Jetpack Compose UI for TV, keyboard, desktop, accessibility focus, D-pad navigation, FocusRequester, focusProperties, key events, or initial focus behavior.

`chrisbanes-skills package`

### compose-modifier-and-layout-style

Use when writing or reviewing Jetpack Compose layout APIs, modifier parameters, modifier chain construction, hardcoded root layout decisions, or layout wrappers around a single conditional.

`chrisbanes-skills package`

### compose-recomposition-performance

Use when investigating Jetpack Compose recomposition performance, skippable/restartable composables, composables.txt or compiler reports, Layout Inspector recomposition counts.

`chrisbanes-skills package`

### compose-side-effects

Use when writing or reviewing Jetpack Compose code with LaunchedEffect, DisposableEffect, SideEffect, rememberCoroutineScope, rememberUpdatedState, snapshotFlow, snackbar, navigation, focus requests, analytics, or event Flow collection.

`chrisbanes-skills package`

### compose-slot-api-pattern

Use when designing or reviewing a reusable Jetpack Compose component whose visual regions vary by caller, or when primitive content parameters and boolean shape flags are accumulating.

`chrisbanes-skills package`

### compose-stability-diagnostics

Use when writing or reviewing Jetpack Compose parameter stability, compiler reports, skippability, unstable UI state classes, collection parameters, or Kotlin 2.0+ strong skipping behavior.

`chrisbanes-skills package`

### compose-state-authoring

Use when writing or reviewing Jetpack Compose code with bare local var in a @Composable, remember { mutableStateOf(...) }, mutableStateListOf/mutableStateMapOf, or @ReadOnlyComposable.

`chrisbanes-skills package`

### compose-state-deferred-reads

Use when Jetpack Compose code reads scroll, animation, gesture, or other frame-rate State in composition, passes changing values across composable boundaries.

`chrisbanes-skills package`

### compose-state-hoisting

Use when deciding where Jetpack Compose UI element state or UI logic should live: local remember state, hoisted composable parameters, a plain state holder class, or a screen-level ViewModel/component.

`chrisbanes-skills package`

### compose-state-holder-ui-split

Use when a Jetpack Compose screen-level composable takes a ViewModel/component/controller, collects state or effects, handles navigation/snackbars, or wires callbacks while also rendering layout.

`chrisbanes-skills package`

### compose-ui-testing-patterns

Use when writing or reviewing Jetpack Compose UI tests, screenshot tests, previews, semantics assertions, fake image loading, keyboard input, focus assertions, interaction state.

`chrisbanes-skills package`

### implement-issue

Use when asked to review, fix, implement, resolve, or work through a specific GitHub, GitLab, Jira, or Linear issue reference.

`chrisbanes-skills package`

### kotlin-control-flow

Use when writing or reviewing Kotlin branching and control flow: when expressions, guard conditions, sealed type exhaustiveness, smart casts, nullable branching, early returns, or replacing complex if/else chains.

`chrisbanes-skills package`

### kotlin-coroutines-structured-concurrency

Use when writing or reviewing Kotlin code that stores CoroutineScope, launches from init/non-suspending APIs, calls runBlocking, or catches broad exceptions around suspend calls.

`chrisbanes-skills package`

### kotlin-flow-state-event-modeling

Use when writing or reviewing Kotlin Flow state and event APIs with StateFlow, MutableStateFlow.update, SharedFlow, Channel, stateIn, SharingStarted.

`chrisbanes-skills package`

### kotlin-functions

Use when choosing Kotlin member, top-level, extension, factory, or service functions for String, primitive, collection, Flow, framework, or third-party receivers.

`chrisbanes-skills package`

### kotlin-multiplatform-expect-actual

Use when designing Kotlin Multiplatform expect/actual or interface boundaries for platform services, native SDKs, source sets, Compose Multiplatform UI, permissions, files, settings, sensors, or platform interop.

`chrisbanes-skills package`

### kotlin-types-value-class

Use when writing or reviewing Kotlin type declarations to choose @JvmInline value class over data class where appropriate, including Compose stability implications.

`chrisbanes-skills package`

### shepherd

Use when asked to shepherd, babysit, monitor, or poll open pull requests or merge requests — including triaging review comments, detecting CI failures, fixing trivial CI issues.

`chrisbanes-skills package`

### using-chrisbanes-skills

Use when a Kotlin, Android, or Jetpack Compose task is too broad for any single focused skill to obviously apply, especially for general review, refactor, architecture, state, performance, testing, or UI API design work.

`chrisbanes-skills package`

---

## 3. Design & Visual

### algorithmic-art

Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems.

`/home/mrksvt/.agents/skills/algorithmic-art/SKILL.md`

### banner-design

Design banners for social media, ads, website heroes, creative assets, and print. Multiple art direction options with AI-generated visuals.

`/home/mrksvt/.agents/skills/banner-design/SKILL.md`

### brand

Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, marketing assets, brand compliance, style guides.

`/home/mrksvt/.agents/skills/brand/SKILL.md`

### brand-guidelines

Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel.

`/home/mrksvt/.agents/skills/brand-guidelines/SKILL.md`

### canvas-design

Create beautiful visual art in .png and .pdf documents using design philosophy. Use when the user asks to create a poster, piece of art, design, or other static piece.

`/home/mrksvt/.agents/skills/canvas-design/SKILL.md`

### design

Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini AI), corporate identity program (50 deliverables, CIP mockups), HTML presentations, banner design, icon design, social photos.

`/home/mrksvt/.config/opencode/skills/design/SKILL.md`

### design-system

Token architecture, component specifications, and slide generation. Three-layer tokens (primitive→semantic→component), CSS variables, spacing/typography scales, component specs, strategic slide creation.

`/home/mrksvt/.config/opencode/skills/design-system/SKILL.md`

### frontend-design

Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.

`/home/mrksvt/.agents/skills/frontend-design/SKILL.md`

### slack-gif-creator

Knowledge and utilities for creating animated GIFs optimized for Slack. Use when users request animated GIFs for Slack.

`/home/mrksvt/.agents/skills/slack-gif-creator/SKILL.md`

### theme-factory

Toolkit for styling artifacts with a theme. 10 pre-set themes with colors/fonts that you can apply to any artifact, or generate a new theme on-the-fly.

`/home/mrksvt/.agents/skills/theme-factory/SKILL.md`

### ui-styling

Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, and canvas-based visual designs.

`/home/mrksvt/.config/opencode/skills/ui-styling/SKILL.md`

### ui-ux-pro-max

UI/UX design intelligence with searchable database.

`/home/mrksvt/.config/opencode/skills/ui-ux-pro-max/SKILL.md`

---

## 4. Documents & Content

### content-research-writer

Assists in writing high-quality content by conducting research, adding citations, improving hooks, iterating on outlines, and providing real-time feedback on each section.

`/home/mrksvt/.config/opencode/skills/content-research-writer/SKILL.md`

### doc-coauthoring

Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content.

`/home/mrksvt/.agents/skills/doc-coauthoring/SKILL.md`

### docx

Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files).

`/home/mrksvt/.agents/skills/docx/SKILL.md`

### internal-comms

A set of resources to help write all kinds of internal communications (status reports, leadership updates, company newsletters, FAQs, incident reports, project updates, etc.).

`/home/mrksvt/.agents/skills/internal-comms/SKILL.md`

### pdf

Use this skill whenever the user wants to do anything with PDF files — reading, merging, splitting, watermarks, creating, filling forms, encrypting, extracting images, OCR.

`/home/mrksvt/.agents/skills/pdf/SKILL.md`

### pptx

Use this skill any time a .pptx or .potx file is involved — creating, reading, editing presentations, slide decks, pitch decks.

`/home/mrksvt/.agents/skills/pptx/SKILL.md`

### slides

Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies.

`/home/mrksvt/.config/opencode/skills/slides/SKILL.md`

### xlsx

Use this skill any time a spreadsheet file is the primary input or output (.xlsx, .xlsm, .xltx, .csv, .tsv).

`/home/mrksvt/.agents/skills/xlsx/SKILL.md`

---

## 5. Web & Deployment

### agent-browser

Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task.

`/home/mrksvt/.agents/skills/agent-browser/SKILL.md`

### deploy-to-vercel

Deploy applications and websites to Vercel. Use when the user requests deployment actions like "deploy my app", "deploy and give me the link", "push this live", or "create a preview deployment".

`/home/mrksvt/.agents/skills/deploy-to-vercel/SKILL.md`

### vercel-composition-patterns

React composition patterns that scale. Use when refactoring components with boolean prop proliferation, building flexible component libraries, or designing reusable APIs.

`/home/mrksvt/.agents/skills/vercel-composition-patterns/SKILL.md`

### vercel-react-best-practices

React and Next.js performance optimization guidelines from Vercel Engineering. Use when writing, reviewing, or refactoring React/Next.js code.

`/home/mrksvt/.agents/skills/vercel-react-best-practices/SKILL.md`

### vercel-react-native-skills

React Native and Expo best practices for building performant mobile apps. Use when building React Native components, optimizing list performance, implementing animations, or working with native modules.

`/home/mrksvt/.agents/skills/vercel-react-native-skills/SKILL.md`

### web-artifacts-builder

Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui).

`/home/mrksvt/.agents/skills/web-artifacts-builder/SKILL.md`

### web-design-guidelines

Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX".

`/home/mrksvt/.agents/skills/web-design-guidelines/SKILL.md`

### webapp-testing

Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots.

`/home/mrksvt/.agents/skills/webapp-testing/SKILL.md`

---

## 6. AI / MCP / LLM

### claude-api

Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration.

`/home/mrksvt/.agents/skills/claude-api/SKILL.md`

### customize-opencode

Use ONLY when the user is editing or creating opencode's own configuration: opencode.json, opencode.jsonc, files under .opencode/, or files under ~/.config/opencode/. Also use when creating or fixing opencode agents, subagents, skills, plugins.

`built-in`

### mcp-builder

Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools.

`/home/mrksvt/.agents/skills/mcp-builder/SKILL.md`

### skill-creator

Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill.

`/home/mrksvt/.agents/skills/skill-creator/SKILL.md`

---

## 7. Project Management

### changelog-generator

Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes.

`/home/mrksvt/.agents/skills/changelog-generator/SKILL.md`

### dispatching-parallel-agents

Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies.

`/home/mrksvt/.config/opencode/skills/dispatching-parallel-agents/SKILL.md`

### init-work

Buat atau update folder .work/ berisi PRD.md, Architecture.md, Design.md, Schema.md, Rules.md dari analisa project nyata. Use when user asks to init work, buat dokumentasi project, setup .work/, atau sebelum mulai fitur besar.

`/home/mrksvt/.config/opencode/skills/init-work/SKILL.md`

### meeting-insights-analyzer

Analyzes meeting transcripts and recordings to uncover behavioral patterns, communication insights, and actionable feedback.

`/home/mrksvt/.config/opencode/skills/meeting-insights-analyzer/SKILL.md`

### using-git-worktrees

Use when starting feature work that needs isolation from current workspace or before executing implementation plans.

`/home/mrksvt/.config/opencode/skills/using-git-worktrees/SKILL.md`

---

## 8. Visualization & Analysis

### graphify

Use for any question about a codebase, its architecture, file relationships, or project content. Turns any input (code, docs, papers, images, videos) into a persistent knowledge graph with god nodes, community detection, and query/path/explain tools.

`/home/mrksvt/.claude/skills/graphify/SKILL.md`

### plantuml-skill

Use when user requests diagrams, flowcharts, sequence diagrams, class diagrams, component diagrams, ER diagrams, architecture charts, or visualizations. Generates .puml files and exports to PNG/SVG via Kroki API.

`/home/mrksvt/.config/opencode/skills/plantuml-skill/skills/plantuml-skill/SKILL.md`

### security-research

Team Mode security research skill. Orchestrates 3 vulnerability hunters and 2 PoC engineers to audit a codebase in parallel, prove exploitability, classify root causes.

`/home/mrksvt/.cache/opencode/skills/security-research/SKILL.md`

### security-review

Alias for security-research. Team Mode security research skill.

`/home/mrksvt/.cache/opencode/skills/security-review/SKILL.md`

---

## 9. Utilities

### piper-tts

Local offline text-to-speech via Piper. Speak short status updates, read results aloud, or generate WAV files without network.

`/home/mrksvt/.config/opencode/skills/piper-tts/SKILL.md`

### template-skill

Replace with description of the skill and when Claude should use it.

`/home/mrksvt/.agents/skills/template-skill/SKILL.md`

---

*Dokumen ini dibuat pada 2026-07-30. Total: 62 skill.*
