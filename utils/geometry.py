import math
from typing import Tuple


def check_collision(
    box1: Tuple[float, float, float, float], box2: Tuple[float, float, float, float]
) -> bool:
    return (
        box1[2] > box2[0]
        and box1[0] < box2[2]
        and box1[3] > box2[1]
        and box1[1] < box2[3]
    )


def check_rect_collision(
    x1: float,
    y1: float,
    w1: float,
    h1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float,
) -> bool:
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def get_attack_box(
    player_x: float,
    player_y: float,
    player_width: float,
    player_height: float,
    facing_right: bool,
    attack_range: float,
) -> Tuple[float, float, float, float]:
    if facing_right:
        attack_left = player_x + player_width
        attack_right = attack_left + attack_range
    else:
        attack_right = player_x
        attack_left = attack_right - attack_range

    attack_top = player_y
    attack_bottom = player_y + player_height

    return (attack_left, attack_top, attack_right, attack_bottom)


def get_entity_box(
    x: float, y: float, width: float, height: float
) -> Tuple[float, float, float, float]:
    return (x, y, x + width, y + height)


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def angle_between(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.atan2(y2 - y1, x2 - x1)


def point_in_rect(
    point_x: float,
    point_y: float,
    rect_x: float,
    rect_y: float,
    rect_w: float,
    rect_h: float,
) -> bool:
    return rect_x <= point_x <= rect_x + rect_w and rect_y <= point_y <= rect_y + rect_h
