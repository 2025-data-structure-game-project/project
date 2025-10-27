import pygame
import random
import math
import time

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)
GRAY = (128, 128, 128)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("용사의 탑 - 공주 구출 작전")
clock = pygame.time.Clock()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        self.on_ground = False
        self.max_hearts = 3
        self.hearts = 3
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_direction = 0
        self.invincible_time = 0
        self.has_sword = False
        self.speed_boost = 0
        self.facing_right = True
        self.attack_cooldown = 0
        self.attacking = False
        self.attack_animation_timer = 0
        self.ranged_attack_cooldown = 0
        
    def update(self, keys, platforms):
        if self.dash_duration > 0:
            self.velocity_x = self.dash_direction * 15
            self.dash_duration -= 1
            if self.dash_duration == 0:
                self.velocity_x = 0
        else:
            self.velocity_x = 0
            if keys[pygame.K_LEFT]:
                self.velocity_x = -(self.speed + self.speed_boost)
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.velocity_x = self.speed + self.speed_boost
                self.facing_right = True
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False
        
        
        self.x += self.velocity_x
        self.check_horizontal_collision(platforms)
        
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.on_ground = False
        self.check_vertical_collision(platforms)
        
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.invincible_time > 0:
            self.invincible_time -= 1
        if self.speed_boost > 0:
            self.speed_boost -= 0.01
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.ranged_attack_cooldown > 0:
            self.ranged_attack_cooldown -= 1

        # 공격 애니메이션 타이머
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= 1
            if self.attack_animation_timer == 0:
                self.attacking = False

        # 화면 밖으로 나가지 않도록 제한
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            
    def check_horizontal_collision(self, platforms):
        for platform in platforms:
            if not platform.visible:
                continue
            if (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y):
                if self.velocity_x > 0:
                    self.x = platform.x - self.width
                elif self.velocity_x < 0:
                    self.x = platform.x + platform.width
                self.velocity_x = 0
                
    def check_vertical_collision(self, platforms):
        for platform in platforms:
            if not platform.visible:
                continue
            if (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y):
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
            return True
        return False
    
    def heal(self, amount=1):
        self.hearts = min(self.hearts + amount, self.max_hearts)
        
    def draw(self, screen):
        color = WHITE if self.invincible_time % 10 < 5 or self.invincible_time == 0 else GRAY

        # 몸체
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # 얼굴
        pygame.draw.rect(screen, BLUE, (self.x + 10, self.y + 5, 10, 10))

        if self.has_sword:
            if self.attacking:
                # 근접 공격 모션 - 칼이 크게 휘둘러짐
                sword_length = 60
                if self.attack_animation_timer > 10:
                    # 공격 준비 모션
                    sword_x = self.x + 5 if self.facing_right else self.x + self.width - 25
                    pygame.draw.rect(screen, YELLOW, (sword_x, self.y + 10, 20, 5))
                else:
                    # 공격 실행 모션 - 더 크고 화려하게
                    sword_x = self.x + self.width if self.facing_right else self.x - sword_length

                    # 칼 본체
                    pygame.draw.rect(screen, YELLOW, (sword_x, self.y + 15, sword_length, 8))

                    # 칼 끝에 큰 이펙트
                    effect_x = sword_x + sword_length if self.facing_right else sword_x
                    pygame.draw.circle(screen, ORANGE, (int(effect_x), int(self.y + 19)), 15)
                    pygame.draw.circle(screen, YELLOW, (int(effect_x), int(self.y + 19)), 10)
                    pygame.draw.circle(screen, WHITE, (int(effect_x), int(self.y + 19)), 5)

                    # 칼날 빛나는 효과
                    pygame.draw.line(screen, WHITE, (sword_x, self.y + 11), (effect_x, self.y + 11), 4)

                    # 공격 궤적 이펙트 - 더 많은 원형 궤적
                    for i in range(5):
                        offset = i * 12
                        arc_x = effect_x - offset if self.facing_right else effect_x + offset
                        arc_size = 10 - i * 2
                        pygame.draw.circle(screen, YELLOW, (int(arc_x), int(self.y + 19)), arc_size, 2)

                    # 공격 범위 표시 (반투명 효과 대신 외곽선으로)
                    attack_range = 60
                    attack_rect_x = self.x + self.width if self.facing_right else self.x - attack_range
                    pygame.draw.rect(screen, RED, (attack_rect_x, self.y - 10, attack_range, 80), 3)

                    # 충격파 효과
                    wave_offset = (15 - self.attack_animation_timer) * 5
                    wave_x = effect_x + wave_offset if self.facing_right else effect_x - wave_offset
                    for i in range(3):
                        wave_size = 20 + i * 10
                        pygame.draw.circle(screen, ORANGE, (int(wave_x), int(self.y + 19)), wave_size, 2)
            else:
                # 대기 중 - 칼이 허리춤에 있음
                sword_x = self.x + self.width - 5 if self.facing_right else self.x - 15
                pygame.draw.rect(screen, YELLOW, (sword_x, self.y + 20, 20, 5))


