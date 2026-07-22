---
name: model-router
description: Automate model selection for OpenCode agents and categories based on task type. Reads current config (oh-my-openagent.json), lists available models, then maps tasks to the best model via agent/category matching. Use when user asks "which model should I use for X?", wants to switch models, optimize model selection, or needs to route a task to the right agent-model pair.
---

# Model Router Skill

## What This Skill Does

Given a task description, this skill:
1. Reads `~/.config/opencode/oh-my-openagent.json` for current agent/category config
2. Runs `opencode models` to see available models
3. Maps the task to the correct agent or category
4. Recommends the best available model + variant
5. Provides the exact config snippet to apply

## Step 0 — Understand the Two Routing Paths

| Path | When | Model Comes From |
|------|------|-----------------|
| **Agent route** | You need a specific agent (Sisyphus, Oracle, Hephaestus, Explore, Librarian) | `oh-my-openagent.json` → `agents.<name>.model` + fallback chain |
| **Category route** | Delegating work via `task(category="...")` | `oh-my-openagent.json` → `categories.<name>.model` + fallback chain |

**Key insight**: The orchestrator picks the agent/category. The model is a consequence of that choice. You route the *task type* → *agent/category*, and the model follows.

**But**: Some agents need specific model families. Hephaestus MUST have GPT-family. Sisyphus MUST have Claude/Kimi/GLM family. Category `visual-engineering` MUST have Gemini/Qwen family.

## Step 1 — Analyze the Task

Read the user's task description. Classify it:

| Task Signature | Agent to Use | Category to Delegate | Required Model Family |
|---|---|---|---|
| Orchestration, delegation planning, multi-step coordination | Sisyphus (self) | — | Claude / Kimi / GLM / GPT-5.4+ |
| Architecture decision, tradeoff analysis, hard debugging | Oracle | — | GPT-5.5 (preferred) or Gemini/Claude/GLM fallback |
| Goal-oriented autonomous deep work | Hephaestus | `deep` | GPT-5.5 (required) |
| Maximum reasoning, hard logic | — | `ultrabrain` | GPT-5.5 (xhigh) or Gemini/Claude fallback |
| Creative, unconventional problem-solving | — | `artistry` | Gemini-3.1-Pro (required) or Claude Opus fallback |
| Frontend, UI, CSS, styling, design | — | `visual-engineering` | Gemini-3.1-Pro (preferred) or Qwen fallback |
| Simple single-file fix, typo, trivial change | — | `quick` | GPT-5.4-mini (preferred) or Claude Haiku/MiniMax fallback |
| General complex work (no specific category) | — | `unspecified-high` | Claude Opus (preferred) or GPT-5.5/GLM/Kimi fallback |
| General simple work (no specific category) | — | `unspecified-low` | Kimi K2.6 (user config) or Claude/Kimi fallback |
| Documentation, prose, technical writing | — | `writing` | Kimi K2.6 (user config) or Gemini Flash/Claude fallback |
| Search codebase, grep, find patterns | Explore | — | GPT-5.4-mini-fast (preferred) or Qwen/MiniMax fallback |
| Search docs, external references, OSS examples | Librarian | — | Same as Explore chain |
| Multimodal, screenshots, vision | Multimodal-Looker | — | GPT-5.5 (preferred) or Kimi/GLM fallback |

## Step 2 — Check Current Config

Run: Read `~/.config/opencode/oh-my-openagent.json`

Extract:
- `agents.<name>.model` — current explicit model (if set, this wins)
- `agents.<name>.variant` — current variant
- `categories.<name>.model` — current category model
- `categories.<name>.variant` — current category variant

## Step 3 — Check Available Models

Run: `opencode models` (list all available `provider/model`)

Match required model family against available models:

