"""TH troop deployment helpers."""

import random
from concurrent.futures import ThreadPoolExecutor

import botstate
import coords
import func as f

from TH_Bot.th_strategies import slot_for


def slot(ctx, slot_number):
    x, y = ctx.get_th_slot_position(slot_number)
    f.tap_scale(x, y)


def multi_tap_scale(points, ctx):
    if not points:
        return True
    if not botstate.should_run():
        return False
    scaled_points = [
        coords.scale(x, y)
        if coords.REAL_W is not None and coords.REAL_H is not None else (x, y)
        for x, y in points
    ]
    f.log(f"[TH MULTI TAP] {len(scaled_points)} taps: {scaled_points}")
    def send(point):
        f.adb(f"input tap {point[0]} {point[1]}")
    with ThreadPoolExecutor(max_workers=len(scaled_points)) as executor:
        list(executor.map(send, scaled_points))
    return botstate.should_run()


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
    for element, count, drop_area, delay, use_multitap in ctx.DEPLOY_SEQUENCE:
        if not botstate.should_run():
            return False
        if delay > 0 and not ctx.sleep_with_exit(delay):
            return False
        try:
            slot_number = slot_for(ctx.TROOP_BAR, element)
        except ValueError as exc:
            f.log(f"[TH] {exc}. Acción omitida.", color="yellow")
            continue
        f.log(f"[TH] {element} | Slot {slot_number} | cantidad={count} | zona={drop_area} | delay={delay}s | multitap={use_multitap}")
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
            if not botstate.should_run():
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
                if not multi_tap_scale(points_to_drop[start:start + ctx.MULTITAP_MAX], ctx):
                    return False
        else:
            for point in points_to_drop:
                if not botstate.should_run():
                    return False
                f.tap_scale(*point)
                if not ctx.sleep_with_exit(ctx.BETWEEN_TROOPS_DELAY):
                    return False
    f.log("[TH] Despliegue terminado")
    return True