class Platform:
    def __init__(self, x, y, width, height, disappearing=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.disappearing = disappearing
        self.timer = 0
        self.visible = True
        
    def update(self, player):
        if self.disappearing and self.visible:
            if (player.x < self.x + self.width and
                player.x + player.width > self.x and
                player.y + player.height >= self.y and
                player.y + player.height <= self.y + 10):
                self.timer += 1
                if self.timer > 60:
                    self.visible = False
            else:
                # 플레이어가 플랫폼을 벗어나면 타이머 리셋
                self.timer = 0
        elif not self.visible:
            self.timer += 1
            if self.timer > 180:
                self.visible = True
                self.timer = 0
                
    def draw(self, screen):
        if self.visible:
            color = ORANGE if self.disappearing else GREEN
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))


class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 35
        self.type = enemy_type
        self.health = 1
        self.velocity_x = 2 if enemy_type == "skeleton" else 0
        self.velocity_y = 0
        self.direction = 1
        self.jump_timer = 0
        self.attack_timer = 0
        self.alive = True
        self.on_ground = False
        
    def update(self, platforms, player):
        if not self.alive:
            return

        if self.type == "skeleton":
            # 중력 적용
            self.velocity_y += 0.5
            self.y += self.velocity_y

            # 바닥 충돌 체크
            self.on_ground = False
            for platform in platforms:
                if (self.x < platform.x + platform.width and
                    self.x + self.width > platform.x and
                    self.y < platform.y + platform.height and
                    self.y + self.height > platform.y and
                    self.velocity_y > 0):
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True

            # 플랫폼 끝에 도달하면 방향 전환
            next_x = self.x + self.velocity_x * self.direction
            at_edge = True

            for platform in platforms:
                if (next_x + 5 < platform.x + platform.width and
                    next_x + self.width - 5 > platform.x and
                    self.y + self.height >= platform.y and
                    self.y + self.height <= platform.y + 20):
                    at_edge = False
                    break

            if at_edge and self.on_ground:
                self.direction *= -1

            self.x += self.velocity_x * self.direction
                        
        elif self.type == "slime":
            self.jump_timer += 1
            if self.jump_timer > 60:
                self.velocity_y = -random.randint(8, 12)
                self.velocity_x = random.randint(-3, 3)
                self.jump_timer = 0
            
            self.y += self.velocity_y
            self.x += self.velocity_x
            self.velocity_y += 0.5
            
            for platform in platforms:
                if (self.x < platform.x + platform.width and
                    self.x + self.width > platform.x and
                    self.y < platform.y + platform.height and
                    self.y + self.height > platform.y and
                    self.velocity_y > 0):
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    
        elif self.type == "mage":
            self.attack_timer += 1
            
    def draw(self, screen):
        if not self.alive:
            return
        if self.type == "skeleton":
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, WHITE, (int(self.x + 15), int(self.y + 10)), 8)
        elif self.type == "slime":
            pygame.draw.circle(screen, GREEN, (int(self.x + 15), int(self.y + 20)), 15)
        elif self.type == "mage":
            pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, YELLOW, (self.x + 10, self.y - 10, 10, 10))


