import math
import random
from typing import Dict, List, Optional, Tuple

import pygame

from config import *


_particle_pool = []
_max_pool_size = 500


def _get_particle_from_pool():
    if _particle_pool:
        return _particle_pool.pop()
    return {}


def _return_particle_to_pool(particle):
    if len(_particle_pool) < _max_pool_size:
        particle.clear()
        _particle_pool.append(particle)


def create_particle_burst(
    x: float,
    y: float,
    count: int = 10,
    colors: Optional[List[Tuple[int, int, int]]] = None,
    particle_type: str = "normal",
) -> List[Dict]:
    if colors is None:
        colors = [YELLOW, ORANGE, RED]

    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)

        if particle_type == "explosion":
            speed = random.uniform(4, 10)
            size = random.randint(3, 8)
            lifetime = random.randint(20, 40)
        elif particle_type == "sparkle":
            speed = random.uniform(1, 3)
            size = random.randint(1, 3)
            lifetime = random.randint(10, 25)
        elif particle_type == "smoke":
            speed = random.uniform(0.5, 2)
            size = random.randint(4, 10)
            lifetime = random.randint(30, 60)
        else:
            speed = random.uniform(2, 6)
            size = random.randint(2, 5)
            lifetime = random.randint(15, 30)

        velocity_x = math.cos(angle) * speed
        velocity_y = math.sin(angle) * speed
        color = random.choice(colors)

        particle = _get_particle_from_pool()
        particle.update({
            "x": x,
            "y": y,
            "vx": velocity_x,
            "vy": velocity_y,
            "color": color,
            "size": size,
            "lifetime": lifetime,
            "max_lifetime": lifetime,
            "type": particle_type,
        })
        particles.append(particle)

    return particles


def update_particles(particles: List[Dict]):
    particles_to_remove = []

    for i, particle in enumerate(particles):
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]

        particle_type = particle.get("type", "normal")

        if particle_type == "smoke":
            particle["vy"] -= 0.1
            particle["vx"] *= 0.98
        elif particle_type == "sparkle":
            particle["vy"] += 0.2
            particle["vx"] *= 0.95
        else:
            particle["vy"] += 0.3

        particle["lifetime"] -= 1

        if particle["lifetime"] <= 0:
            particles_to_remove.append(i)

    for i in reversed(particles_to_remove):
        removed = particles.pop(i)
        _return_particle_to_pool(removed)


_particle_surface_cache = {}

def draw_particles(surface: pygame.Surface, particles: List[Dict]):
    if not particles:
        return

    for particle in particles:
        alpha = particle["lifetime"] / particle["max_lifetime"]
        particle_type = particle.get("type", "normal")

        if particle_type == "smoke":
            size = int(particle["size"] * (1.5 - alpha * 0.5))
            color = particle["color"]
            color_with_fade = (
                min(255, int(color[0] * alpha)),
                min(255, int(color[1] * alpha)),
                min(255, int(color[2] * alpha)),
            )
        elif particle_type == "sparkle":
            size = max(1, int(particle["size"] * (0.5 + alpha * 0.5)))
            color_with_fade = particle["color"]
        else:
            size = max(1, int(particle["size"] * alpha))
            color_with_fade = particle["color"]

        if size > 0:
            alpha_value = int(255 * alpha)

            cache_key = (size, particle_type)
            if cache_key not in _particle_surface_cache:
                _particle_surface_cache[cache_key] = pygame.Surface(
                    (size * 2, size * 2), pygame.SRCALPHA
                )

            particle_surf = _particle_surface_cache[cache_key].copy()
            particle_surf.fill((0, 0, 0, 0))

            pygame.draw.circle(
                particle_surf,
                (*color_with_fade, alpha_value),
                (size, size),
                size,
            )
            surface.blit(
                particle_surf,
                (int(particle["x"]) - size, int(particle["y"]) - size),
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


_glow_surface_cache = {}

def draw_glow(
    surface: pygame.Surface,
    x: int,
    y: int,
    radius: int,
    color: Tuple[int, int, int],
    intensity: float = 0.5,
):
    cache_key = (radius, color, int(intensity * 100))

    if cache_key not in _glow_surface_cache:
        glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            alpha = int(intensity * 255 / (i + 1))
            current_radius = radius * i // 2
            pygame.draw.circle(
                glow_surf,
                (*color, alpha),
                (radius * 2, radius * 2),
                current_radius,
            )
        _glow_surface_cache[cache_key] = glow_surf

        if len(_glow_surface_cache) > 50:
            _glow_surface_cache.pop(next(iter(_glow_surface_cache)))

    surface.blit(_glow_surface_cache[cache_key], (x - radius * 2, y - radius * 2))


_trail_surface = None

def draw_trail(
    surface: pygame.Surface,
    positions: List[Tuple[float, float]],
    color: Tuple[int, int, int],
    width: int = 5,
):
    global _trail_surface

    if len(positions) < 2:
        return

    if _trail_surface is None:
        _trail_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    _trail_surface.fill((0, 0, 0, 0))

    for i in range(len(positions) - 1):
        alpha = int(255 * (i + 1) / len(positions))
        current_width = max(1, int(width * (i + 1) / len(positions)))

        pygame.draw.line(
            _trail_surface,
            (*color, alpha),
            (int(positions[i][0]), int(positions[i][1])),
            (int(positions[i + 1][0]), int(positions[i + 1][1])),
            current_width,
        )

    surface.blit(_trail_surface, (0, 0))


def create_screen_fade(
    surface: pygame.Surface, alpha: int, color: Tuple[int, int, int] = BLACK
):
    fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fade_surf.fill((*color, alpha))
    surface.blit(fade_surf, (0, 0))


def draw_lightning(
    surface: pygame.Surface,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    segments: int = 8,
    color: Tuple[int, int, int] = CYAN,
):
    points = [(start_x, start_y)]

    for i in range(1, segments):
        t = i / segments
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t

        offset_x = random.uniform(-20, 20)
        offset_y = random.uniform(-20, 20)

        points.append((x + offset_x, y + offset_y))

    points.append((end_x, end_y))

    for i in range(len(points) - 1):
        pygame.draw.line(surface, color, points[i], points[i + 1], 3)
        pygame.draw.line(surface, WHITE, points[i], points[i + 1], 1)
