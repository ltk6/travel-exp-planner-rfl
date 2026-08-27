# INC-001 — Groq Mass Model Deprecation

| Field | Value |
|---|---|
| **Date** | 2026-08-27 |
| **Type** | Vendor Incident |
| **Status** | Resolved |
| **Severity** | High — primary LLM chain broken; service non-functional until config updated |
| **Affected Components** | N5 (activity generation), N17 (feedback processing) |
| **Resolution Time** | < 1 hour (detected and resolved same session) |

---

## Summary

Groq deprecated the majority of models used in the N5 and N17 LLM provider chains without a scheduled migration window communicated in advance. The two primary models (`llama-3.3-70b-versatile` and `llama-3.1-8b-instant`) were removed from the supported model list. Any call reaching those models would fail at the API level, causing N5 activity generation and N17 feedback processing to return errors for all LLM-dependent endpoints (`/activities`, `/feedback/activities`).

---

## Timeline

| Time | Event |
|---|---|
| Pre-Phase 0 | `meta-llama/llama-4-scout-17b` deprecated by Groq; removed from chain before baseline work began. No impact recorded. |
| 2026-08-27 | Groq deprecated `llama-3.3-70b-versatile` and `llama-3.1-8b-instant`. Discovered during Phase 1 close review. |
| 2026-08-27 | Surviving model list confirmed from Groq console. Chain reconstructed. |
| 2026-08-27 | n5/config.py and n17/config.py updated. Incident logged. Docker build verified passing. |

---

## Impact

- `/activities` and `/feedback/activities` endpoints would return LLM errors on any request hitting a deprecated model.
- `/locations`, `/explore`, `/health` endpoints unaffected (no LLM dependency).
- N1 embedding service unaffected.
- No data loss. No database corruption.

---

## Root Cause

External vendor (Groq) deprecated supported models without advance notice to free-tier users. The project had no abstraction layer or monitoring to detect model availability changes — model names were hardcoded directly in config files with no fallback to a verified-available model.

The roadmap assumed a stable vendor platform for the duration of Phase 0-2. This assumption was not validated and was not listed as an explicit risk.

---

## Resolution

Surviving model list confirmed from Groq console:

| Model | TPM | RPD | Token/Day |
|---|---|---|---|
| qwen/qwen3.6-27b | 8K | 1K | 200K |
| qwen/qwen3.8-27b | 8K | 1K | 2M |
| openai/gpt-oss-120b | 8K | 1K | 200K |
| openai/gpt-oss-20b | 8K | 1K | 200K |

Updated LLM_CHAIN in both N5 and N17:

    qwen/qwen3.6-27b -> qwen/qwen3.8-27b -> openai/gpt-oss-120b -> openai/gpt-oss-20b

---

## Consequences & Risk Forward

The surviving chain caps at 8K tokens per minute across all models. This is materially more constrained than the deprecated llama-70b primary. This worsens the Phase 3 load test conditions — which is useful: rate exhaustion is now easier to trigger deliberately, strengthening the circuit breaker hypothesis.

Risk of further deprecation remains. All model names are isolated in two config files (n5/config.py, n17/config.py). A future swap requires a one-line change per file.

---

## Action Items

| Action | Status | Phase |
|---|---|---|
| Add vendor platform stability to risk register | Done | Phase 0 close |
| Isolate model names to config only — no hardcoding elsewhere | Done | Phase 0 close |
| Validate surviving chain produces correct output format | Pending | Phase 2 smoke tests |
| Add model availability check to /health/deep endpoint | Proposed | Phase 6 (circuit breaker sprint) |
