
import pygame
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.width = ITEM_WIDTH
        self.height = ITEM_HEIGHT
        self.type = item_type
        self.collected = False

    def draw(self, screen, shake_offset=(0, 0)):
        
        if self.collected:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.type == "health":
            # 체력 회복 포션 (빨간 하트)
            pygame.draw.rect(screen, RED, (draw_x, draw_y, self.width, self.height))
            pygame.draw.circle(screen, PINK, (int(draw_x + 15), int(draw_y + 15)), 8)

        elif self.type == "max_health":
            # 최대 체력 증가 (금색 하트)
            pygame.draw.rect(screen, GOLD, (draw_x, draw_y, self.width, self.height))
            pygame.draw.circle(screen, YELLOW, (int(draw_x + 15), int(draw_y + 15)), 8)

        elif self.type == "speed":
            # 이속 증가 (파란 번개)
            pygame.draw.polygon(
                screen,
                CYAN,
                [
                    (draw_x + 15, draw_y),
                    (draw_x + 10, draw_y + 15),
                    (draw_x + 15, draw_y + 15),
                    (draw_x + 10, draw_y + 30),
                    (draw_x + 20, draw_y + 15),
                    (draw_x + 15, draw_y + 15),
                ],
            )

        elif self.type == "sword":
            # 검 (회색 검)
            pygame.draw.rect(screen, GRAY, (draw_x + 10, draw_y + 5, 10, 20))
            pygame.draw.rect(screen, GOLD, (draw_x + 8, draw_y + 15, 14, 5))
            pygame.draw.circle(screen, GOLD, (int(draw_x + 15), int(draw_y + 5)), 5)


class Chest:
    def __init__(self, x, y, item):
        self.x = x
        self.y = y
        self.width = CHEST_WIDTH
        self.height = CHEST_HEIGHT
        self.item = item
        self.opened = False
        self.open_animation = 0

    def draw(self, screen, shake_offset=(0, 0)):
        
        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.opened:
            # 열린 상자
            color = DARK_GRAY
            # 뚜껑이 열린 상태
            pygame.draw.rect(
                screen, color, (draw_x, draw_y + 15, self.width, self.height - 15)
            )
            pygame.draw.rect(
                screen, ORANGE, (draw_x, draw_y, self.width, 15), 2
            )  # 열린 뚜껑
        else:
            # 닫힌 상자
            color = ORANGE
            pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
            pygame.draw.rect(screen, GOLD, (draw_x + 15, draw_y + 15, 10, 10))  # 자물쇠

            # 반짝임 효과
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.circle(
                    screen, YELLOW, (int(draw_x + 10), int(draw_y + 10)), 3
                )


