# 🛡️ Aegis v2.0 — State-Aware AI Assistant for Windows

> **AI that understands your system context, remembers your preferences, and NEVER acts without approval.**

Aegis v2.0 upgrades the stateless CLI assistant into a state-aware supervised operating intelligence with persistent memory, contextual planning, and a background sleep mode.

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.13.x** — [Download](https://www.python.org/downloads/)
- **Google Gemini API Key** — [Get yours here](https://aistudio.google.com/app/apikey)

### Setup

```bash
# 1. Navigate to the project
cd D:\Aegis

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Add your GEMINI_API_KEY to .env

# 5. Launch Aegis (CLI Mode)
python main.py

# 6. Launch Aegis (Background Mode)
python main.py --mode background
```

---

## 🌟 New in v2.0 (Phase 2)

### 🧠 Contextual Planning
Aegis now sees what you see. Before planning, it gathers:
- **System Health:** CPU, RAM, and Disk metrics.
- **Active Environment:** Foreground application and all open window titles.
- **Process Awareness:** Detects if an application is already running to avoid redundant "open" commands.
- **Memory History:** Learns from your previous approvals and rejections.

### 💾 Persistent Memory
Powered by SQLite, Aegis maintains an advisory history:
- **Approved/Rejected Actions:** Tracks what you liked and what you didn't.
- **App Usage Stats:** Remembers your most frequently used tools.
- **User Preferences:** Stores personalized settings.

### 💤 Background Sleep Mode
A new tray-resident daemon allows Aegis to stay active while staying out of the way.
- **Wake Hotkey:** Press `Ctrl+Alt+A` to wake Aegis instantly.
- **Tray Icon:** Monitor status and exit gracefully from the system tray.
- **Zero Auto-Execution:** Even in background mode, Aegis *always* asks for approval before acting.

---

## 🏗️ Architecture

```
aegis/
├── background/             # NEW: Tray daemon & global hotkeys
├── brain/                  # AI Brain Layer (ContextualPlanner)
├── core/                   # NEW: System awareness & registry
├── execution/              # Execution Engine (Actions)
├── interfaces/             # User Interfaces (v2 CLI)
├── memory/                 # NEW: SQLite persistence layer
├── security/               # Security Layer (Untouched)
├── logs/                   # Structured logging
├── tests/                  # v2 Test Suite
├── config.py               # v2 Configuration
└── main.py                 # Multi-mode entry point
```

---

## 🔒 Security Integrity
Aegis v2.0 maintains 100% of the original security guarantees. The **security pipeline** (Validator → Approval Gate → Execution Engine) is immutable. The new memory and context layers are **advisory only** and cannot bypass validation.

---

## 🧪 Testing

Aegis v2.0 includes a comprehensive test suite covering all new modules:
```bash
python -m pytest tests/ -v
```

---

## 📜 License
Personal use only. Built for safety and intelligence.