class Projectile:
    def __init__(self, x, y, direction, proj_type="magic", from_player=False):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 10
        # 플레이어 투사체는 더 빠르게
        if from_player:
            self.velocity_x = direction * 12
        else:
            self.velocity_x = direction * 5
        self.type = proj_type
        self.active = True
        self.from_player = from_player
        self.timer = 0

    def update(self):
        self.x += self.velocity_x
        self.timer += 1
        if self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False

    def draw(self, screen):
        if self.active:
            if self.type == "player_energy":
                # 플레이어 에너지탄
                pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), 8)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 5)
                # 꼬리 이펙트
                for i in range(3):
                    offset = i * 8
                    tail_x = self.x - offset if self.velocity_x > 0 else self.x + offset
                    pygame.draw.circle(screen, BLUE, (int(tail_x), int(self.y)), 4 - i, 1)
            elif self.type == "magic":
                pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), 5)
            else:
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 5)


class Trap:
    def __init__(self, x, y, trap_type):
        self.x = x
        self.y = y
        self.type = trap_type
        self.width = 40
        self.height = 40
        self.timer = 0
        self.active = True
        self.falling = False
        self.original_x = x
        self.original_y = y
        
    def update(self, player):
        if self.type == "blade":
            self.timer += 1
            self.x = self.original_x + math.sin(self.timer * 0.05) * 100
            
        elif self.type == "spike":
            if not self.falling and abs(player.x - self.x) < 50 and player.y > self.y:
                self.falling = True
            if self.falling:
                self.y += 8
                if self.y > SCREEN_HEIGHT:
                    self.active = False
                    
        elif self.type == "fireball":
            self.timer += 1
            if self.timer > 120:
                self.timer = 0
                return True
        return False
        
    def draw(self, screen):
        if not self.active:
            return
        if self.type == "blade":
            pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), 20)
            pygame.draw.line(screen, RED, (self.x - 15, self.y), (self.x + 15, self.y), 3)
        elif self.type == "spike":
            points = [(self.x, self.y - 20), (self.x - 15, self.y + 20), (self.x + 15, self.y + 20)]
            pygame.draw.polygon(screen, RED, points)
        elif self.type == "fireball":
            color = ORANGE if self.timer % 40 < 20 else RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 15)


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = item_type
        self.collected = False
        
    def draw(self, screen):
        if not self.collected:
            if self.type == "health":
                pygame.draw.circle(screen, RED, (int(self.x + 15), int(self.y + 15)), 12)
                pygame.draw.rect(screen, WHITE, (self.x + 12, self.y + 10, 6, 10))
                pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 12, 10, 6))
            elif self.type == "max_health":
                pygame.draw.circle(screen, PURPLE, (int(self.x + 15), int(self.y + 15)), 12)
                pygame.draw.rect(screen, WHITE, (self.x + 12, self.y + 10, 6, 10))
                pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 12, 10, 6))
            elif self.type == "speed":
                pygame.draw.circle(screen, BLUE, (int(self.x + 15), int(self.y + 15)), 12)
                pygame.draw.polygon(screen, WHITE, [(self.x + 20, self.y + 15), (self.x + 10, self.y + 10), (self.x + 10, self.y + 20)])
            elif self.type == "sword":
                pygame.draw.rect(screen, YELLOW, (self.x + 5, self.y + 10, 20, 5))
                pygame.draw.rect(screen, GRAY, (self.x + 20, self.y + 7, 5, 11))


