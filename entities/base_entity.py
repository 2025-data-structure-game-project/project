from typing import Optional, Tuple

import pygame

from config import *


class BaseEntity:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.on_ground = False
        self.gravity = PLAYER_GRAVITY

        self.facing_right = True
        self.alive = True

        self.hit_flash = 0

    def apply_gravity(self):
        self.velocity_y += self.gravity

    def apply_velocity(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    def get_bottom(self) -> float:
        return self.y + self.height

    def get_top(self) -> float:
        return self.y

    def get_left(self) -> float:
        return self.x

    def get_right(self) -> float:
        return self.x + self.width

    def set_position(self, x: float, y: float):
        self.x = x
        self.y = y

    def move(self, dx: float, dy: float):
        self.x += dx
        self.y += dy

    def check_screen_bounds(
        self, screen_width: int = SCREEN_WIDTH, screen_height: int = SCREEN_HEIGHT
    ):
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width
            self.velocity_x = 0

        if self.y > screen_height:
            self.alive = False

    def update(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement update()")

    def draw(self, surface: pygame.Surface, shake_offset: Tuple[int, int] = (0, 0)):
        raise NotImplementedError("Subclass must implement draw()")

    def take_damage(self, amount: int = 1) -> bool:
        return False

    def is_dead(self) -> bool:
        return not self.alive


class PhysicsEntity(BaseEntity):
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__(x, y, width, height)
        self.max_fall_speed = 20

    def apply_physics(self):
        self.apply_gravity()

        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed

        self.apply_velocity()

    def check_platform_collision_vertical(self, platforms):
        self.on_ground = False

        for platform in platforms:
            if not hasattr(platform, "visible") or platform.visible:
                if (
                    self.x < platform.x + platform.width
                    and self.x + self.width > platform.x
                    and self.y < platform.y + platform.height
                    and self.y + self.height > platform.y
                ):
                    if self.velocity_y > 0:
                        self.y = platform.y - self.height
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0:
                        self.y = platform.y + platform.height
                        self.velocity_y = 0

    def check_platform_collision_horizontal(self, platforms):
        for platform in platforms:
            if not hasattr(platform, "visible") or platform.visible:
                if (
                    self.x < platform.x + platform.width
                    and self.x + self.width > platform.x
                    and self.y < platform.y + platform.height
                    and self.y + self.height > platform.y
                ):
                    if self.velocity_x > 0:
                        self.x = platform.x - self.width
                        self.velocity_x = 0
                    elif self.velocity_x < 0:
                        self.x = platform.x + platform.width
                        self.velocity_x = 0


class DamageableEntity(PhysicsEntity):
    def __init__(
        self, x: float, y: float, width: int, height: int, max_health: int = 1
    ):
        super().__init__(x, y, width, height)
        self.max_health = max_health
        self.health = max_health
        self.invincible_time = 0

    def take_damage(self, amount: int = 1) -> bool:
        if self.invincible_time > 0:
            return False

        self.health -= amount
        self.hit_flash = HIT_FLASH_DURATION

        if self.health <= 0:
            self.health = 0
            self.alive = False

        return True

    def heal(self, amount: int = 1):
        self.health = min(self.health + amount, self.max_health)

    def is_invincible(self) -> bool:
        return self.invincible_time > 0

    def update_timers(self):
        if self.invincible_time > 0:
            self.invincible_time -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def get_health_percent(self) -> float:
        return (self.health / self.max_health) * 100 if self.max_health > 0 else 0

    def is_low_health(self, threshold: float = 25.0) -> bool:
        return self.get_health_percent() <= threshold


class AnimatedEntity(DamageableEntity):
    def __init__(
        self, x: float, y: float, width: int, height: int, max_health: int = 1
    ):
        super().__init__(x, y, width, height, max_health)
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5

    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame += 1

    def set_animation(self, animation_name: str, reset: bool = True):
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            if reset:
                self.animation_frame = 0
                self.animation_timer = 0

    def get_sprite_key(self) -> str:
        return f"{self.__class__.__name__.lower()}_{self.current_animation}"
