"""Load TH troop-bar layouts and deployment strategies from JSON."""

import json
from pathlib import Path
from types import SimpleNamespace


STRATEGIES_FILE = Path(__file__).with_name("th_strategies.json")
DEFAULT_STRATEGY = "default"


def _load_strategies():
    with STRATEGIES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_strategy(name=DEFAULT_STRATEGY):
    """Return a TH strategy by name."""
    strategies = _load_strategies()
    try:
        return strategies[name]
    except KeyError as exc:
        raise ValueError(f"Estrategia TH desconocida: {name}") from exc


def slot_for(bar, element):
    """Return the 1-based game slot for an element in a bar."""
    try:
        return bar.index(element) + 1
    except ValueError as exc:
        raise ValueError(f"Elemento '{element}' no está en la barra TH") from exc


def build_context(strategy_name=DEFAULT_STRATEGY, edge_zone_points=None, get_th_slot_position=None):
    """Build the small execution context for a TH attack."""
    strategy = get_strategy(strategy_name)
    return SimpleNamespace(
        TROOP_BAR=strategy["bar"],
        DEPLOY_SEQUENCE=strategy["sequence"],
        EDGE_ZONE_POINTS=edge_zone_points,
        get_th_slot_position=get_th_slot_position,
    )
