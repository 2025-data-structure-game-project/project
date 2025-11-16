
import pygame
import random
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BOSS_WIDTH
        self.height = BOSS_HEIGHT
        self.max_health = BOSS_MAX_HEALTH
        self.health = BOSS_MAX_HEALTH
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

        # 패턴 관련
        self.pattern = None
        self.pattern_timer = 0
        self.pattern_phase = 0  # 패턴 단계 (예고, 실행, 종료)
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.attack_cooldown = 0

        # 상태
        self.stunned = False
        self.stun_timer = 0
        self.facing_right = True
        self.berserk_mode = False
        self.platform_collapsed = False

        # 이펙트
        self.hit_flash = 0
        self.charge_particles = []
        self.warning_timer = 0

        # AI
        self.last_pattern = None
        self.pattern_count = 0

    def update(self, player, platforms, projectiles):

        # 쿨다운 감소
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.vulnerable = False
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.warning_timer > 0:
            self.warning_timer -= 1

        # 스턴 상태
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
            return None, []

        # 중력 적용
        self.velocity_y += BOSS_GRAVITY
        self.y += self.velocity_y
        self.x += self.velocity_x

        # 화면 밖으로 나가지 않도록
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
            self.enter_stun("wall")
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.velocity_x = 0
            self.enter_stun("wall")

        # 발판 충돌
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
                if self.velocity_y > 0:
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True

                    # 돌진 중 충돌
                    if self.pattern == "charge" and abs(self.velocity_x) > 10:
                        self.velocity_x = 0
                        self.enter_stun("charge")

        # 광폭 모드 체크
        if self.health <= BOSS_VULNERABLE_THRESHOLD and not self.berserk_mode:
            self.enter_berserk_mode()

        # 패턴 실행
        actions = []
        if self.pattern is None and self.attack_cooldown <= 0:
            self.choose_pattern(player)

        if self.pattern:
            action = self.execute_pattern(player, projectiles)
            if action:
                actions.append(action)

        # 플레이어 방향 바라보기
        if self.pattern not in ["charge"] and not self.stunned:
            self.facing_right = player.x > self.x

        return self.pattern, actions

    def choose_pattern(self, player):
        
        distance = abs(player.x - self.x)
        player_above = player.y < self.y - 50

        # 가중치 기반 패턴 선택
        patterns = []
        weights = []

        if self.berserk_mode:
            # 광폭 모드: 모든 패턴 균등
            patterns = ["jump", "flame", "charge", "slash", "teleport"]
            weights = [20, 20, 20, 20, 20]
        else:
            # HP에 따른 가중치
            hp_percent = (self.health / self.max_health) * 100

            if distance < 100:
                # 근거리
                patterns = ["slash", "jump"]
                weights = [60, 40]
            elif distance < 300:
                # 중거리
                patterns = ["charge", "slash", "flame"]
                weights = [40, 30, 30]
            else:
                # 원거리
                patterns = ["flame", "jump", "charge"]
                weights = [50, 30, 20]

            # HP가 낮을수록 공격적인 패턴
            if hp_percent < 50:
                if "charge" in patterns:
                    idx = patterns.index("charge")
                    weights[idx] += 20

        # 같은 패턴 연속 사용 방지
        if self.last_pattern in patterns:
            idx = patterns.index(self.last_pattern)
            weights[idx] = max(5, weights[idx] - 30)

        # 가중치 기반 선택
        self.pattern = random.choices(patterns, weights=weights)[0]
        self.last_pattern = self.pattern
        self.pattern_timer = 0
        self.pattern_phase = 0
        self.facing_right = player.x > self.x
        self.warning_timer = 45  # 예고 시간

    def execute_pattern(self, player, projectiles):
        
        self.pattern_timer += 1

        if self.pattern == "jump":
            return self.pattern_jump(player)
        elif self.pattern == "flame":
            return self.pattern_flame(player, projectiles)
        elif self.pattern == "charge":
            return self.pattern_charge(player)
        elif self.pattern == "slash":
            return self.pattern_slash(player)
        elif self.pattern == "teleport":
            return self.pattern_teleport(player)

        return None

    def pattern_jump(self, player):
        
        if self.pattern_phase == 0:
            # 예고 단계
            if self.pattern_timer >= 30:
                self.pattern_phase = 1
                self.velocity_y = -BOSS_JUMP_POWER
                self.pattern_timer = 0

        elif self.pattern_phase == 1:
            # 점프 중 - 플레이어 위치 약간 추적
            if self.velocity_y > 0:
                target_x = player.x - self.width // 2
                if abs(self.x - target_x) > 5:
                    self.velocity_x = 3 if target_x > self.x else -3

            # 착지
            if self.on_ground and self.pattern_timer > 10:
                self.pattern_phase = 2
                self.pattern_timer = 0
                self.velocity_x = 0
                self.enter_vulnerable(90)
                return (
                    "shockwave",
                    {"x": self.x + self.width // 2, "y": self.y + self.height},
                )

        elif self.pattern_phase == 2:
            # 회복 중
            if self.pattern_timer >= 90:
                self.end_pattern()

        return None

    def pattern_flame(self, player, projectiles):
        
        if self.pattern_phase == 0:
            # 차징 단계
            if self.pattern_timer >= 40:
                self.pattern_phase = 1
                self.pattern_timer = 0

        elif self.pattern_phase == 1:
            # 발사 단계 (3연발)
            if self.pattern_timer in [10, 20, 30]:
                direction = 1 if self.facing_right else -1
                # 각도 변화
                angle_offset = [0, -0.3, 0.3][self.pattern_timer // 10 - 1]
                return ("flame", {"direction": direction, "angle": angle_offset})

            if self.pattern_timer >= 40:
                self.pattern_phase = 2
                self.pattern_timer = 0
                self.enter_vulnerable(60)

        elif self.pattern_phase == 2:
            # 휴식
            if self.pattern_timer >= 60:
                self.end_pattern()

        return None

    def pattern_charge(self, player):
        
        if self.pattern_phase == 0:
            # 예고 단계
            if self.pattern_timer >= 45:
                self.pattern_phase = 1
                self.pattern_timer = 0
                self.velocity_x = (
                    BOSS_CHARGE_SPEED if self.facing_right else -BOSS_CHARGE_SPEED
                )

        elif self.pattern_phase == 1:
            # 돌진 중
            if self.stunned:
                self.pattern_phase = 2
                self.pattern_timer = 0

        elif self.pattern_phase == 2:
            # 스턴 상태는 enter_stun에서 처리
            if not self.stunned:
                self.end_pattern()

        return None

    def pattern_slash(self, player):
        
        if self.pattern_phase == 0:
            # 준비 단계
            if self.pattern_timer >= 30:
                self.pattern_phase = 1
                self.pattern_timer = 0

        elif self.pattern_phase == 1:
            # 3연속 베기
            if self.pattern_timer in [10, 25, 40]:
                slash_num = self.pattern_timer // 15
                return (
                    "slash",
                    {"num": slash_num, "direction": 1 if self.facing_right else -1},
                )

            if self.pattern_timer >= 50:
                self.pattern_phase = 2
                self.pattern_timer = 0
                self.enter_vulnerable(60)

        elif self.pattern_phase == 2:
            # 휴식
            if self.pattern_timer >= 60:
                self.end_pattern()

        return None

    def pattern_teleport(self, player):
        
        if self.pattern_phase == 0:
            if self.pattern_timer >= 20:
                # 플레이어 근처로 텔레포트
                offset = 80 if random.random() > 0.5 else -80
                self.x = player.x + offset
                self.y = player.y - 100
                self.pattern_phase = 1
                self.pattern_timer = 0
                return ("teleport", {})

        elif self.pattern_phase == 1:
            # 즉시 검 휘두르기
            if self.pattern_timer == 5:
                return (
                    "slash",
                    {"num": 0, "direction": 1 if self.facing_right else -1},
                )
            if self.pattern_timer >= 20:
                self.end_pattern()

        return None

    def enter_vulnerable(self, duration):
        
        if self.health > BOSS_VULNERABLE_THRESHOLD:
            self.vulnerable = True
            self.vulnerable_timer = duration
        # HP 10% 이하면 항상 vulnerable

    def enter_stun(self, reason):
        
        self.stunned = True
        self.stun_timer = BOSS_CHARGE_STUN_DURATION
        self.vulnerable = True
        self.vulnerable_timer = BOSS_CHARGE_STUN_DURATION
        self.velocity_x = 0

    def enter_berserk_mode(self):
        
        self.berserk_mode = True
        self.vulnerable = True  # 항상 공격 가능
        self.attack_cooldown = 0

    def end_pattern(self):
        
        self.pattern = None
        self.pattern_timer = 0
        self.pattern_phase = 0

        if self.berserk_mode:
            self.attack_cooldown = BOSS_PATTERN_COOLDOWN_BERSERK
        else:
            self.attack_cooldown = BOSS_PATTERN_COOLDOWN_NORMAL

    def take_damage(self, amount):
        
        # HP 11% 이상일 때는 vulnerable 체크
        if self.health > BOSS_VULNERABLE_THRESHOLD and not self.vulnerable:
            return False  # 막힘

        self.health = max(0, self.health - amount)
        self.hit_flash = HIT_FLASH_DURATION

        # 약간 넉백
        knockback = 10 if self.facing_right else -10
        self.velocity_x = -knockback

        return True

    def can_be_damaged(self):
        
        return self.health <= BOSS_VULNERABLE_THRESHOLD or self.vulnerable

    def draw(self, screen, shake_offset=(0, 0)):

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        # 보스 박스 색상 결정
        if self.hit_flash > 0:
            color = WHITE  # 피격 시 하얀색
        elif self.stunned:
            color = GRAY  # 스턴 시 회색
        elif self.berserk_mode:
            color = DARK_RED  # 광폭 모드 시 어두운 빨강
        else:
            color = RED  # 기본 빨강

        # 보스 박스 그리기
        pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))

        # 테두리
        pygame.draw.rect(screen, BLACK, (draw_x, draw_y, self.width, self.height), 3)

        # 방어막 (vulnerable 아닐 때)
        if not self.can_be_damaged() and self.health > BOSS_VULNERABLE_THRESHOLD:
            # 보라색 방어막
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

        # vulnerable 표시
        if self.vulnerable and self.health > BOSS_VULNERABLE_THRESHOLD:
            # 노란 별
            for i in range(3):
                angle = (pygame.time.get_ticks() / 500 + i * 2 * math.pi / 3) % (
                    2 * math.pi
                )
                star_x = draw_x + self.width // 2 + 40 * math.cos(angle)
                star_y = draw_y + self.height // 2 + 40 * math.sin(angle)
                self.draw_star(screen, star_x, star_y, 8, 4)

        # 광폭 모드 오라
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

        # 패턴별 이펙트
        if self.pattern == "jump" and self.pattern_phase == 0:
            # 점프 예고 - 무릎 굽히기
            pygame.draw.rect(
                screen, YELLOW, (draw_x, draw_y + self.height, self.width, 5)
            )

        elif self.pattern == "flame" and self.pattern_phase == 0:
            # 화염 차징
            charge_size = int(5 + (self.pattern_timer / 40) * 15)
            magic_x = int(draw_x + (self.width if self.facing_right else 0))
            magic_y = int(draw_y + 30)
            pygame.draw.circle(screen, ORANGE, (magic_x, magic_y), charge_size, 2)
            pygame.draw.circle(screen, RED, (magic_x, magic_y), charge_size - 5, 2)

        elif self.pattern == "charge" and self.pattern_phase == 0:
            # 돌진 예고
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

        elif self.pattern == "charge" and self.pattern_phase == 1:
            # 돌진 중 잔상
            trail_x = draw_x - self.velocity_x
            trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            trail_surface.fill((*CYAN, 100))
            screen.blit(trail_surface, (trail_x, draw_y))

        elif self.pattern == "slash" and self.pattern_phase == 0:
            # 검 들어올리기
            sword_x = draw_x + self.width // 2
            sword_y = draw_y - 20
            pygame.draw.line(
                screen, WHITE, (sword_x, sword_y), (sword_x, sword_y + 30), 5
            )
            pygame.draw.circle(screen, GOLD, (sword_x, sword_y), 8)

        elif self.pattern == "slash" and self.pattern_phase == 1:
            # 검 휘두르기
            sword_x = draw_x + (self.width if self.facing_right else 0)
            sword_y = draw_y + 30
            swing_angle = (self.pattern_timer % 15) * 12  # 0 ~ 180도

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

        # 스턴 상태 - 별이 빙글빙글
        if self.stunned:
            for i in range(3):
                angle = (pygame.time.get_ticks() / 300 + i * 2 * math.pi / 3) % (
                    2 * math.pi
                )
                star_x = draw_x + self.width // 2 + 30 * math.cos(angle)
                star_y = draw_y - 20 + 15 * math.sin(angle)
                self.draw_star(screen, star_x, star_y, 6, 3)

    def draw_star(self, surface, x, y, outer_radius, inner_radius, points=5):
        
        star_points = []
        for i in range(points * 2):
            angle = math.pi / 2 + (i * math.pi / points)
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + radius * math.cos(angle)
            py = y - radius * math.sin(angle)
            star_points.append((px, py))

        pygame.draw.polygon(surface, YELLOW, star_points)
