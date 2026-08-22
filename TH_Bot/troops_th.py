"""TH troop deployment configuration."""

# (slot, number of troops, deployment zone, delay, use_multitap)
DEPLOY_SEQUENCE = [
    (1, 8, "edge",   0,   True),
    (2, 8, "edge",   0,   True),
    (7, 10, "random", 0,   True),
    (8, 10, "random", 0,   True),
    (4,  1, "edge",   0,   False),
    (5,  1, "edge",   0,   False),
    (6,  1, "edge",   0,   False),
    (7, 20, "random", 0,   True),
    (8, 20, "random", 0,   True),
    (4,  0, "edge",   0,   False),
    (5,  0, "edge",   0,   False),
    (6,  0, "edge",   0,   False),
]
