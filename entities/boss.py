import math
import random

import pygame
from patterns.charge_pattern import ChargePattern
from patterns.flame_pattern import FlamePattern
from patterns.jump_pattern import JumpPattern
from patterns.slash_pattern import SlashPattern
from patterns.teleport_pattern import TeleportPattern

from config import *
from entities.base_entity import DamageableEntity
from systems.asset_manager import get_asset_manager


class Boss(DamageableEntity):
    def __init__(self, x, y):
        super().__init__(x, y, BOSS_WIDTH, BOSS_HEIGHT, max_health=BOSS_MAX_HEALTH)

        self.assets = get_asset_manager()

        self.pattern = None
        self.current_pattern_obj = None
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.attack_cooldown = 0

        self.stunned = False
        self.stun_timer = 0
        self.berserk_mode = False
        self.platform_collapsed = False

        self.charge_particles = []
        self.warning_timer = 0

        self.last_pattern = None
        self.pattern_count = 0

        self.patterns = {
            "jump": JumpPattern(self),
            "flame": FlamePattern(self),
            "charge": ChargePattern(self),
            "slash": SlashPattern(self),
            "teleport": TeleportPattern(self),
        }

    def update(self, player, platforms, projectiles):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.vulnerable = False
        if self.warning_timer > 0:
            self.warning_timer -= 1

        self.update_timers()

        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
            return None, []

        self.apply_gravity()
        self.y += self.velocity_y
        self.x += self.velocity_x

        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
            self.enter_stun("wall")
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.velocity_x = 0
            self.enter_stun("wall")

        self.check_platform_collision_vertical(platforms)

        if self.pattern == "charge" and abs(self.velocity_x) > 10:
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
                        self.velocity_x = 0
                        self.enter_stun("charge")

        if self.health <= BOSS_VULNERABLE_THRESHOLD and not self.berserk_mode:
            self.enter_berserk_mode()

        actions = []
        if self.pattern is None and self.attack_cooldown <= 0:
            self.choose_pattern(player)

        if self.current_pattern_obj:
            action = self.current_pattern_obj.update(player, projectiles)
            if action:
                actions.append(action)

            if self.current_pattern_obj.is_complete():
                self.end_pattern()

        if self.pattern not in ["charge"] and not self.stunned:
            self.facing_right = player.x > self.x

        return self.pattern, actions

    def choose_pattern(self, player):
        distance = abs(player.x - self.x)

        patterns = []
        weights = []

        if self.berserk_mode:
            patterns = ["jump", "flame", "charge", "slash", "teleport"]
            weights = [20, 20, 20, 20, 20]
        else:
            hp_percent = (self.health / self.max_health) * 100

            if distance < 100:
                patterns = ["slash", "jump"]
                weights = [60, 40]
            elif distance < 300:
                patterns = ["charge", "slash", "flame"]
                weights = [40, 30, 30]
            else:
                patterns = ["flame", "jump", "charge"]
                weights = [50, 30, 20]

            if hp_percent < 50:
                if "charge" in patterns:
                    idx = patterns.index("charge")
                    weights[idx] += 20

        if self.last_pattern in patterns:
            idx = patterns.index(self.last_pattern)
            weights[idx] = max(5, weights[idx] - 30)

        self.pattern = random.choices(patterns, weights=weights)[0]
        self.last_pattern = self.pattern
        self.current_pattern_obj = self.patterns[self.pattern]
        self.current_pattern_obj.start()
        self.facing_right = player.x > self.x
        self.warning_timer = 45

    def enter_stun(self, reason):
        self.stunned = True
        self.stun_timer = BOSS_CHARGE_STUN_DURATION
        self.vulnerable = True
        self.vulnerable_timer = BOSS_CHARGE_STUN_DURATION
        self.velocity_x = 0

    def enter_berserk_mode(self):
        self.berserk_mode = True
        self.vulnerable = True
        self.attack_cooldown = 0

    def end_pattern(self):
        self.pattern = None
        self.current_pattern_obj = None

        if self.berserk_mode:
            self.attack_cooldown = BOSS_PATTERN_COOLDOWN_BERSERK
        else:
            self.attack_cooldown = BOSS_PATTERN_COOLDOWN_NORMAL

    def take_damage(self, amount):
        if self.health > BOSS_VULNERABLE_THRESHOLD and not self.vulnerable:
            return False

        self.health = max(0, self.health - amount)
        self.hit_flash = HIT_FLASH_DURATION

        knockback = 10 if self.facing_right else -10
        self.velocity_x = -knockback

        if self.health <= 0:
            self.alive = False

        return True

    def can_be_damaged(self):
        return self.health <= BOSS_VULNERABLE_THRESHOLD or self.vulnerable

    def draw(self, screen, shake_offset=(0, 0)):
        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        sprite_key = "boss_idle"
        if self.berserk_mode:
            sprite_key = "boss_berserk"
        elif self.hit_flash > 0:
            sprite_key = "boss_hurt"
        elif self.pattern:
            sprite_key = "boss_attack"

        sprite = self.assets.get_sprite(sprite_key)

        if sprite:
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            screen.blit(sprite, (draw_x, draw_y))
        else:
            if self.hit_flash > 0:
                color = WHITE
            elif self.stunned:
                color = GRAY
            elif self.berserk_mode:
                color = DARK_RED
            else:
                color = RED

            pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
            pygame.draw.rect(
                screen, BLACK, (draw_x, draw_y, self.width, self.height), 3
            )

        if not self.can_be_damaged() and self.health > BOSS_VULNERABLE_THRESHOLD:
            shield_surface = pygame.Surface(
                (self.width + 20, self.height + 20), pygame.SRCALPHA
            )
            pygame.draw.circle(
                shield_surface,
                (*PURPLE, 64),
                (self.width // 2 + 10, self.height // 2 + 10),
                max(self.width, self.height) // 2 + 10,
            )
            pygame.draw.circle(
                shield_surface,
                (*LIGHT_BLUE, 128),
                (self.width // 2 + 10, self.height // 2 + 10),
                max(self.width, self.height) // 2 + 10,
                3,
            )
            screen.blit(shield_surface, (draw_x - 10, draw_y - 10))

        if self.vulnerable and self.health > BOSS_VULNERABLE_THRESHOLD:
            for i in range(3):
                angle = (pygame.time.get_ticks() / 500 + i * 2 * math.pi / 3) % (
                    2 * math.pi
                )
                star_x = draw_x + self.width // 2 + 40 * math.cos(angle)
                star_y = draw_y + self.height // 2 + 40 * math.sin(angle)
                self.draw_star(screen, star_x, star_y, 8, 4)

        if self.berserk_mode:
            aura_surface = pygame.Surface(
                (self.width + 40, self.height + 40), pygame.SRCALPHA
            )
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            alpha = int(50 + pulse * 50)
            pygame.draw.circle(
                aura_surface,
                (*RED, alpha),
                (self.width // 2 + 20, self.height // 2 + 20),
                max(self.width, self.height) // 2 + 20,
            )
            screen.blit(aura_surface, (draw_x - 20, draw_y - 20))

        self.draw_pattern_effects(screen, draw_x, draw_y)

        if self.stunned:
            for i in range(3):
                angle = (pygame.time.get_ticks() / 300 + i * 2 * math.pi / 3) % (
                    2 * math.pi
                )
                star_x = draw_x + self.width // 2 + 30 * math.cos(angle)
                star_y = draw_y - 20 + 15 * math.sin(angle)
                self.draw_star(screen, star_x, star_y, 6, 3)

    def draw_pattern_effects(self, screen, draw_x, draw_y):
        if not self.current_pattern_obj:
            return

        if self.pattern == "jump" and self.current_pattern_obj.phase == 0:
            pygame.draw.rect(
                screen, YELLOW, (draw_x, draw_y + self.height, self.width, 5)
            )

        elif self.pattern == "flame" and self.current_pattern_obj.phase == 0:
            charge_size = int(5 + (self.current_pattern_obj.timer / 40) * 15)
            magic_x = int(draw_x + (self.width if self.facing_right else 0))
            magic_y = int(draw_y + 30)
            pygame.draw.circle(screen, ORANGE, (magic_x, magic_y), charge_size, 2)
            pygame.draw.circle(screen, RED, (magic_x, magic_y), charge_size - 5, 2)

        elif self.pattern == "charge" and self.current_pattern_obj.phase == 0:
            arrow_x = draw_x + (self.width + 30 if self.facing_right else -30)
            pygame.draw.polygon(
                screen,
                RED,
                [
                    (arrow_x, draw_y + self.height // 2),
                    (
                        arrow_x + (20 if self.facing_right else -20),
                        draw_y + self.height // 2 - 10,
                    ),
                    (
                        arrow_x + (20 if self.facing_right else -20),
                        draw_y + self.height // 2 + 10,
                    ),
                ],
            )

        elif self.pattern == "charge" and self.current_pattern_obj.phase == 1:
            trail_x = draw_x - self.velocity_x
            trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            trail_surface.fill((*CYAN, 100))
            screen.blit(trail_surface, (trail_x, draw_y))

        elif self.pattern == "slash" and self.current_pattern_obj.phase == 0:
            sword_x = draw_x + self.width // 2
            sword_y = draw_y - 20
            pygame.draw.line(
                screen, WHITE, (sword_x, sword_y), (sword_x, sword_y + 30), 5
            )
            pygame.draw.circle(screen, GOLD, (sword_x, sword_y), 8)

        elif self.pattern == "slash" and self.current_pattern_obj.phase == 1:
            sword_x = draw_x + (self.width if self.facing_right else 0)
            sword_y = draw_y + 30
            swing_angle = (self.current_pattern_obj.timer % 15) * 12

            length = 50
            end_x = sword_x + length * math.cos(
                math.radians(swing_angle if self.facing_right else 180 - swing_angle)
            )
            end_y = sword_y - length * math.sin(math.radians(swing_angle))
            pygame.draw.line(
                screen, WHITE, (sword_x, sword_y), (int(end_x), int(end_y)), 5
            )
            pygame.draw.line(
                screen, CYAN, (sword_x, sword_y), (int(end_x), int(end_y)), 2
            )

    def draw_star(self, surface, x, y, outer_radius, inner_radius, points=5):
        star_points = []
        for i in range(points * 2):
            angle = math.pi / 2 + (i * math.pi / points)
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + radius * math.cos(angle)
            py = y - radius * math.sin(angle)
            star_points.append((px, py))

        pygame.draw.polygon(surface, YELLOW, star_points)
