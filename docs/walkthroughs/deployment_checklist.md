# Aegis v7.0 Deployment Checklist

### Pre-Flight (Local Environment)
- [ ] Ensure Python 3.9+ is installed.
- [ ] Run `pip install -r requirements.txt` (Core dependencies).
- [ ] (Optional) Install `ultralytics`, `torch`, `opencv-python` for Vision features.
- [ ] (Optional) Install `pyttsx3`, `SpeechRecognition` for Voice features.

### Configuration
- [ ] Review `config/config.yaml` for `ACTION_WHITELIST`.
- [ ] Verify `MEMORY_DB_PATH` is accessible.
- [ ] Ensure `logs/` directory is writable.

### Security Check
- [ ] Verify `security/validator.py` is active.
- [ ] Test a HIGH risk action (e.g., PowerShell delete) to ensure approval gate triggers.

### Smoke Test
- [ ] Run `python main.py --mode cli`.
- [ ] Type `open notepad`. Verify focus and verification pass.
- [ ] Type `search who is the CEO of Google`. Verify browser opens search results.

### Production Promotion
- [ ] Run `pytest tests/test_v7_comprehensive.py`.
- [ ] Review `diagnostics.zip` for any anomalies.
- [ ] promote to `master` branch.
