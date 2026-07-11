"""
Estado global persistente del bot.
Todas las variables se guardan automáticamente en gui_state.json
"""
import json
import os
from pathlib import Path

# Path al archivo de persistencia
STATE_FILE = Path(__file__).parent / "gui_state.json"

# ============ VARIABLES GLOBALES ============
# GUI Settings
swipe_dx = 0
swipe_dy = 400
attacks_per_cycle = 2
debug_mode = False

# ============ FUNCIONES DE PERSISTENCIA ============

def load_state():
    """Cargar el estado desde el archivo JSON."""
    global swipe_dx, swipe_dy, attacks_per_cycle, debug_mode
    
    if not STATE_FILE.exists():
        return
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cargar GUI settings
        swipe_dx = data.get("swipe_dx", 0)
        swipe_dy = data.get("swipe_dy", 400)
        attacks_per_cycle = data.get("attacks_per_cycle", 2)
        debug_mode = data.get("debug_mode", False)
        
    except Exception as e:
        print(f"Error cargando estado: {e}")


def save_state():
    """Guardar el estado en el archivo JSON."""
    data = {
        "swipe_dx": swipe_dx,
        "swipe_dy": swipe_dy,
        "attacks_per_cycle": attacks_per_cycle,
        "debug_mode": debug_mode,
    }
    
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error guardando estado: {e}")


def set_swipe_values(dx, dy):
    """Actualizar valores de swipe."""
    global swipe_dx, swipe_dy
    swipe_dx = int(dx) if isinstance(dx, str) else dx
    swipe_dy = int(dy) if isinstance(dy, str) else dy
    save_state()


def set_attacks(num):
    """Actualizar número de ataques por ciclo."""
    global attacks_per_cycle
    attacks_per_cycle = int(num) if isinstance(num, str) else num
    save_state()


def set_debug(enabled):
    """Actualizar modo debug."""
    global debug_mode
    debug_mode = bool(enabled)
    save_state()


# Cargar estado al importar el módulo
load_state()
