# Aegis v3.6-stable Runbook & Security Model

## Overview
Aegis v3.6-stable is a fully decoupled, production-ready AI Assistant for Windows. This version introduces deterministic fallbacks, circuit breaking, local SQLite durable writes, and opt-in AI enhancement features.

## Architecture & Decoupling
1. **Planning**: `ContextualPlanner` prepares context -> `LLMClient` (with pybreaker/backoff) generates raw JSON.
2. **Validation**: `plan_validator.py` ensures the structure matches expected schema. `action_normalizer.py` converts legacy arguments (like `value`) to canonical schema params.
3. **Execution**: The `AegisCLI` no longer instantiates actual execution objects. Everything flows through `ExecutionEngine`, outputting canonical dictionaries.

## Security & Telemetry
Aegis logs all events to `logs/data`:
- `aegis.log`: Standard systemic logs.
- `ai_plans.jsonl`: Audit log of all plans generated.
- `approvals.jsonl`: Audit log of user accept/reject decisions.
- `executions.jsonl`: Audit log of final command execution results.
- `migration.log`: Tracks database schema progressions.

## Environment Variables
- `GROQ_API_KEY`: Required for cloud LLM usage.
- `AEGIS_OFFLINE_MODE`: Set to `true` to force a mocked local fallback mode, useful for CI or air-gapped systems.
- `GROQ_MODEL`: Can override the default Llama 3.3 model.

## Opt-In Modes (Beta)
- **Dashboard**: Run `fastapi dev ui/dashboard.py` to view AI decisions live.
- **Memory**: FAISS vector integration available in `memory/vector_store.py`.
