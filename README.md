# Trantor-BB-CoC-Bot


# ⚠️ Development Status

This is an active work-in-progress.

The repository currently contains a mix of new code and legacy code from previous versions while the project is being refactored.

Expect:
- Unused functions
- Duplicate code
- Temporary debug utilities
- Incomplete features
- Frequent breaking changes

The project is being cleaned and reorganized as the core functionality evolves.

## Current Scope

This project currently focuses on **Builder Base farming**.

The standard farming mode follows a simple strategy:
- Find a match.
- Deploy a few troops.
- Surrender immediately.
- Repeat.
- After a cycle of X attacks check if Elixir store is full to Stop.

A second **full attack mode is currently in Beta**. It deploys troops and waits for the battle to finish instead of surrendering immediately. This mode is still being validated and is not yet considered stable.

It is **not** intended to perform intelligent attacks or maximize trophies.
Future versions may include more advanced attack strategies, but that is not the current objective.

## Features

- 🤖 Automated Builder Base attacks
- ⚔️ Two attack modes: immediate surrender and full battle (Beta)
- ⚙️ Persistent configuration through the GUI
- 📱 ADB device control
- 👁️ Computer vision with OpenCV
- 🎯 Relative coordinates for any emulator resolution

## Roadmap

Current goals:
- Continue improving attack logic and battle flow.
- Continue refactoring remaining legacy code.
- Improve and expand configuration options.
- Develop more robust battle-state detection.

## Disclaimer

This bot is for educational purposes only. Use at your own risk.  
Automating gameplay may violate Clash of Clans' Terms of Service.

Este bot es solo para fines educativos. Úsalo bajo tu propia responsabilidad.
Automatizar el juego puede violar los Términos de Servicio de Clash of Clans.

## Requirements
- Python 3
- Project dependencies: `pip install -r requirements.txt`
- ADB configured and connected to the emulator

## Tested Environment
The project is currently developed and tested on:

- Windows 10
- Python 3.x
- LDPlayer emulator
- ADB

## Usage
```bash
python main.py
```

## Notes
- The bot uses the emulator resolution to adjust taps and swipes.
- The main project files include `main.py`, `func.py`, and `attacks.py`.
