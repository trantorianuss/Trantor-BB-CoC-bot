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

Cleaning and reorganizing the code is planned before the first stable release.

This repository intentionally contains work-in-progress code. Cleaning and code organization will happen once the core functionality is complete.

## Current Scope

This project currently focuses on **Builder Base farming**.

The bot follows a very simple strategy:
- Find a match.
- Deploy a few troops.
- Surrender immediately.
- Repeat.
- After a cycle of X attacks check if Elixir store is full to Stop 

It is **not** intended to perform intelligent attacks or maximize trophies.
Future versions may include more advanced attack strategies, but that is not the current objective.

## Features

- 🤖 Automated Builder Base attacks
- 📱 ADB device control
- 👁️ Computer vision with OpenCV
- 🎯 Relative coordinates for any emulator resolution

## Roadmap

Current goals:
- Improve attack logic.
- Complete code refactoring.
- Remove legacy code.
- Improve configuration system.
- Better logging.


## Disclaimer

This bot is for educational purposes only. Use at your own risk.  
Automating gameplay may violate Clash of Clans' Terms of Service.

Este bot es solo para fines educativos. Úsalo bajo tu propia responsabilidad.
Automatizar el juego puede violar los Términos de Servicio de Clash of Clans.


## Requisitos
- Python 3
- Dependencias del proyecto: `pip install -r requirements.txt`
- ADB configurado y conectado al emulador

## Ejecución
```bash
python main.py
```

## Notas
- El bot usa la resolución del emulador para ajustar los taps y swipes.
- Puedes revisar el código en los archivos principales como `main.py`, `func.py` y `attacks.py`.
