import pygame
import random
import math
from config import *


def check_collision(box1, box2):
    return (
        box1[2] > box2[0]
        and box1[0] < box2[2]
        and box1[3] > box2[1]
        and box1[1] < box2[3]
    )


def check_rect_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def get_attack_box(
    player_x, player_y, player_width, player_height, facing_right, attack_range
):
    if facing_right:
        attack_left = player_x + player_width
        attack_right = attack_left + attack_range
    else:
        attack_right = player_x
        attack_left = attack_right - attack_range

    attack_top = player_y
    attack_bottom = player_y + player_height

    return (attack_left, attack_top, attack_right, attack_bottom)


def get_entity_box(x, y, width, height):
    return (x, y, x + width, y + height)


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def lerp(start, end, t):
    return start + (end - start) * t


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))


def random_range(min_val, max_val):
    return random.uniform(min_val, max_val)


def draw_text(surface, text, x, y, size=FONT_MEDIUM, color=WHITE, center=False):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)

    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    else:
        surface.blit(text_surface, (x, y))

    return text_surface.get_rect()


def draw_text_outline(
    surface,
    text,
    x,
    y,
    size=FONT_MEDIUM,
    color=WHITE,
    outline_color=BLACK,
    center=False,
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


def draw_circle_outline(surface, color, center, radius, width=2):
    pygame.draw.circle(surface, color, center, radius, width)


def draw_shockwave(surface, center_x, center_y, radius, color=RED, width=3):
    pygame.draw.circle(
        surface, color, (int(center_x), int(center_y)), int(radius), width
    )


def draw_arc(surface, color, rect, start_angle, end_angle, width=3):
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, width)


def draw_health_bar(
    surface,
    x,
    y,
    width,
    height,
    current_hp,
    max_hp,
    bg_color=BLACK,
    bar_color=GREEN,
    border_color=WHITE,
):
    pygame.draw.rect(surface, bg_color, (x - 2, y - 2, width + 4, height + 4))
    pygame.draw.rect(surface, RED, (x, y, width, height))

    health_width = int((current_hp / max_hp) * width)
    pygame.draw.rect(surface, bar_color, (x, y, health_width, height))

    pygame.draw.rect(surface, border_color, (x - 2, y - 2, width + 4, height + 4), 2)


def draw_cooldown_indicator(surface, x, y, size, cooldown, max_cooldown, color=CYAN):
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


def create_particle_burst(x, y, count=10, colors=None):
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


def update_particles(particles):
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vy"] += 0.3
        particle["lifetime"] -= 1

        if particle["lifetime"] <= 0:
            particles.remove(particle)


def draw_particles(surface, particles):
    for particle in particles:
        alpha = particle["lifetime"] / particle["max_lifetime"]
        size = max(1, int(particle["size"] * alpha))

        pygame.draw.circle(
            surface, particle["color"], (int(particle["x"]), int(particle["y"])), size
        )


def shake_screen(intensity=SCREEN_SHAKE_INTENSITY):
    return (
        random.randint(-intensity, intensity),
        random.randint(-intensity, intensity),
    )


def draw_star(surface, x, y, outer_radius, inner_radius, points=5, color=YELLOW):
    star_points = []
    for i in range(points * 2):
        angle = math.pi / 2 + (i * math.pi / points)
        radius = outer_radius if i % 2 == 0 else inner_radius
        px = x + radius * math.cos(angle)
        py = y - radius * math.sin(angle)
        star_points.append((px, py))

    pygame.draw.polygon(surface, color, star_points)


def draw_heart(surface, x, y, size, filled=True):
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


def draw_sword_slash(surface, x, y, width, height, angle, color=WHITE):
    center_x = x + width // 2
    center_y = y + height // 2

    length = max(width, height)
    start_x = center_x - length * math.cos(angle) // 2
    start_y = center_y - length * math.sin(angle) // 2
    end_x = center_x + length * math.cos(angle) // 2
    end_y = center_y + length * math.sin(angle) // 2

    pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 5)
    pygame.draw.line(surface, CYAN, (start_x, start_y), (end_x, end_y), 2)


def draw_shield(surface, x, y, size, alpha=128):
    shield_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(shield_surface, (*PURPLE, alpha), (size, size), size)
    pygame.draw.circle(shield_surface, (*LIGHT_BLUE, alpha // 2), (size, size), size, 3)

    surface.blit(shield_surface, (x - size, y - size))


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