| Family | Models in User's 9router Provider | Notes |
|---|---|---|
| Claude | `9router/Claude`, `9router/Claude_Opus`, `9router/Claude_Sonnet`, `9router/Claude_Haiku`, `9router/Claude4.5_Haiku`, `9router/Claude4.5_Sonnet`, `9router/Claude4.6_Opus`, `9router/Claude4.6_Sonnet`, `9router/Claude4.7_Opus` | Variants: `max`, `high`, `medium`, `low`, `xhigh` |
| Kimi | `9router/iamhc/Kimi-K2.6`, `9router/nvidia/moonshotai/kimi-k2.6`, `9router/nararouter/kimi-k2.7-code-free` | K2.7 newest, K2.6 stable |
| GLM | `9router/iamhc/glm-5.2`, `9router/kr/glm-5` | GLM-5.2 newest |
| GPT | Not available in 9router | No direct GPT access — use Kimi/GLM as Claude-like fallback for GPT-dependent agents |
| Gemini | Not available in 9router | No direct Gemini access — use Qwen as visual fallback |
| Qwen | `9router/iamhc/Qwen3-Coder-Next-FP8`, `9router/iamhc/Qwen3.5-397B-A17B`, `9router/kr/qwen3-coder-next` | Qwen3-Coder-Next for visual/coding tasks |
| MiniMax | `9router/iamhc/MiniMax-M3`, `9router/nvidia/minimaxai/minimax-m3` | Fast utility model, M3 flagship |
| DeepSeek | `9router/iamhc/DeepSeek-V4-Pro`, `9router/iamhc/DeepSeek-V4-Flash` | GPT-like autonomous behavior for `deep`/`ultrabrain` |
| MiMo | `9router/nararouter/mimo-v2.5-pro`, `opencode/mimo-v2.5-free` | Utility/quick tasks |
| Mistral | `9router/nvidia/mistralai/mistral-large-3-675b-instruct-2512` | General purpose |
| Spark | `9router/iamhc/Spark-X2-Flash` | Fast utility |
| SenseNova | `9router/iamhc/sensenova-u1-fast` | Fast utility |
| Kat Coder | `9router/iamhc/kat-coder-pro-v2` | Coding specialist |

## Step 4 — Match (Task + Available Models → Best Selection)

### Routing Decision Tree

