import pygame

from config import *
from entities.base_entity import AnimatedEntity
from systems.asset_manager import get_asset_manager


class Player(AnimatedEntity):
    def __init__(self, x, y):
        super().__init__(
            x, y, PLAYER_WIDTH, PLAYER_HEIGHT, max_health=PLAYER_MAX_HEARTS
        )

        self.assets = get_asset_manager()

        self.speed = PLAYER_SPEED
        self.jump_power = PLAYER_JUMP_POWER

        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_direction = 0

        self.has_sword = False
        self.speed_boost = 0

        self.attack_cooldown = 0
        self.attacking = False
        self.attack_animation_timer = 0
        self.ranged_attack_cooldown = 0

    def update(self, keys, platforms):
        self.update_timers()
        self.update_animation()

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.ranged_attack_cooldown > 0:
            self.ranged_attack_cooldown -= 1
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= 1
        else:
            self.attacking = False

        if self.dash_duration > 0:
            self.velocity_x = self.dash_direction * PLAYER_DASH_SPEED
            self.dash_duration -= 1
            if self.dash_duration == 0:
                self.velocity_x = 0
        else:
            self.velocity_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity_x = -(self.speed + self.speed_boost)
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity_x = self.speed + self.speed_boost
                self.facing_right = True

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False

        self.x += self.velocity_x
        self.check_screen_bounds()
        self.check_platform_collision_horizontal(platforms)

        self.apply_gravity()
        self.y += self.velocity_y
        self.check_platform_collision_vertical(platforms)

        if not self.on_ground:
            if self.velocity_y < 0:
                self.set_animation("jump")
            else:
                self.set_animation("fall")
        elif abs(self.velocity_x) > 0:
            self.set_animation("run")
        elif self.attacking:
            self.set_animation("attack")
        else:
            self.set_animation("idle")

    def take_damage(self, amount=1):
        if self.invincible_time <= 0:
            self.health -= amount
            self.invincible_time = 60
            self.hit_flash = HIT_FLASH_DURATION

            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.set_animation("death")

    def heal(self, amount=1):
        self.health = min(self.health + amount, self.max_health)

    def start_dash(self):
        if self.dash_cooldown <= 0:
            self.dash_direction = 1 if self.facing_right else -1
            self.dash_duration = PLAYER_DASH_DURATION
            self.dash_cooldown = PLAYER_DASH_COOLDOWN
            self.invincible_time = PLAYER_INVINCIBLE_FRAMES
            return True
        return False

    def can_attack(self):
        return self.has_sword and self.attack_cooldown <= 0

    def start_attack(self):
        if self.can_attack():
            self.attacking = True
            self.attack_animation_timer = 15
            self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
            return True
        return False

    def can_ranged_attack(self):
        return self.ranged_attack_cooldown <= 0

    def start_ranged_attack(self):
        if self.can_ranged_attack():
            self.ranged_attack_cooldown = PLAYER_RANGED_COOLDOWN
            return True
        return False

    def draw(self, screen, shake_offset=(0, 0)):
        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.invincible_time > 0 and self.invincible_time % 10 < 5:
            return

        sprite_key = f"player_{self.current_animation}"
        sprite = self.assets.get_sprite(sprite_key)

        if sprite:
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)

            if self.hit_flash > 0:
                sprite = sprite.copy()
                sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(sprite, (draw_x, draw_y))
        else:
            if self.hit_flash > 0:
                color = WHITE
            else:
                color = BLUE

            pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
            pygame.draw.rect(
                screen, BLACK, (draw_x, draw_y, self.width, self.height), 2
            )

        if self.has_sword:
            sword_x = draw_x + self.width if self.facing_right else draw_x - 20
            sword_y = draw_y + 15

            if self.attacking and self.attack_animation_timer > 0:
                import math

                progress = 1 - (self.attack_animation_timer / 15)
                angle = -45 + (progress * 90)

                length = 25
                center_x = sword_x + 10 if self.facing_right else sword_x
                center_y = sword_y

                rad = math.radians(angle if self.facing_right else 180 - angle)
                end_x = center_x + length * math.cos(rad)
                end_y = center_y - length * math.sin(rad)

                pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), 4)
                pygame.draw.line(screen, CYAN, (center_x, center_y), (end_x, end_y), 2)
            else:
                pygame.draw.rect(screen, GRAY, (sword_x, sword_y, 20, 5))

        if self.dash_duration > 0:
            trail_x = draw_x - self.dash_direction * 15
            trail_alpha = 100
            trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            trail_surface.fill((*CYAN, trail_alpha))
            screen.blit(trail_surface, (trail_x, draw_y))
