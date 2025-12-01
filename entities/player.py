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

        self.trail_positions = []
        self.max_trail_length = 8

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
            self.assets.play_sound("jump", volume=0.4)

        self.x += self.velocity_x
        self.check_screen_bounds()
        self.check_platform_collision_horizontal(platforms)

        self.apply_gravity()
        self.y += self.velocity_y
        self.check_platform_collision_vertical(platforms)

        if self.dash_duration > 0:
            self.trail_positions.append((self.x + self.width // 2, self.y + self.height // 2))
            if len(self.trail_positions) > self.max_trail_length:
                self.trail_positions.pop(0)
        else:
            if len(self.trail_positions) > 0:
                self.trail_positions.pop(0)

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
            self.assets.play_sound("damage", volume=0.5)

            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.set_animation("death")
                self.assets.play_sound("death", volume=0.6)

    def heal(self, amount=1):
        self.health = min(self.health + amount, self.max_health)

    def start_dash(self):
        if self.dash_cooldown <= 0:
            self.dash_direction = 1 if self.facing_right else -1
            self.dash_duration = PLAYER_DASH_DURATION
            self.dash_cooldown = PLAYER_DASH_COOLDOWN
            self.invincible_time = PLAYER_INVINCIBLE_FRAMES
            self.assets.play_sound("dash", volume=0.4)
            return True
        return False

    def can_attack(self):
        return self.has_sword and self.attack_cooldown <= 0

    def start_attack(self):
        if self.can_attack():
            self.attacking = True
            self.attack_animation_timer = 15
            self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
            self.assets.play_sound("attack", volume=0.5)
            return True
        return False

    def can_ranged_attack(self):
        return self.ranged_attack_cooldown <= 0

    def start_ranged_attack(self):
        if self.can_ranged_attack():
            self.ranged_attack_cooldown = PLAYER_RANGED_COOLDOWN
            self.assets.play_sound("projectile", volume=0.4)
            return True
        return False

    def draw(self, screen, shake_offset=(0, 0)):
        from utils.effects import draw_trail, draw_glow, draw_sword_slash
        import math

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if len(self.trail_positions) > 1:
            adjusted_positions = [
                (pos[0] + shake_offset[0], pos[1] + shake_offset[1])
                for pos in self.trail_positions
            ]
            draw_trail(screen, adjusted_positions, CYAN, 8)

        if self.dash_duration > 0:
            draw_glow(
                screen,
                int(draw_x + self.width // 2),
                int(draw_y + self.height // 2),
                30,
                CYAN,
                0.7,
            )

        if self.attacking and self.attack_animation_timer > 10:
            slash_x = draw_x + (self.width if self.facing_right else -40)
            slash_y = draw_y + self.height // 4
            angle = -0.5 if self.facing_right else 0.5
            draw_sword_slash(screen, slash_x, slash_y, 60, 40, angle, CYAN)

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

            sprite_offset_y = sprite.get_height() - self.height
            screen.blit(sprite, (draw_x, draw_y - sprite_offset_y))
        else:
            if self.hit_flash > 0:
                color = WHITE
            else:
                color = BLUE

            pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
            pygame.draw.rect(
                screen, BLACK, (draw_x, draw_y, self.width, self.height), 2
            )