```
Task type?
├─ Orchestration / planning / delegation → Sisyphus agent
│   ├─ Claude available? → 9router/Claude4.7_Opus (max) | 9router/Claude4.6_Opus (max) | 9router/Claude_Opus (max)
│   ├─ Kimi available? → 9router/nararouter/kimi-k2.7-code-free | 9router/iamhc/Kimi-K2.6
│   ├─ GLM available? → 9router/iamhc/glm-5.2 | 9router/kr/glm-5
│   └─ Bottom fallback → 9router/iamhc/DeepSeek-V4-Pro (NOT recommended, but better than nothing)
│
├─ Deep autonomous work → Hephaestus or category=deep
│   ├─ No GPT available → Use DeepSeek as nearest GPT-family substitute
│   │   Hephaestus: model="9router/iamhc/DeepSeek-V4-Pro"
│   │   deep category: model="9router/iamhc/DeepSeek-V4-Pro", variant="high"
│   └─ WARNING: Claude/Kimi are WRONG for Hephaestus. Hephaestus prompt is GPT-tuned.
│       If no GPT, use DeepSeek or disable Hephaestus entirely.
│
├─ Architecture / debugging consultation → Oracle
│   ├─ DeepSeek-V4-Pro (high) — best GPT-substitute for reasoning
│   ├─ Claude4.7_Opus (max) — strong reasoning fallback
│   └─ GLM-5.2 (high) → Kimi K2.6
│
├─ Max reasoning → ultrabrain category
│   └─ 9router/iamhc/DeepSeek-V4-Pro (xhigh) — closest GPT-5.5 substitute
│
├─ Visual / frontend / UI → visual-engineering category
│   ├─ No Gemini → Use Qwen as best visual substitute
│   │   9router/iamhc/Qwen3-Coder-Next-FP8 (high) | 9router/kr/qwen3-coder-next (high)
│   └─ Qwen not enough? → Claude4.6_Sonnet (medium) as last resort (wrong reasoning style)
│
├─ Creative / artistry → artistry category
│   ├─ 9router/Claude4.7_Opus (max) — best creative reasoning without Gemini
│   ├─ 9router/iamhc/DeepSeek-V4-Pro (medium) — alternative
│   └─ WARNING: This category requires Gemini family. Performance will degrade.
│
├─ Quick / trivial → quick category
│   ├─ 9router/nararouter/mimo-v2.5-pro — current user config, fast utility
│   ├─ 9router/iamhc/MiniMax-M3 — MiniMax flagship, fast
│   ├─ 9router/Claude_Haiku — cheap Claude
│   └─ 9router/iamhc/Spark-X2-Flash — ultra-fast
│
├─ General complex → unspecified-high
│   ├─ 9router/Claude_Opus (max) | 9router/Claude4.7_Opus (max)
│   └─ 9router/iamhc/DeepSeek-V4-Pro → 9router/kr/glm-5 → Kimi K2.6
│
├─ General simple → unspecified-low
│   └─ 9router/nararouter/mimo-v2.5-pro | 9router/iamhc/MiniMax-M3
│
├─ Writing / docs → writing category
│   └─ 9router/Claude_Sonnet | 9router/iamhc/DeepSeek-V4-Pro | 9router/nararouter/mimo-v2.5-pro
│
├─ Codebase grep / search → Explore agent
│   ├─ 9router/nararouter/mimo-v2.5-pro — current user config, good for search
│   └─ 9router/iamhc/MiniMax-M3 → 9router/iamhc/Qwen3-Coder-Next-FP8 → 9router/Claude_Haiku
│
├─ External docs/references → Librarian agent
│   └─ Same as Explore chain
│
└─ Screenshots / vision → Multimodal-Looker agent
    └─ 9router/iamhc/DeepSeek-V4-Pro (medium) | 9router/Claude_Haiku (medium) | Kimi K2.6
```

## Step 5 — Produce Config Snippet

Output the exact `oh-my-openagent.json` snippet to apply. Format:

```jsonc
// For agent override:
"agents": {
  "<agent-name>": {
    "model": "<provider/model>",
    "variant": "<max|high|medium|low|xhigh>"
  }
}

// For category override:
"categories": {
  "<category-name>": {
    "model": "<provider/model>",
    "variant": "<max|high|medium|low|xhigh>"
  }
}
```

### Variant Rules

| Variant | When to Use |
|---------|------------|
| `max` | Orchestrator (Sisyphus), max reasoning (Oracle/Momus), anything needing full context window |
| `xhigh` | ultrabrain, Momus review, highest-effort reasoning |
| `high` | Architecture (Oracle), visual-engineering, artistry, unspecified-high |
| `medium` | Deep work (Hephaestus, deep category), Multimodal-Looker, general tasks |
| `low` | Quick tasks, Explore/Librarian, unspecified-low, writing |

**Note on 9router**: Variants may be limited. The system downgrades to closest supported. Check `opencode models` for variant support.

## Step 6 — Switching Models at Runtime

Two ways:

### Method A: Config Edit (persistent)
Edit `~/.config/opencode/oh-my-openagent.json` directly. Takes effect on next agent spawn.

### Method B: OpenCode UI (temporary)
In OpenCode TUI, use model selector dropdown. This overrides config only for the main agent session.

## Hard Constraints (NEVER Violate)

1. **Hephaestus = GPT-family ONLY**. Never route Hephaestus to Claude/Kimi/MiniMax. If no GPT, use DeepSeek or disable.
2. **visual-engineering = Gemini/Qwen ONLY**. Never route visual work to Claude/Kimi/GLM.
3. **artistry = Gemini-family preferred**. Claude Opus is acceptable fallback; GPT is third.
4. **Explorers stay cheap**. Never put Opus/Max models on Explore/Librarian — that's hiring a senior engineer to run grep.
5. **DeepSeek is GPT-substitute, not Claude-substitute**. Use for `deep`, `ultrabrain`, Oracle. NOT for Sisyphus orchestration.
6. **Sisyphus NEVER on MiniMax/Qwen**. These models cannot hold the 1100-line orchestration prompt.

