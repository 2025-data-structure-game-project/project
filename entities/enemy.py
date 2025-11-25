import random

import pygame

from config import *
from entities.base_entity import DamageableEntity
from systems.asset_manager import get_asset_manager


class Enemy(DamageableEntity):
    def __init__(self, x, y, enemy_type, color="blue"):
        super().__init__(x, y, ENEMY_WIDTH, ENEMY_HEIGHT, max_health=1)

        self.assets = get_asset_manager()
        self.type = enemy_type
        self.color = color

        if enemy_type == "skeleton":
            self.velocity_x = SKELETON_SPEED
            self.direction = 1
        else:
            self.direction = 1

        self.attack_timer = 0
        self.jump_timer = 0

        self.current_animation = "idle"

    def update(self, platforms, player):
        if not self.alive:
            return

        self.update_timers()

        self.apply_gravity()
        self.y += self.velocity_y

        self.x += self.velocity_x

        self.check_platform_collision_vertical(platforms)

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
                        self.direction *= -1
                        self.velocity_x *= -1
                    elif self.velocity_x < 0:
                        self.x = platform.x + platform.width
                        self.direction *= -1
                        self.velocity_x *= -1

        if self.type == "skeleton":
            self.facing_right = self.direction > 0

            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
                self.direction *= -1
                self.velocity_x *= -1
                self.facing_right = self.direction > 0

            if abs(self.velocity_x) > 0:
                self.current_animation = "walk"
            else:
                self.current_animation = "idle"

        elif self.type == "slime":
            self.jump_timer += 1
            if self.on_ground and self.jump_timer > random.randint(60, 120):
                self.velocity_y = -SLIME_JUMP_POWER
                self.velocity_x = random.choice([-2, 2])
                self.jump_timer = 0
                self.current_animation = "jump"
            elif self.on_ground:
                self.current_animation = "idle"

    def draw(self, screen, shake_offset=(0, 0)):
        if not self.alive:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.type == "slime":
            sprite_key = f"slime_{self.color}_{self.current_animation}"
        else:
            sprite_key = f"{self.type}_{self.current_animation}"

        sprite = self.assets.get_sprite(sprite_key)

        if sprite:
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)

            screen.blit(sprite, (draw_x, draw_y))
        else:
            if self.type == "skeleton":
                color = GRAY
            elif self.type == "slime":
                color = GREEN
            else:
                color = ORANGE

            pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
            pygame.draw.rect(
                screen, BLACK, (draw_x, draw_y, self.width, self.height), 2
            )
