import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = PLAYER_SPEED
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity = PLAYER_GRAVITY
        self.on_ground = False

        # 체력
        self.max_hearts = PLAYER_MAX_HEARTS
        self.hearts = PLAYER_MAX_HEARTS

        # 대시
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_direction = 0

        # 무적 시간
        self.invincible_time = 0

        # 아이템
        self.has_sword = False
        self.speed_boost = 0

        # 애니메이션
        self.facing_right = True
        self.attack_cooldown = 0
        self.attacking = False
        self.attack_animation_timer = 0
        self.ranged_attack_cooldown = 0

        # 피격 효과
        self.hit_flash = 0

    def update(self, keys, platforms):
        # 쿨다운 감소
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.ranged_attack_cooldown > 0:
            self.ranged_attack_cooldown -= 1
        if self.invincible_time > 0:
            self.invincible_time -= 1
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= 1
        else:
            self.attacking = False
        if self.hit_flash > 0:
            self.hit_flash -= 1

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

        # 점프
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False

        # 수평 이동
        self.x += self.velocity_x
        
        # 화면 경계 체크
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        
        self.check_horizontal_collision(platforms)

        # 수직 이동
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.on_ground = False
        self.check_vertical_collision(platforms)

    def check_horizontal_collision(self, platforms):
        for platform in platforms:
            if (
                self.x < platform.x + platform.width
                and self.x + self.width > platform.x
                and self.y < platform.y + platform.height
                and self.y + self.height > platform.y
            ):
                if self.velocity_x > 0:
                    self.x = platform.x - self.width
                elif self.velocity_x < 0:
                    self.x = platform.x + platform.width

    def check_vertical_collision(self, platforms):
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
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.y = platform.y + platform.height
                    self.velocity_y = 0

    def take_damage(self, amount=1):
        if self.invincible_time <= 0:
            self.hearts -= amount
            self.invincible_time = 60
            self.hit_flash = HIT_FLASH_DURATION

    def heal(self, amount=1):
        self.hearts = min(self.hearts + amount, self.max_hearts)

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

        # 무적/피격 시 깜빡임
        if self.invincible_time > 0 and self.invincible_time % 10 < 5:
            return

        # 플레이어 본체
        if self.hit_flash > 0:
            color = WHITE
        else:
            color = BLUE

        pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))

        # 얼굴
        eye_y = draw_y + 10
        if self.facing_right:
            pygame.draw.circle(screen, BLACK, (int(draw_x + 20), int(eye_y)), 3)
        else:
            pygame.draw.circle(screen, BLACK, (int(draw_x + 10), int(eye_y)), 3)

        # 검 표시 (소지 중일 때)
        if self.has_sword:
            sword_x = draw_x + self.width if self.facing_right else draw_x - 20
            sword_y = draw_y + 15

            if self.attacking and self.attack_animation_timer > 0:
                # 공격 애니메이션
                progress = 1 - (self.attack_animation_timer / 15)
                angle = -45 + (progress * 90)  # -45도에서 45도로

                import math

                length = 25
                center_x = sword_x + 10 if self.facing_right else sword_x
                center_y = sword_y

                rad = math.radians(angle if self.facing_right else 180 - angle)
                end_x = center_x + length * math.cos(rad)
                end_y = center_y - length * math.sin(rad)

                pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), 4)
                pygame.draw.line(screen, CYAN, (center_x, center_y), (end_x, end_y), 2)
            else:
                # 검 대기 상태
                pygame.draw.rect(screen, GRAY, (sword_x, sword_y, 20, 5))

        # 대시 잔상 효과
        if self.dash_duration > 0:
            trail_x = draw_x - self.dash_direction * 15
            trail_alpha = 100
            trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            trail_surface.fill((*CYAN, trail_alpha))
            screen.blit(trail_surface, (trail_x, draw_y))
