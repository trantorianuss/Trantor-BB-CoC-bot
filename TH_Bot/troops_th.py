"""TH troop deployment configuration and helpers."""

import random
from concurrent.futures import ThreadPoolExecutor

import coords
import func as f


# (slot, number of troops, deployment zone, delay, use_multitap)
DEPLOY_SEQUENCE = [
    (1, 12, "edge",   0,   False),
    (2, 16, "edge",   0,   False),
    (3,  1, "edge",   0,   False),
    (4,  1, "edge",   0, False),
    (5,  1, "edge",   0, False),
    #(3,  1, "edge",   0, False),
    (6, 4, "random", 0,   False),
    (7, 3, "random", 0,   False),
    (3,  0, "edge",   0,   False),
    (4,  0, "edge",   0, False),
    (5,  0, "edge",   0, False),
]
DEPLOY_SEQUENCE_Terminus_elefantes = [
    (1, 8, "edge",   0,   False),
    (2, 8, "edge",   0,   False),
    (4,  1, "edge",   0,   False),
    (5,  1, "edge",   0, False),
    (6,  1, "edge",   0, False),
    (7,  1, "edge",   0, False),
    (8, 6, "random", 0,   False),
    (1, 1, "random", 0,   False),
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


def slot(ctx, n):
    x, y = ctx.get_th_slot_position(n)
    f.tap_scale(x, y)


def multi_tap_scale(points, ctx):
    if not points:
        return True
    if ctx.exit_requested():
        return False

    scaled_points = [
        coords.scale(x, y)
        if coords.REAL_W is not None and coords.REAL_H is not None
        else (x, y)
        for x, y in points
    ]
    f.log(f"[TH MULTI TAP] {len(scaled_points)} taps: {scaled_points}")

    def send(point):
        x, y = point
        f.adb(f"input tap {x} {y}")

    with ThreadPoolExecutor(max_workers=len(scaled_points)) as executor:
        list(executor.map(send, scaled_points))

    return not ctx.exit_requested()


def random_drop_point(ctx):
    center_x, center_y = ctx.DROP_DIAMOND_CENTER
    half_width = ctx.DROP_DIAMOND_HALF_WIDTH
    half_height = ctx.DROP_DIAMOND_HALF_HEIGHT

    while True:
        x = random.uniform(center_x - half_width, center_x + half_width)
        y = random.uniform(center_y - half_height, center_y + half_height)
        if abs(x - center_x) / half_width + abs(y - center_y) / half_height <= 1:
            return int(x), int(y)


def deploy_troops(ctx):
    edge_index = 0

    for slot_number, count, drop_area, delay, use_multitap in ctx.DEPLOY_SEQUENCE:
        if ctx.exit_requested():
            return False

        if delay > 0 and not ctx.sleep_with_exit(delay):
            return False

        f.log(
            f"[TH] Slot {slot_number} | cantidad={count} | "
            f"zona={drop_area} | delay={delay}s | multitap={use_multitap}"
        )
        slot(ctx, slot_number)

        if count == 0:
            continue

        if drop_area == "center":
            drop_points = [ctx.DROP_POINT_CENTER]
        elif drop_area == "edge":
            drop_points = ctx.EDGE_ZONE_POINTS or ctx.DROP_POINTS_EDGE
        elif drop_area == "random":
            drop_points = None
        else:
            f.log(f"[TH] Zona de despliegue desconocida: {drop_area}", color="red")
            continue

        points_to_drop = []
        for _ in range(count):
            if ctx.exit_requested():
                return False

            if drop_area == "edge":
                drop_point = drop_points[edge_index % len(drop_points)]
                edge_index += 1
            elif drop_area == "random":
                drop_point = random_drop_point(ctx)
                f.log(f"[TH] Random drop -> {drop_point}")
            else:
                drop_point = drop_points[0]

            points_to_drop.append(drop_point)

        if use_multitap:
            for start in range(0, len(points_to_drop), ctx.MULTITAP_MAX):
                batch = points_to_drop[start:start + ctx.MULTITAP_MAX]
                if not multi_tap_scale(batch, ctx):
                    return False
        else:
            for point in points_to_drop:
                if ctx.exit_requested():
                    return False
                f.tap_scale(*point)
                if not ctx.sleep_with_exit(ctx.BETWEEN_TROOPS_DELAY):
                    return False

    f.log("[TH] Despliegue terminado")
    return True
