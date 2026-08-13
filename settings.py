"""
Estado global persistente del bot.
Todas las variables se guardan automáticamente en gui_state.json
"""
import json
import os
import random
from pathlib import Path

# Path al archivo de persistencia
STATE_FILE = Path(__file__).parent / "gui_state.json"

# ============ VARIABLES GLOBALES ============
# GUI Settings
swipe_dx = 0
swipe_dy = 400
attacks_min_per_cycle = 2
attacks_max_per_cycle = 4
extra_troops_min = 0
extra_troops_max = 4
debug_mode = False

# ============ FUNCIONES DE PERSISTENCIA ============

def load_state():
    """Cargar el estado desde el archivo JSON."""
    global swipe_dx, swipe_dy, attacks_min_per_cycle, attacks_max_per_cycle
    global extra_troops_min, extra_troops_max, debug_mode
    
    if not STATE_FILE.exists():
        return
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cargar GUI settings
        swipe_dx = data.get("swipe_dx", 0)
        swipe_dy = data.get("swipe_dy", 400)

        if "attacks_min_per_cycle" in data or "attacks_max_per_cycle" in data:
            attacks_min_per_cycle = data.get("attacks_min_per_cycle", attacks_min_per_cycle)
            attacks_max_per_cycle = data.get("attacks_max_per_cycle", attacks_max_per_cycle)
        else:
            legacy_value = data.get("attacks_per_cycle", 2)
            attacks_min_per_cycle = int(legacy_value)
            attacks_max_per_cycle = int(legacy_value)

        extra_troops_min = data.get("extra_troops_min", 0)
        extra_troops_max = data.get("extra_troops_max", 4)
        if not _valid_non_negative_range(extra_troops_min, extra_troops_max):
            extra_troops_min = 0
            extra_troops_max = 4

        debug_mode = data.get("debug_mode", False)
        
    except Exception as e:
        print(f"Error cargando estado: {e}")


def save_state():
    """Guardar el estado en el archivo JSON."""
    data = {
        "swipe_dx": swipe_dx,
        "swipe_dy": swipe_dy,
        "attacks_min_per_cycle": attacks_min_per_cycle,
        "attacks_max_per_cycle": attacks_max_per_cycle,
        "extra_troops_min": extra_troops_min,
        "extra_troops_max": extra_troops_max,
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


def set_attacks_range(min_value, max_value):
    """Actualizar rango aleatorio de ataques por ciclo."""
    global attacks_min_per_cycle, attacks_max_per_cycle
    attacks_min_per_cycle = max(1, int(min_value) if isinstance(min_value, str) else int(min_value))
    attacks_max_per_cycle = max(attacks_min_per_cycle, int(max_value) if isinstance(max_value, str) else int(max_value))
    save_state()


def get_attacks_per_cycle():
    """Obtener un número aleatorio de ataques dentro del rango configurado."""
    return random.randint(attacks_min_per_cycle, attacks_max_per_cycle)


def _valid_non_negative_range(min_value, max_value):
    """Comprobar que un rango contiene enteros no negativos y min <= max."""
    try:
        min_value = int(min_value)
        max_value = int(max_value)
    except (TypeError, ValueError):
        return False
    return min_value >= 0 and max_value >= 0 and max_value >= min_value


def set_extra_troops_range(min_value, max_value):
    """Actualizar el rango aleatorio de tropas extra por ataque."""
    global extra_troops_min, extra_troops_max

    try:
        min_value = int(min_value)
        max_value = int(max_value)
    except (TypeError, ValueError):
        return False

    if not _valid_non_negative_range(min_value, max_value):
        return False

    extra_troops_min = min_value
    extra_troops_max = max_value
    save_state()
    return True


def get_extra_troops():
    """Obtener un número aleatorio de tropas extra dentro del rango configurado."""
    return random.randint(extra_troops_min, extra_troops_max)


def set_debug(enabled):
    """Actualizar modo debug."""
    global debug_mode
    debug_mode = bool(enabled)
    save_state()


# Cargar estado al importar el módulo
load_state()
