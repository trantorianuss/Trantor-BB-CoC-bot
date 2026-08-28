"""TH troop-bar layouts and deployment strategies."""

# The order in BAR defines the real game slot: first item = slot 1, etc.
# SEQUENCE contains actions, not slot numbers, so the same element can be
# deployed multiple times and the sequence can move back and forth through
# the troop bar.

STRATEGIES = {
    "default": {
        "bar": ["troop_1", "troop_2", "troop_3", "hero_1", "hero_2", "spell_1", "spell_2"],
        "sequence": [
            ("troop_1", 5, "edge", 0, False), ("troop_2", 6, "edge", 0, False),
            ("troop_3", 1, "edge", 0, False), ("hero_1", 1, "edge", 0, False),
            ("hero_2", 1, "edge", 0, False), ("spell_1", 2, "random", 0, False),
            ("spell_2", 2, "random", 0, False), ("hero_1", 0, "edge", 0, False),
            ("hero_2", 0, "edge", 0, False), ("troop_1", 6, "edge", 0, False),
            ("troop_2", 10, "edge", 0, False), ("spell_1", 2, "random", 0, False),
            ("spell_2", 1, "random", 0, False),
        ],
    },
    "tresheroes": {
        "bar": ["troop_1", "troop_2", "troop_3", "hero_1", "hero_2", "hero_3", "spell_1", "spell_2"],
        "sequence": [
            ("troop_1", 12, "edge", 0, False), ("troop_2", 16, "edge", 0, False),
            ("troop_3", 1, "edge", 0, False), ("hero_1", 1, "edge", 0, False),
            ("hero_2", 1, "edge", 0, False), ("spell_1", 4, "random", 0, False),
            ("spell_2", 3, "random", 0, False), ("troop_3", 0, "edge", 0, False),
            ("hero_1", 0, "edge", 0, False), ("hero_2", 0, "edge", 0, False),
        ],
    },
    "Terminus_elefantes": {
        "bar": ["troop_1", "troop_2", "troop_3", "hero_1", "hero_2", "hero_3", "spell_1", "spell_2"],
        "sequence": [
            ("troop_1", 12, "edge", 0, False), ("troop_2", 8, "edge", 0, False),
            ("hero_1", 1, "edge", 0, False), ("hero_2", 1, "edge", 0, False),
            ("hero_3", 1, "edge", 0, False), ("spell_1", 1, "edge", 0, False),
            ("spell_2", 1, "edge", 0, False), ("spell_2", 6, "random", 0, False),
            ("troop_1", 1, "random", 0, False), ("hero_1", 0, "edge", 0, False),
            ("hero_2", 0, "edge", 0, False), ("hero_3", 0, "edge", 0, False),
        ],
    },
    "kk": {
        "bar": ["troop_1", "troop_2", "troop_3", "hero_1", "hero_2", "hero_3", "spell_1", "spell_2"],
        "sequence": [
            ("troop_1", 8, "edge", 0, True), ("troop_2", 8, "edge", 0, True),
            ("spell_1", 10, "random", 0, True), ("spell_2", 10, "random", 0, True),
            ("hero_1", 1, "edge", 0, False), ("hero_2", 1, "edge", 0, False),
            ("hero_3", 1, "edge", 0, False), ("spell_1", 20, "random", 0, True),
            ("spell_2", 20, "random", 0, True), ("hero_1", 0, "edge", 0, False),
            ("hero_2", 0, "edge", 0, False), ("hero_3", 0, "edge", 0, False),
        ],
    },
    "terminis_BCK": {
        "bar": ["troop_1", "troop_2", "troop_3", "hero_1", "hero_2", "hero_3", "spell_1", "spell_2", "troop_4", "troop_5"],
        "sequence": [
            ("troop_1", 6, "edge", 0, True), ("troop_2", 12, "edge", 0, True),
            ("troop_3", 3, "edge", 0, False), ("hero_1", 1, "edge", 0, False),
            ("hero_2", 1, "edge", 0.1, False), ("hero_3", 1, "edge", 0.1, False),
            ("spell_1", 1, "edge", 0.1, False), ("spell_2", 1, "edge", 0.1, False),
            ("hero_2", 0, "edge", 0.1, False), ("hero_3", 0, "edge", 0.1, False),
            ("spell_1", 0, "edge", 0.1, False), ("spell_2", 0, "edge", 0.1, False),
            ("troop_4", 10, "random", 0, True), ("troop_5", 1, "random", 0, True),
        ],
    },
}

DEFAULT_STRATEGY = "default"


def get_strategy(name=DEFAULT_STRATEGY):
    """Return a TH strategy by name."""
    try:
        return STRATEGIES[name]
    except KeyError as exc:
        raise ValueError(f"Estrategia TH desconocida: {name}") from exc


def slot_for(bar, element):
    """Return the 1-based game slot for an element in a bar."""
    try:
        return bar.index(element) + 1
    except ValueError as exc:
        raise ValueError(f"Elemento '{element}' no está en la barra TH") from exc