## Anti-Patterns

- "Just use Opus for everything" — wastes $ on grep/search tasks
- "Gemini for code" — wrong family, visual specialist
- "Kimi for Hephaestus" — wrong prompt family, Hephaestus expects GPT principles
- "MiniMax for orchestration" — cannot handle Sisyphus prompt complexity
- Ignoring variant — `max` on a search agent wastes context window

## Quick Reference: User's Current Config

From `oh-my-openagent.json`, the user's current setup (9router-only, no GPT/Gemini):

| Agent | Current Model | Fallback |
|-------|--------------|----------|
| Sisyphus | `9router/VSCode_Codex` (max) | Claude Sonnet → Mistral Large |
| Sisyphus-Junior | `9router/nararouter/mistral-large` | Kimi K2.7 |
| Hephaestus | `9router/VSCode_Codex` (medium) | Codex OpenAI → Mistral Large |
| Oracle | `9router/VSCode_Codex` (high) | Claude Opus → Claude Sonnet → Mistral |
| Prometheus | `9router/VSCode_Codex` (max) | Claude Sonnet → Mistral Large |
| Metis | `9router/Claude_Sonnet` | VSCode_Codex (high) → Mistral Large |
| Momus | `9router/VSCode_Codex` (xhigh) | Claude Opus → Mistral Large |
| Atlas | `9router/nararouter/mistral-large` | GPT_NoCodex (medium) |
| Librarian | `9router/nararouter/mimo-v2.5-pro` | Mistral Large |
| Explore | `9router/nararouter/mimo-v2.5-pro` | Mistral Large |
| Multimodal | `9router/Claude_Haiku` (medium) | Qwen3-Coder-Next → Mistral Large |

| Category | Current Model | Fallback |
|----------|--------------|----------|
| visual-engineering | `9router/Claude_Haiku` (high) | Qwen3-Coder-Next (max) |
| ultrabrain | `9router/kr/qwen3-coder-next` (xhigh) | Claude Opus → Mistral Large |
| deep | `9router/nararouter/mistral-large` (medium) | Qwen3-Coder-Next (max) → GPT_NoCodex |
| artistry | `9router/nararouter/mimo-v2.5-pro` (high) | Claude Sonnet → Mistral Large |
| quick | `9router/nararouter/mimo-v2.5-pro` | Mistral Large → Claude Haiku |
| unspecified-low | `9router/nararouter/mimo-v2.5-pro` | Mistral Large |
| unspecified-high | `9router/nararouter/mistral-large` | Qwen3-Coder-Next (medium) |
| writing | `9router/nararouter/mimo-v2.5-pro` | Mistral Large |

## Suggested Improvements to Current Config

Based on available 9router models, these changes would improve model-task matching:

1. **`deep` category**: Change to `9router/iamhc/DeepSeek-V4-Pro` (high) — DeepSeek is better GPT-substitute than Mistral for autonomous coding
2. **`ultrabrain` category**: Change to `9router/iamhc/DeepSeek-V4-Pro` (xhigh) — DeepSeek > Qwen for max reasoning
3. **Oracle agent**: Change to `9router/iamhc/DeepSeek-V4-Pro` (high) — DeepSeek is best reasoning model without GPT
4. **Hephaestus agent**: Change to `9router/iamhc/DeepSeek-V4-Pro` (medium) — only valid GPT-substitute; VSCode_Codex may not have GPT characteristics
5. **`visual-engineering` category**: Keep `9router/kr/qwen3-coder-next` (high) — Qwen is best visual alternative to Gemini
6. **Explore/Librarian**: Keep `9router/nararouter/mimo-v2.5-pro` — fast/cheap, appropriate for search
7. **`quick` category**: Add `9router/iamhc/MiniMax-M3` as fast option