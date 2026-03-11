# Aegis v3.6.1 — Upgrade Report

## Fixed Issues

### Critical API Mismatches (Runtime Crashes)

| Issue | Location | Root Cause | Fix |
|---|---|---|---|
| `MemoryManager.get_user_profile()` missing | `contextual_planner.py:240` | Method never implemented | Added with DB table + legacy JSON fallback |
| `MemoryManager.set_preference()` missing | `preference_store.py:46,58,72` | Method never implemented | Added with `preferences` table |
| `MemoryManager.get_preference()` missing | `preference_store.py:42,51,62` | Method never implemented | Added with default fallback |

### Schema Gaps

| Table | Purpose | Migration |
|---|---|---|
| `preferences` | Key-value store for user preferences | v3 migration |
| `user_profile` | Single-row profile with behavioral data | v3 migration + legacy JSON import |

### Version & Config

- Bumped `AEGIS_VERSION` from `v3.6-stable` → `v3.6.1`
- Fixed hardcoded DB path in health endpoint (`main.py`) → uses `MEMORY_DB_PATH` from config

---

## New Features

### User Profile API
- `get_user_profile()` — returns dict, never raises, falls back to legacy JSON
- `set_user_profile(profile)` — full upsert
- `update_user_profile(patch)` — merge patch into existing profile
- `_load_user_profile_from_db()` — internal DB loader
- `_load_legacy_profile_json()` — internal JSON fallback

### Preferences API
- `get_preference(key, default)` — safe read with default
- `set_preference(key, value)` — upsert with commit

### DB Migration v3
- Auto-creates `preferences` and `user_profile` tables
- Imports legacy `user_profile.json` during migration and deletes original

---

## Test Coverage

```
58 passed in 4.69s
```

| Suite | Tests | Status |
|---|---|---|
| `test_memory_user_profile.py` | 9 | ✅ All pass |
| `test_memory.py` | 6 | ✅ All pass |
| `test_logger.py` | 6 | ✅ All pass |
| `test_plan_validation.py` | 3 | ✅ All pass |
| `test_cli_flow.py` | 1 | ✅ All pass |
| `test_llm_offline_mode.py` | 1 | ✅ All pass |
| `test_db_migration.py` | 3 | ✅ All pass |
| `test_validator.py` | 14 | ✅ All pass |
| `integration/test_open_app_flow.py` | 2 | ✅ All pass |
| `integration/test_malformed_llm_recovery.py` | 4 | ✅ All pass |
| `integration/test_offline_mode.py` | 2 | ✅ All pass |
| **Total** | **58** | **✅ 58/58** |

---

## Files Modified

| File | Change |
|---|---|
| `memory/memory_manager.py` | Added preferences table, user_profile table, 7 new methods, migration v3 |
| `config.py` | Version bump to v3.6.1 |
| `main.py` | Fixed health endpoint DB path, version to v3.6.1 |
| `tests/test_memory.py` | Updated for v3.6 API |
| `tests/test_logger.py` | Updated for v3.6 API |
| `tests/test_db_migration.py` | Updated for schema v3 |

## Files Created

| File | Purpose |
|---|---|
| `tests/test_memory_user_profile.py` | User profile + preferences tests |
| `tests/integration/__init__.py` | Integration test package |
| `tests/integration/test_open_app_flow.py` | Open app e2e flow |
| `tests/integration/test_malformed_llm_recovery.py` | Malformed LLM recovery |
| `tests/integration/test_offline_mode.py` | Offline mode validation |

---

## Known Limitations & Next Steps
- Vector store (`memory/vector_store.py`) is a skeleton — needs FAISS integration
- Plugin system (`skills/__init__.py`) is a shell — needs plugin loader
- Dashboard (`ui/dashboard.py`) is minimal — needs auth and real-time updates
- Consider adding `test_health_endpoint.py` for HTTP-level verification