class Chest:
    def __init__(self, x, y, item):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 35
        self.item = item
        self.opened = False
        
    def draw(self, screen):
        color = GRAY if self.opened else ORANGE
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, YELLOW, (self.x + 15, self.y + 15, 10, 8))


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 60
        self.max_health = 100
        self.health = 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.pattern = None
        self.pattern_timer = 0
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.attack_cooldown = 0
        self.stunned = False
        self.stun_timer = 0
        self.facing_right = True
        
    def update(self, player, platforms):
        self.velocity_y += 0.8
        self.y += self.velocity_y
        self.x += self.velocity_x

        # 보스가 화면 밖으로 나가지 않도록 제한
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
            self.stunned = True
            self.stun_timer = 30
            self.vulnerable = True
            self.vulnerable_timer = 60
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.velocity_x = 0
            self.stunned = True
            self.stun_timer = 30
            self.vulnerable = True
            self.vulnerable_timer = 60

        self.on_ground = False
        for platform in platforms:
            if (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y):
                if self.velocity_y > 0:
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                if abs(self.velocity_x) > 5:
                    self.velocity_x = 0
                    self.stunned = True
                    self.stun_timer = 30
                    self.vulnerable = True
                    self.vulnerable_timer = 60
                    
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
            return None
            
        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.vulnerable = False
                
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.health <= 10:
            if self.attack_cooldown <= 0:
                self.vulnerable = True
                self.choose_random_pattern(player)
                self.attack_cooldown = 30
        elif self.pattern is None and self.attack_cooldown <= 0:
            self.choose_random_pattern(player)
            
        return self.execute_pattern(player)
        
    def choose_random_pattern(self, player):
        patterns = ["jump", "flame", "charge", "slash"]
        self.pattern = random.choice(patterns)
        self.pattern_timer = 0
        self.facing_right = player.x > self.x
        
    def execute_pattern(self, player):
        if self.pattern == "jump":
            if self.pattern_timer == 0 and self.on_ground:
                self.velocity_y = -18
                self.pattern_timer = 1
            elif self.on_ground and self.pattern_timer > 0:
                self.pattern = None
                self.vulnerable = True
                self.vulnerable_timer = 90
                self.attack_cooldown = 120
                return ("shockwave", None)
                
        elif self.pattern == "charge":
            if self.pattern_timer == 0:
                self.velocity_x = 12 if self.facing_right else -12
                self.pattern_timer = 1
                
        elif self.pattern == "flame":
            self.pattern_timer += 1
            if self.pattern_timer == 30:
                direction = 1 if self.facing_right else -1
                return ("flame", direction)
            elif self.pattern_timer > 60:
                self.pattern = None
                self.vulnerable = True
                self.vulnerable_timer = 60
                self.attack_cooldown = 100
                
        elif self.pattern == "slash":
            self.pattern_timer += 1
            if self.pattern_timer > 60:
                self.pattern = None
                self.vulnerable = True
                self.vulnerable_timer = 60
                self.attack_cooldown = 100
        return (None, None)
        
    def take_damage(self, amount):
        if self.health > 0:
            self.health = max(0, self.health - amount)
            return True
        return False
        
    def draw(self, screen):
        color = DARK_RED if not self.stunned else GRAY
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x + 15, self.y + 10, 20, 20))
        
        if self.pattern == "slash":
            sword_x = self.x + self.width if self.facing_right else self.x - 30
            pygame.draw.rect(screen, RED, (sword_x, self.y + 20, 30, 8))
            
        bar_width = 100
        bar_height = 10
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        pygame.draw.rect(screen, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))


