
import pygame
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *


class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.type = enemy_type
        self.health = 1
        self.velocity_x = SKELETON_SPEED if enemy_type == "skeleton" else 0
        self.velocity_y = 0
        self.direction = 1
        self.on_ground = False
        self.alive = True
        self.attack_timer = 0
        self.jump_timer = 0

    def update(self, platforms, player):
        
        if not self.alive:
            return

        # 중력 적용
        self.velocity_y += PLAYER_GRAVITY
        self.y += self.velocity_y

        # 수평 이동
        self.x += self.velocity_x

        # 충돌 처리
        self.on_ground = False
        for platform in platforms:
            if not platform.visible:
                continue

            if (
                self.x < platform.x + platform.width
                and self.x + self.width > platform.x
                and self.y < platform.y + platform.height
                and self.y + self.height > platform.y
            ):
                # 수직 충돌
                if self.velocity_y > 0:
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True

                # 수평 충돌 (벽)
                if self.velocity_x > 0:
                    self.x = platform.x - self.width
                    self.direction *= -1
                    self.velocity_x *= -1
                elif self.velocity_x < 0:
                    self.x = platform.x + platform.width
                    self.direction *= -1
                    self.velocity_x *= -1

        # 적 타입별 행동
        if self.type == "skeleton":
            # 해골병사: 좌우로 왔다갔다
            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
                self.direction *= -1
                self.velocity_x *= -1

        elif self.type == "slime":
            # 슬라임: 불규칙한 점프
            self.jump_timer += 1
            if self.on_ground and self.jump_timer > random.randint(60, 120):
                self.velocity_y = -SLIME_JUMP_POWER
                self.velocity_x = random.choice([-2, 2])
                self.jump_timer = 0

        elif self.type == "mage":
            # 마법사: 제자리에서 공격
            self.attack_timer += 1
            # 플레이어를 향해 바라보기
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1

    def draw(self, screen, shake_offset=(0, 0)):
        
        if not self.alive:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.type == "skeleton":
            # 해골병사 (회색)
            pygame.draw.rect(screen, GRAY, (draw_x, draw_y, self.width, self.height))
            # 해골 머리
            pygame.draw.circle(screen, WHITE, (int(draw_x + 15), int(draw_y + 10)), 8)
            pygame.draw.circle(screen, BLACK, (int(draw_x + 12), int(draw_y + 8)), 2)
            pygame.draw.circle(screen, BLACK, (int(draw_x + 18), int(draw_y + 8)), 2)

        elif self.type == "slime":
            # 슬라임 (녹색, 둥근 모양)
            pygame.draw.ellipse(
                screen, GREEN, (draw_x, draw_y + 10, self.width, self.height - 10)
            )
            # 눈
            pygame.draw.circle(screen, BLACK, (int(draw_x + 10), int(draw_y + 20)), 3)
            pygame.draw.circle(screen, BLACK, (int(draw_x + 20), int(draw_y + 20)), 3)

        elif self.type == "mage":
            # 마법사 (보라색)
            pygame.draw.rect(screen, PURPLE, (draw_x, draw_y, self.width, self.height))
            # 모자
            points = [
                (draw_x + 5, draw_y + 5),
                (draw_x + 25, draw_y + 5),
                (draw_x + 15, draw_y - 10),
            ]
            pygame.draw.polygon(screen, DARK_GRAY, points)
            # 눈
            pygame.draw.circle(screen, YELLOW, (int(draw_x + 15), int(draw_y + 15)), 4)

            # 공격 차징 표시
            if self.attack_timer > 100:
                charge_progress = (self.attack_timer - 100) / 20
                size = int(5 + charge_progress * 10)
                magic_x = draw_x + 15 + (self.direction * 20)
                magic_y = draw_y + 15
                pygame.draw.circle(screen, PINK, (int(magic_x), int(magic_y)), size, 2)
