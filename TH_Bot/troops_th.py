"""TH troop deployment configuration."""

# (slot, number of troops, deployment zone, delay, use_multitap)
DEPLOY_SEQUENCE = [
    (1, 8, "edge",   0,   True),
    (2, 8, "edge",   0,   True),
    (4,  1, "edge",   0,   False),
    (5,  1, "edge",   0, False),
    (6,  1, "edge",   0, False),
    (7,  1, "edge",   0, False),
    (8, 6, "random", 0,   True),
    (1, 1, "random", 0,   True),
    (4,  0, "edge",   0,   False),
    (5,  0, "edge",   0, False),
    (6,  0, "edge",   0, False),
]
DEPLOY_SEQUENCE_kk = [
    (1, 8, "edge",   0,   True),
    (2, 8, "edge",   0,   True),
    (7, 10, "random", 0,   True),
    (8, 10, "random", 0,   True),
    (4,  1, "edge",   0,   False),
    (5,  1, "edge",   0, False),
    (6,  1, "edge",   0, False),
    (7, 20, "random", 0,   True),
    (8, 20, "random", 0,   True),
    (4,  0, "edge",   0,   False),
    (5,  0, "edge",   0, False),
    (6,  0, "edge",   0, False),
]

DEPLOY_SEQUENCE_terminis_BCK = [
    (1,  6, "edge",   0,   True),
    (2, 12, "edge",   0,   True),
    (3,  3, "edge",   0,   False),
    (4,  1, "edge",   0,   False),
    (5,  1, "edge",   0.1, False),
    (6,  1, "edge",   0.1, False),
    (7,  1, "edge",   0.1, False),
    (8,  1, "edge",   0.1, False),
    (5,  0, "edge",   0.1, False),
    (6,  0, "edge",   0.1, False),
    (7,  0, "edge",   0.1, False),
    (8,  0, "edge",   0.1, False),
    (9, 10, "random", 0,   True),
    (10, 1, "random", 0,   True),
]
