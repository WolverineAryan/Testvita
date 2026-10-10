# CodeVita AI Coach — AI Layer & Prompt Architecture

## 1. Core Principle
The Large Language Model is **never** the sole source of truth for calculations or skill analytics.
- **Deterministic Engines First**: Accuracy, confidence, topic mastery scores, and prioritization weights are computed deterministically.
- **Structured AI Generation**: The AI layer transforms calibrated numerical metrics into actionable day-by-day tasks and contextual advice.

---

## 2. AI Provider Abstraction (`AIProvider`)
The application defines an abstract interface `AIProvider` in `app/ai/provider.py`:
- `generate_text(system_prompt: str, user_prompt: str) -> str`
- `generate_structured(system_prompt: str, user_prompt: str, schema: str) -> dict`

### Implementations:
- **`NvidiaNemotronAIProvider`**: Powered by NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`) utilizing high-parameter Nemotron models (`nvidia/llama-3.1-nemotron-70b-instruct` / `nvidia/nemotron-4-340b-instruct`). Provides high-precision competitive programming coaching, reasoning, code reviews, and JSON-structured daily study plan generation.
- **`MockAIProvider`**: Built-in deterministic heuristic provider guaranteeing 100% functionality and test pass rate even in zero API key / offline environments.

---

## 3. Dedicated Prompt Templates (`app/ai/prompts/`)
- `planner.py`: System instructions for formulating day-by-day task schedules.
- `tutor.py`: Socratic conversational tutor preventing immediate code disclosure and fostering algorithmic discovery.
- `review.py`: Automated code review assessing time complexity, memory footprint, edge cases, and optimization.
- `analysis.py`: Mock exam debrief summarizing time sinks and next study steps.

---

## 4. Prompt Injection Defense
- Problem statements, submitted user code, and custom inputs are sanitized and quarantined as untrusted inputs inside delimited context blocks.
- System prompt instructions cannot be overridden by user problem notes.