class Trap:
    def __init__(self, x, y, trap_type):
        self.x = x
        self.y = y
        self.type = trap_type
        self.width = TRAP_WIDTH
        self.height = TRAP_HEIGHT
        self.timer = 0
        self.active = True
        self.falling = False
        self.original_x = x
        self.original_y = y
        self.velocity_y = 0

    def update(self, player):
        
        self.timer += 1

        if self.type == "blade":
            # 움직이는 칼날
            self.x = self.original_x + 100 * (1 if (self.timer // 60) % 2 == 0 else -1)

        elif self.type == "spike":
            # 떨어지는 가시
            if not self.falling:
                # 플레이어가 아래 지나가면 떨어짐
                if abs(player.x - self.x) < 50 and player.y > self.y:
                    self.falling = True
            else:
                self.velocity_y += 0.5
                self.y += self.velocity_y
                if self.y > SCREEN_HEIGHT:
                    self.active = False

        elif self.type == "fireball":
            # 불덩이 발사 장치
            if self.timer >= FIREBALL_INTERVAL:
                self.timer = 0
                return True  # 발사 신호

        return False

    def draw(self, screen, shake_offset=(0, 0)):
        
        if not self.active:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.type == "blade":
            # 칼날 (회전하는 톱날)
            import math

            angle = (self.timer * 10) % 360
            center_x = draw_x + self.width // 2
            center_y = draw_y + self.height // 2

            # 톱날 그리기
            pygame.draw.circle(screen, GRAY, (int(center_x), int(center_y)), 20)

            # 날 부분
            for i in range(8):
                blade_angle = math.radians(angle + i * 45)
                blade_x = center_x + 25 * math.cos(blade_angle)
                blade_y = center_y + 25 * math.sin(blade_angle)
                pygame.draw.line(
                    screen,
                    RED,
                    (int(center_x), int(center_y)),
                    (int(blade_x), int(blade_y)),
                    3,
                )

        elif self.type == "spike":
            # 가시 (삼각형들)
            if not self.falling:
                # 경고 표시
                if self.timer % 60 < 30:
                    pygame.draw.rect(screen, RED, (draw_x, draw_y - 5, self.width, 3))

            for i in range(4):
                spike_x = draw_x + i * 10
                points = [
                    (spike_x, draw_y + self.height),
                    (spike_x + 5, draw_y),
                    (spike_x + 10, draw_y + self.height),
                ]
                pygame.draw.polygon(screen, GRAY, points)

        elif self.type == "fireball":
            # 발사 장치
            pygame.draw.rect(
                screen, DARK_GRAY, (draw_x, draw_y, self.width, self.height)
            )

            # 차징 표시
            if self.timer > FIREBALL_INTERVAL - 30:
                charge = (self.timer - (FIREBALL_INTERVAL - 30)) / 30
                pygame.draw.circle(
                    screen,
                    ORANGE,
                    (int(draw_x + self.width // 2), int(draw_y + self.height // 2)),
                    int(5 + charge * 10),
                    2,
                )


class Checkpoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.activated = False
        self.animation_timer = 0

    def check_activation(self, player):
        """플레이어가 체크포인트에 닿았는지 확인"""
        if not self.activated:
            if (player.x < self.x + self.width and 
                player.x + player.width > self.x and
                player.y < self.y + self.height and
                player.y + player.height > self.y):
                self.activated = True
                return True
        return False

    def draw(self, screen, shake_offset=(0, 0)):
        """체크포인트 그리기"""
        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]
        
        self.animation_timer += 1
        
        if self.activated:
            # 활성화된 체크포인트 (초록색 깃발)
            color = GREEN
            # 깃발 흔들림 효과
            wave = 3 * (1 if (self.animation_timer // 10) % 2 == 0 else -1)
            
            # 깃발 기둥
            pygame.draw.rect(screen, DARK_GRAY, (draw_x + 5, draw_y, 5, self.height))
            
            # 깃발
            flag_points = [
                (draw_x + 10, draw_y + 5),
                (draw_x + 35 + wave, draw_y + 15),
                (draw_x + 10, draw_y + 25)
            ]
            pygame.draw.polygon(screen, color, flag_points)
            
            # 빛나는 효과
            if self.animation_timer % 60 < 30:
                pygame.draw.circle(screen, YELLOW, (int(draw_x + 20), int(draw_y + 15)), 5, 2)
        else:
            # 비활성화된 체크포인트 (회색 깃발)
            color = GRAY
            
            # 깃발 기둥
            pygame.draw.rect(screen, DARK_GRAY, (draw_x + 5, draw_y, 5, self.height))
            
            # 깃발
            flag_points = [
                (draw_x + 10, draw_y + 5),
                (draw_x + 35, draw_y + 15),
                (draw_x + 10, draw_y + 25)
            ]
            pygame.draw.polygon(screen, color, flag_points)


class Platform:
    def __init__(self, x, y, width, height, disappearing=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.disappearing = disappearing
        self.timer = 0
        self.visible = True
        self.original_visible = True
        self.warning = False
        self.collapsing = False
        self.collapse_timer = 0

    def update(self, player):
        
        if not self.disappearing or not self.visible:
            return

        # 플레이어가 밟고 있는지 체크
        if (
            player.x < self.x + self.width
            and player.x + player.width > self.x
            and player.y + player.height >= self.y
            and player.y + player.height <= self.y + 10
            and player.on_ground
        ):
            self.timer += 1
            if self.timer > DISAPPEARING_PLATFORM_TIMER:
                self.visible = False
                self.timer = 0
        else:
            # 플레이어가 떠나면 다시 나타남
            if self.timer > 0:
                self.timer = max(0, self.timer - 1)
            if not self.visible and self.timer == 0:
                import time

                # 3초 후 재생성
                self.visible = True

    def start_collapse(self):
        
        if not self.collapsing:
            self.collapsing = True
            self.collapse_timer = 0
            self.warning = True

    def update_collapse(self):
        
        if not self.collapsing:
            return False

        self.collapse_timer += 1

        if self.collapse_timer < PLATFORM_COLLAPSE_WARNING:
            # 경고 단계
            self.warning = True
        elif self.collapse_timer < PLATFORM_COLLAPSE_WARNING + 30:
            # 금 가는 단계
            pass
        else:
            # 완전히 붕괴
            self.visible = False
            return True

        return False

    def draw(self, screen, shake_offset=(0, 0)):

        if not self.visible:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        # 플랫폼 색상 결정
        if self.collapsing and self.warning:
            # 붕괴 중 - 빨간색 깜빡임
            if self.collapse_timer % 20 < 10:
                color = RED
            else:
                color = DARK_GRAY
        elif self.disappearing:
            # 사라지는 발판
            color = (120, 120, 140)
            if self.timer > 0:
                # 투명도 효과 (Surface로 처리)
                alpha = int(255 * (1 - self.timer / DISAPPEARING_PLATFORM_TIMER))
                platform_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                platform_surface.fill((*color, alpha))
                screen.blit(platform_surface, (draw_x, draw_y))
                pygame.draw.rect(screen, BLACK, (draw_x, draw_y, self.width, self.height), 2)
                return
        else:
            # 일반 발판
            color = DARK_GRAY

        # 플랫폼 박스 그리기
        pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))

        # 테두리
        pygame.draw.rect(screen, BLACK, (draw_x, draw_y, self.width, self.height), 2)

        # 붕괴 중 금 가는 효과
        if self.collapsing and self.collapse_timer >= PLATFORM_COLLAPSE_WARNING:
            import random

            for _ in range(3):
                crack_x1 = draw_x + random.randint(0, int(self.width))
                crack_y1 = draw_y + random.randint(0, int(self.height))
                crack_x2 = crack_x1 + random.randint(-20, 20)
                crack_y2 = crack_y1 + random.randint(-20, 20)
                pygame.draw.line(
                    screen, BLACK, (crack_x1, crack_y1), (crack_x2, crack_y2), 2
                )
