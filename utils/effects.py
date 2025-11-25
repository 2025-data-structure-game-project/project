import math
import random
from typing import Dict, List, Optional, Tuple

import pygame

from config import *


def create_particle_burst(
    x: float,
    y: float,
    count: int = 10,
    colors: Optional[List[Tuple[int, int, int]]] = None,
) -> List[Dict]:
    if colors is None:
        colors = [YELLOW, ORANGE, RED]

    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        velocity_x = math.cos(angle) * speed
        velocity_y = math.sin(angle) * speed
        color = random.choice(colors)
        size = random.randint(2, 5)
        lifetime = random.randint(15, 30)

        particles.append(
            {
                "x": x,
                "y": y,
                "vx": velocity_x,
                "vy": velocity_y,
                "color": color,
                "size": size,
                "lifetime": lifetime,
                "max_lifetime": lifetime,
            }
        )

    return particles


def update_particles(particles: List[Dict]):
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vy"] += 0.3
        particle["lifetime"] -= 1

        if particle["lifetime"] <= 0:
            particles.remove(particle)


def draw_particles(surface: pygame.Surface, particles: List[Dict]):
    for particle in particles:
        alpha = particle["lifetime"] / particle["max_lifetime"]
        size = max(1, int(particle["size"] * alpha))
        pygame.draw.circle(
            surface, particle["color"], (int(particle["x"]), int(particle["y"])), size
        )


def shake_screen(intensity: int = SCREEN_SHAKE_INTENSITY) -> Tuple[int, int]:
    return (
        random.randint(-intensity, intensity),
        random.randint(-intensity, intensity),
    )


def draw_text(
    surface: pygame.Surface,
    text: str,
    x: float,
    y: float,
    size: int = FONT_MEDIUM,
    color: Tuple[int, int, int] = WHITE,
    center: bool = False,
) -> pygame.Rect:
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)

    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    else:
        surface.blit(text_surface, (x, y))

    return text_surface.get_rect()


def draw_text_outline(
    surface: pygame.Surface,
    text: str,
    x: float,
    y: float,
    size: int = FONT_MEDIUM,
    color: Tuple[int, int, int] = WHITE,
    outline_color: Tuple[int, int, int] = BLACK,
    center: bool = False,
):
    font = pygame.font.Font(None, size)

    for dx in [-2, 0, 2]:
        for dy in [-2, 0, 2]:
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                if center:
                    outline_rect = outline_surface.get_rect(center=(x + dx, y + dy))
                    surface.blit(outline_surface, outline_rect)
                else:
                    surface.blit(outline_surface, (x + dx, y + dy))

    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    else:
        surface.blit(text_surface, (x, y))


def draw_circle_outline(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    center: Tuple[int, int],
    radius: int,
    width: int = 2,
):
    pygame.draw.circle(surface, color, center, radius, width)


def draw_shockwave(
    surface: pygame.Surface,
    center_x: float,
    center_y: float,
    radius: float,
    color: Tuple[int, int, int] = RED,
    width: int = 3,
):
    pygame.draw.circle(
        surface, color, (int(center_x), int(center_y)), int(radius), width
    )


def draw_arc(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    rect: pygame.Rect,
    start_angle: float,
    end_angle: float,
    width: int = 3,
):
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, width)


def draw_health_bar(
    surface: pygame.Surface,
    x: float,
    y: float,
    width: int,
    height: int,
    current_hp: float,
    max_hp: float,
    bg_color: Tuple[int, int, int] = BLACK,
    bar_color: Tuple[int, int, int] = GREEN,
    border_color: Tuple[int, int, int] = WHITE,
):
    pygame.draw.rect(surface, bg_color, (x - 2, y - 2, width + 4, height + 4))
    pygame.draw.rect(surface, RED, (x, y, width, height))

    health_width = int((current_hp / max_hp) * width)
    pygame.draw.rect(surface, bar_color, (x, y, health_width, height))

    pygame.draw.rect(surface, border_color, (x - 2, y - 2, width + 4, height + 4), 2)


def draw_cooldown_indicator(
    surface: pygame.Surface,
    x: int,
    y: int,
    size: int,
    cooldown: float,
    max_cooldown: float,
    color: Tuple[int, int, int] = CYAN,
):
    if cooldown > 0:
        pygame.draw.circle(surface, DARK_GRAY, (x, y), size)

        progress = cooldown / max_cooldown
        end_angle = -math.pi / 2 + (2 * math.pi * (1 - progress))

        if progress < 1:
            points = [(x, y)]
            for i in range(int(360 * (1 - progress)) + 1):
                angle = math.radians(i - 90)
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
                points.append((px, py))

            if len(points) > 2:
                pygame.draw.polygon(surface, color, points)

        pygame.draw.circle(surface, WHITE, (x, y), size, 2)
    else:
        pygame.draw.circle(surface, color, (x, y), size)
        pygame.draw.circle(surface, WHITE, (x, y), size, 2)


def draw_star(
    surface: pygame.Surface,
    x: float,
    y: float,
    outer_radius: float,
    inner_radius: float,
    points: int = 5,
    color: Tuple[int, int, int] = YELLOW,
):
    star_points = []
    for i in range(points * 2):
        angle = math.pi / 2 + (i * math.pi / points)
        radius = outer_radius if i % 2 == 0 else inner_radius
        px = x + radius * math.cos(angle)
        py = y - radius * math.sin(angle)
        star_points.append((px, py))

    pygame.draw.polygon(surface, color, star_points)


def draw_heart(
    surface: pygame.Surface, x: float, y: float, size: int, filled: bool = True
):
    if filled:
        color = RED
    else:
        color = DARK_GRAY

    pygame.draw.circle(surface, color, (int(x - size // 4), int(y)), size // 2)
    pygame.draw.circle(surface, color, (int(x + size // 4), int(y)), size // 2)
    points = [(x - size // 2, y), (x + size // 2, y), (x, y + size)]
    pygame.draw.polygon(surface, color, points)

    if not filled:
        pygame.draw.circle(surface, RED, (int(x - size // 4), int(y)), size // 2, 2)
        pygame.draw.circle(surface, RED, (int(x + size // 4), int(y)), size // 2, 2)
        pygame.draw.polygon(surface, RED, points, 2)


def draw_sword_slash(
    surface: pygame.Surface,
    x: float,
    y: float,
    width: float,
    height: float,
    angle: float,
    color: Tuple[int, int, int] = WHITE,
):
    center_x = x + width // 2
    center_y = y + height // 2

    length = max(width, height)
    start_x = center_x - length * math.cos(angle) // 2
    start_y = center_y - length * math.sin(angle) // 2
    end_x = center_x + length * math.cos(angle) // 2
    end_y = center_y + length * math.sin(angle) // 2

    pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 5)
    pygame.draw.line(surface, CYAN, (start_x, start_y), (end_x, end_y), 2)


def draw_shield(
    surface: pygame.Surface, x: float, y: float, size: int, alpha: int = 128
):
    shield_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(shield_surface, (*PURPLE, alpha), (size, size), size)
    pygame.draw.circle(shield_surface, (*LIGHT_BLUE, alpha // 2), (size, size), size, 3)
    surface.blit(shield_surface, (x - size, y - size))


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def random_range(min_val: float, max_val: float) -> float:
    return random.uniform(min_val, max_val)