class Game:
    def __init__(self):
        self.player = Player(100, 500)
        self.stage = 1
        self.enemies = []
        self.platforms = []
        self.traps = []
        self.projectiles = []
        self.items = []
        self.chests = []
        self.boss = None
        self.deaths = 0
        self.start_time = time.time()
        self.stage_start_time = time.time()
        self.items_collected = 0
        self.game_over = False
        self.victory = False
        self.in_menu = True  # 메뉴 상태 추가
        self.menu_selection = 0  # 0: Start Game, 1: Quit

    def start_game(self):
        """메뉴에서 게임을 시작할 때 호출"""
        self.in_menu = False
        self.start_time = time.time()
        self.load_stage(1)
        
    def load_stage(self, stage_num):
        self.stage = stage_num
        self.enemies = []
        self.platforms = []
        self.traps = []
        self.projectiles = []
        self.items = []
        self.chests = []
        self.boss = None
        self.stage_start_time = time.time()
        
        if stage_num == 1:
            self.player.x = 100
            self.player.y = 500
            self.platforms = [
                Platform(0, 650, SCREEN_WIDTH, 50),  # 바닥
                Platform(200, 550, 150, 20),  # 첫 번째 발판
                Platform(420, 470, 130, 20),  # 두 번째 발판 (간격 좁힘)
                Platform(620, 390, 130, 20),  # 세 번째 발판 (간격 좁힘)
                Platform(400, 310, 150, 20),  # 네 번째 발판
                Platform(150, 230, 150, 20),  # 다섯 번째 발판
                Platform(450, 150, 150, 20),  # 여섯 번째 발판
                Platform(750, 150, 200, 20),  # 출구 발판
            ]
            self.enemies = [
                Enemy(250, 500, "skeleton"),
                Enemy(500, 400, "slime"),
            ]
            self.chests = [
                Chest(470, 430, Item(470, 430, "health")),
                Chest(250, 510, Item(250, 510, "speed")),
            ]
            
        elif stage_num == 2:
            self.player.x = 50
            self.player.y = 500
            self.platforms = [
                Platform(0, 650, 250, 50),  # 시작 바닥 (넓게)
                Platform(280, 580, 120, 20),  # 첫 번째 발판
                Platform(450, 500, 120, 20, disappearing=True),  # 사라지는 발판 1
                Platform(620, 420, 120, 20),  # 중간 발판
                Platform(480, 340, 120, 20),  # 왼쪽으로 이동
                Platform(280, 260, 120, 20, disappearing=True),  # 사라지는 발판 2
                Platform(100, 180, 150, 20),  # 왼쪽 상단
                Platform(320, 120, 150, 20),  # 중앙 상단
                Platform(550, 80, 150, 20),  # 오른쪽 중앙
                Platform(780, 50, 200, 20),  # 출구 발판
            ]
            self.enemies = [
                Enemy(300, 530, "skeleton"),
                Enemy(640, 370, "slime"),
                Enemy(130, 130, "mage"),
            ]
            self.traps = [
                Trap(550, 360, "blade"),  # 칼날 함정
                Trap(250, 200, "spike"),  # 낙하 가시
                Trap(400, 80, "spike"),  # 낙하 가시
                Trap(480, 280, "fireball"),  # 화염구
            ]
            self.chests = [
                Chest(820, 10, Item(820, 10, "sword")),  # 칼 (오른쪽 끝)
                Chest(140, 140, Item(140, 140, "max_health")),  # 최대 체력 증가
            ]
            
        elif stage_num == 3:
            self.player.x = 100
            self.player.y = 500
            # 보스 스테이지에서는 칼을 기본으로 제공
            self.player.has_sword = True
            self.platforms = [
                Platform(0, 650, SCREEN_WIDTH, 50),  # 바닥
                Platform(200, 550, 600, 30),  # 중앙 메인 발판 (50픽셀 내림)
                Platform(50, 450, 130, 20),  # 왼쪽 회피 발판 (50픽셀 내림)
                Platform(820, 450, 130, 20),  # 오른쪽 회피 발판 (50픽셀 내림)
                Platform(100, 350, 150, 20),  # 왼쪽 중간 발판 (50픽셀 내림)
                Platform(425, 350, 150, 20),  # 중앙 중간 발판 (50픽셀 내림)
                Platform(750, 350, 150, 20),  # 오른쪽 중간 발판 (50픽셀 내림)
                Platform(250, 250, 150, 20),  # 왼쪽 상단 발판 (50픽셀 내림)
                Platform(550, 250, 150, 20),  # 오른쪽 상단 발판 (50픽셀 내림)
            ]
            self.boss = Boss(SCREEN_WIDTH // 2 - 25, 480)
            
    def restart_stage(self):
        self.deaths += 1
        self.player.hearts = self.player.max_hearts
        self.player.invincible_time = 60
        self.load_stage(self.stage)

    def melee_attack(self):
        """플레이어의 근접 칼 공격 처리 (Z키)"""
        if not self.player.has_sword or self.player.attack_cooldown > 0:
            return

        # 공격 애니메이션 시작
        self.player.attacking = True
        self.player.attack_animation_timer = 15
        self.player.attack_cooldown = 30

        attack_range = 60  # 공격 범위 증가
        attack_x = self.player.x + self.player.width if self.player.facing_right else self.player.x - attack_range

        # 일반 적 공격
        for enemy in self.enemies:
            if enemy.alive:
                if (enemy.x < attack_x + attack_range and
                    enemy.x + enemy.width > attack_x and
                    abs(self.player.y - enemy.y) < 80):  # 수직 범위도 증가
                    enemy.alive = False

        # 보스 공격
        if self.boss:
            # 충돌 박스 확인
            boss_left = self.boss.x
            boss_right = self.boss.x + self.boss.width
            attack_left = attack_x
            attack_right = attack_x + attack_range
            y_diff = abs(self.player.y - self.boss.y)

            # 디버그 출력
            print(f"[MELEE] Boss: {boss_left}-{boss_right}, Attack: {attack_left}-{attack_right}, Y_diff: {y_diff}")

            if (boss_left < attack_right and
                boss_right > attack_left and
                y_diff < 80):  # 수직 범위도 증가
                print(f"[MELEE] HIT! Boss HP: {self.boss.health} -> {self.boss.health - 1}")
                if self.boss.take_damage(1):
                    if self.boss.health <= 0:
                        self.victory = True

    def ranged_attack(self):
        """플레이어의 원거리 에너지탄 공격 (D키)"""
        if self.player.ranged_attack_cooldown > 0:
            return

        # 쿨다운 설정
        self.player.ranged_attack_cooldown = 45  # 0.75초

        # 에너지탄 발사
        direction = 1 if self.player.facing_right else -1
        projectile_x = self.player.x + self.player.width if self.player.facing_right else self.player.x
        projectile_y = self.player.y + 15
        self.projectiles.append(Projectile(projectile_x, projectile_y, direction, "player_energy", from_player=True))
        
    def update(self, keys):
        if self.game_over or self.victory:
            return
            
        self.player.update(keys, self.platforms)
        
        for platform in self.platforms:
            if platform.disappearing:
                platform.update(self.player)
                
        for enemy in self.enemies:
            enemy.update(self.platforms, self.player)
            if enemy.alive and not (self.player.invincible_time > 0):
                if (self.player.x < enemy.x + enemy.width and
                    self.player.x + self.player.width > enemy.x and
                    self.player.y < enemy.y + enemy.height and
                    self.player.y + self.player.height > enemy.y):
                    self.player.take_damage()
                    
            if enemy.type == "mage" and enemy.attack_timer > 120:
                direction = 1 if self.player.x > enemy.x else -1
                self.projectiles.append(Projectile(enemy.x + 15, enemy.y + 15, direction, "magic"))
                enemy.attack_timer = 0
                
        for projectile in self.projectiles:
            projectile.update()

            # 플레이어 투사체가 적에게 명중
            if projectile.from_player and projectile.active:
                # 일반 적 공격
                for enemy in self.enemies:
                    if enemy.alive:
                        if (enemy.x < projectile.x + projectile.width and
                            enemy.x + enemy.width > projectile.x and
                            enemy.y < projectile.y + projectile.height and
                            enemy.y + enemy.height > projectile.y):
                            enemy.alive = False
                            projectile.active = False
                            break

                # 보스 공격
                if self.boss and projectile.active:
                    if (self.boss.x < projectile.x + projectile.width and
                        self.boss.x + self.boss.width > projectile.x and
                        self.boss.y < projectile.y + projectile.height and
                        self.boss.y + self.boss.height > projectile.y):
                        if self.boss.take_damage(1):
                            if self.boss.health <= 0:
                                self.victory = True
                        projectile.active = False

            # 적 투사체가 플레이어에게 명중
            elif not projectile.from_player and projectile.active and not (self.player.invincible_time > 0):
                if (self.player.x < projectile.x + projectile.width and
                    self.player.x + self.player.width > projectile.x and
                    self.player.y < projectile.y + projectile.height and
                    self.player.y + self.player.height > projectile.y):
                    self.player.take_damage()
                    projectile.active = False

        self.projectiles = [p for p in self.projectiles if p.active]
        
        for trap in self.traps:
            if trap.update(self.player):
                direction = 1 if self.player.x > trap.x else -1
                self.projectiles.append(Projectile(trap.x, trap.y, direction, "fireball"))
                
            if trap.active and self.player.invincible_time <= 0:
                if (self.player.x < trap.x + trap.width and
                    self.player.x + self.player.width > trap.x and
                    self.player.y < trap.y + trap.height and
                    self.player.y + self.player.height > trap.y):
                    if trap.type == "blade":
                        self.player.hearts = 0
                    else:
                        self.player.take_damage()
                        
        for chest in self.chests:
            if not chest.opened:
                if (self.player.x < chest.x + chest.width and
                    self.player.x + self.player.width > chest.x and
                    self.player.y < chest.y + chest.height and
                    self.player.y + self.player.height > chest.y):
                    chest.opened = True
                    if chest.item.type == "health":
                        self.player.heal()
                    elif chest.item.type == "max_health":
                        self.player.max_hearts += 1
                        self.player.hearts = self.player.max_hearts
                    elif chest.item.type == "speed":
                        self.player.speed_boost = 3
                    elif chest.item.type == "sword":
                        self.player.has_sword = True
                    self.items_collected += 1
                    
        if self.boss:
            boss_action = self.boss.update(self.player, self.platforms)
            
            if boss_action:
                action_type, action_data = boss_action
                if action_type == "shockwave":
                    if self.player.on_ground and abs(self.player.x - self.boss.x) < 200:
                        if self.player.invincible_time <= 0:
                            self.player.take_damage()
                elif action_type == "flame":
                    self.projectiles.append(Projectile(self.boss.x + 25, self.boss.y + 30, action_data, "fireball"))
                    
            if self.boss.pattern == "slash":
                sword_range = 50
                sword_x = self.boss.x + self.boss.width if self.boss.facing_right else self.boss.x - sword_range
                if (self.player.x < sword_x + sword_range and
                    self.player.x + self.player.width > sword_x and
                    abs(self.player.y - self.boss.y) < 60):
                    if self.player.invincible_time <= 0:
                        self.player.take_damage()
                        
            if self.player.invincible_time <= 0:
                if (self.player.x < self.boss.x + self.boss.width and
                    self.player.x + self.player.width > self.boss.x and
                    self.player.y < self.boss.y + self.boss.height and
                    self.player.y + self.player.height > self.boss.y):
                    self.player.take_damage()
                    
                            
        if self.player.hearts <= 0:
            self.restart_stage()
            
        if self.player.y > SCREEN_HEIGHT:
            self.restart_stage()
            
        if self.stage < 3 and self.player.x > SCREEN_WIDTH - 50:
            self.load_stage(self.stage + 1)
            
    def draw_menu(self, screen):
        """메뉴 화면 그리기"""
        screen.fill(BLACK)

        # 게임 제목
        font_title = pygame.font.Font(None, 100)
        title_text = font_title.render("TOWER OF HERO", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        # 부제목
        font_subtitle = pygame.font.Font(None, 50)
        subtitle_text = font_subtitle.render("Princess Rescue Mission", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle_text, subtitle_rect)

        # 메뉴 옵션
        font_menu = pygame.font.Font(None, 60)
        menu_options = ["Start Game", "Quit"]

        for i, option in enumerate(menu_options):
            color = YELLOW if i == self.menu_selection else WHITE
            text = font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 80))
            screen.blit(text, text_rect)

            # 선택된 항목에 화살표 표시
            if i == self.menu_selection:
                arrow_left = font_menu.render(">", True, YELLOW)
                arrow_right = font_menu.render("<", True, YELLOW)
                screen.blit(arrow_left, (text_rect.left - 50, text_rect.top))
                screen.blit(arrow_right, (text_rect.right + 30, text_rect.top))

        # 조작법 안내
        font_small = pygame.font.Font(None, 30)
        controls = [
            "Controls:",
            "Arrow Keys / WASD - Move & Jump",
            "F - Dash",
            "Z - Melee Attack (Sword)",
            "D - Energy Ball Attack"
        ]

        for i, text in enumerate(controls):
            control_text = font_small.render(text, True, GRAY if i == 0 else WHITE)
            screen.blit(control_text, (50, 520 + i * 30))

    def draw(self, screen):
        screen.fill(BLACK)

        for platform in self.platforms:
            platform.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for projectile in self.projectiles:
            projectile.draw(screen)

        for trap in self.traps:
            trap.draw(screen)

        for chest in self.chests:
            chest.draw(screen)
            if chest.opened and not chest.item.collected:
                chest.item.draw(screen)

        if self.boss:
            self.boss.draw(screen)

        self.player.draw(screen)
        
        for i in range(self.player.max_hearts):
            x = 10 + i * 35
            y = 10
            if i < self.player.hearts:
                pygame.draw.circle(screen, RED, (x + 12, y + 12), 10)
                pygame.draw.rect(screen, RED, (x + 8, y + 8, 8, 16))
                pygame.draw.rect(screen, RED, (x + 16, y + 8, 8, 16))
            else:
                pygame.draw.circle(screen, GRAY, (x + 12, y + 12), 10, 2)
                
        font = pygame.font.Font(None, 30)
        stage_text = font.render(f"Stage {self.stage}", True, WHITE)
        screen.blit(stage_text, (SCREEN_WIDTH - 120, 10))
        
        deaths_text = font.render(f"Deaths: {self.deaths}", True, WHITE)
        screen.blit(deaths_text, (SCREEN_WIDTH - 150, 40))
        
        elapsed_time = int(time.time() - self.start_time)
        time_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 70))
        
        score = max(0, 10000 - self.deaths * 100 - elapsed_time * 10 + self.items_collected * 500)
        score_text = font.render(f"Score: {score}", True, YELLOW)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 100))
        
        # 대시 쿨다운 표시
        if self.player.dash_cooldown > 0:
            dash_text = font.render(f"Dash(F): {self.player.dash_cooldown // 60 + 1}s", True, YELLOW)
            screen.blit(dash_text, (10, 50))
        else:
            dash_text = font.render("Dash(F): Ready!", True, GREEN)
            screen.blit(dash_text, (10, 50))

        # 원거리 공격 쿨다운 표시
        if self.player.ranged_attack_cooldown > 0:
            ranged_text = font.render(f"Energy(D): {(self.player.ranged_attack_cooldown / 60):.1f}s", True, YELLOW)
            screen.blit(ranged_text, (10, 80))
        else:
            ranged_text = font.render("Energy(D): Ready!", True, GREEN)
            screen.blit(ranged_text, (10, 80))

        # 근접 공격 쿨다운 표시
        if self.player.has_sword:
            if self.player.attack_cooldown > 0:
                melee_text = font.render(f"Sword(Z): {(self.player.attack_cooldown / 60):.1f}s", True, YELLOW)
                screen.blit(melee_text, (10, 110))
            else:
                melee_text = font.render("Sword(Z): Ready!", True, GREEN)
                screen.blit(melee_text, (10, 110))
            
        if self.victory:
            font_large = pygame.font.Font(None, 80)
            victory_text = font_large.render("VICTORY!", True, YELLOW)
            screen.blit(victory_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
            
            font_medium = pygame.font.Font(None, 40)
            final_time = int(time.time() - self.start_time)
            stats_text = [
                f"Total Deaths: {self.deaths}",
                f"Clear Time: {final_time}s",
                f"Items Collected: {self.items_collected}",
                "",
                "Press R to Restart"
            ]
            for i, text in enumerate(stats_text):
                stat_surface = font_medium.render(text, True, WHITE)
                screen.blit(stat_surface, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + i * 40))


def main():
    game = Game()
    running = True

    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # 메뉴 화면에서의 키 입력
                if game.in_menu:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        game.menu_selection = (game.menu_selection - 1) % 2
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        game.menu_selection = (game.menu_selection + 1) % 2
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if game.menu_selection == 0:  # Start Game
                            game.start_game()
                        elif game.menu_selection == 1:  # Quit
                            running = False
                # 게임 플레이 중 키 입력
                else:
                    if event.key == pygame.K_r and game.victory:
                        game = Game()
                    elif event.key == pygame.K_f and game.player.dash_cooldown <= 0:
                        game.player.dash_direction = 1 if game.player.facing_right else -1
                        game.player.dash_duration = 10
                        game.player.dash_cooldown = 120
                        game.player.invincible_time = 12
                    elif event.key == pygame.K_z:
                        game.melee_attack()
                    elif event.key == pygame.K_d:
                        game.ranged_attack()

        # 메뉴 화면이 아닐 때만 게임 업데이트
        if not game.in_menu:
            game.update(keys)
            game.draw(screen)
        else:
            game.draw_menu(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
