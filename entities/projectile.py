import math

import pygame

from config import *
from entities.base_entity import BaseEntity, PhysicsEntity
from systems.asset_manager import get_asset_manager


class Projectile(PhysicsEntity):
    def __init__(self, x, y, direction, proj_type="magic", from_player=False, angle=0):
        super().__init__(x, y, PROJECTILE_WIDTH, PROJECTILE_HEIGHT)

        self.assets = get_asset_manager()
        self.type = proj_type
        self.from_player = from_player
        self.active = True

        if from_player:
            base_speed = PROJECTILE_PLAYER_SPEED
        else:
            base_speed = PROJECTILE_SPEED

        if angle != 0:
            self.velocity_x = base_speed * direction * math.cos(angle)
            self.velocity_y = base_speed * math.sin(angle)
        else:
            self.velocity_x = base_speed * direction
            self.velocity_y = 0

        self.gravity_affected = False
        self.lifetime = 180

    def update(self):
        if not self.active:
            return

        self.x += self.velocity_x
        self.y += self.velocity_y

        if self.gravity_affected:
            self.velocity_y += 0.3

        self.lifetime -= 1

        if (
            self.x < -50
            or self.x > SCREEN_WIDTH + 50
            or self.y < -50
            or self.y > SCREEN_HEIGHT + 50
            or self.lifetime <= 0
        ):
            self.active = False

    def check_platform_collision(self, platforms):
        for platform in platforms:
            if not platform.visible:
                continue

            if (
                self.x < platform.x + platform.width
                and self.x + self.width > platform.x
                and self.y < platform.y + platform.height
                and self.y + self.height > platform.y
            ):
                if self.velocity_y > 0:
                    return platform, self.x, platform.y

        return None, None, None

    def draw(self, screen, shake_offset=(0, 0)):
        if not self.active:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.type in ["magic", "player_energy", "fireball"]:
            sprite_key = f"projectile_{self.type.replace('player_', '')}"
            sprite = self.assets.get_sprite(sprite_key)

            if sprite:
                screen.blit(sprite, (draw_x, draw_y))
            else:
                center_x = int(draw_x + self.width // 2)
                center_y = int(draw_y + self.height // 2)

                if self.type == "magic":
                    pygame.draw.circle(screen, PURPLE, (center_x, center_y), 6)
                    pygame.draw.circle(screen, PINK, (center_x, center_y), 3)

                elif self.type == "fireball":
                    pygame.draw.circle(screen, RED, (center_x, center_y), 8)
                    pygame.draw.circle(screen, ORANGE, (center_x, center_y), 5)
                    pygame.draw.circle(screen, YELLOW, (center_x, center_y), 2)

                elif self.type == "player_energy":
                    pygame.draw.circle(screen, CYAN, (center_x, center_y), 7)
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), 4)

        elif self.type == "sword_beam":
            length = 30
            center_y = draw_y + self.height // 2

            if self.velocity_x > 0:
                start_x = draw_x
                end_x = draw_x + length
            else:
                start_x = draw_x + length
                end_x = draw_x

            pygame.draw.line(screen, WHITE, (start_x, center_y), (end_x, center_y), 6)
            pygame.draw.line(screen, CYAN, (start_x, center_y), (end_x, center_y), 3)
            pygame.draw.circle(screen, WHITE, (int(end_x), int(center_y)), 5)


class Fire(BaseEntity):
    def __init__(self, x, y, width):
        super().__init__(x, y, min(width, 100), 30)
        self.duration = FIRE_DURATION
        self.damage_timer = 0
        self.active = True
        self.flicker_timer = 0

    def update(self):
        self.duration -= 1
        self.damage_timer += 1
        self.flicker_timer += 1

        if self.duration <= 0:
            self.active = False

    def can_damage(self):
        if self.damage_timer >= FIRE_DAMAGE_INTERVAL:
            self.damage_timer = 0
            return True
        return False

    def draw(self, screen, shake_offset=(0, 0)):
        if not self.active:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        import random

        flicker = random.randint(-3, 3)

        for i in range(3):
            height = self.height - i * 8 + flicker
            alpha = 200 - i * 50

            fire_surface = pygame.Surface((self.width, height), pygame.SRCALPHA)

            if i == 0:
                color = (*RED, alpha)
            elif i == 1:
                color = (*ORANGE, alpha)
            else:
                color = (*YELLOW, alpha)

            fire_surface.fill(color)
            screen.blit(fire_surface, (draw_x, draw_y - height))

        if self.flicker_timer % 5 == 0:
            smoke_y = draw_y - self.height - random.randint(0, 20)
            smoke_x = draw_x + random.randint(0, int(self.width))
            pygame.draw.circle(screen, (*GRAY, 100), (int(smoke_x), int(smoke_y)), 3)
