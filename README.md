# Aegis – Desktop Operating Intelligence

Aegis is an intelligent desktop automation framework that turns natural language commands into real OS actions. Unlike simplistic voice assistants, Aegis plans multi‑step strategies, validates security, and verifies each action’s success – no hallucinations.

## Capabilities
- 🚀 Launch any application (verified process creation)
- 🌐 Browser automation (search, open first result)
- 👁️ Vision & OCR (click text on screen, read dialogs)
- 🎤 Voice I/O (speak & listen – optional)
- 🔧 System control (hotspot, brightness, device manager)
- 📁 File organization (scan, group, suggest structure)

## Tech Stack
- Python 3.9+, psutil, pyautogui, OpenCV, pytesseract, rapidfuzz
- Playwright, BeautifulSoup, screen‑brightness‑control
- Modular architecture: Planner → Security → Action Dispatcher → Verification

## Status
✅ Core operational – actively used for daily automation tasks.  
⚠️ Voice & advanced vision require optional dependencies (see install guide).

## Quick Start
```bash
git clone https://github.com/yourusername/aegis.git
cd aegis
pip install -r requirements.txt
playwright install
python main.py
