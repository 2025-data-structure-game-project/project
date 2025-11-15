import pygame
import time
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from entities.player import Player
from entities.boss import Boss
from entities.projectile import Projectile, Fire
from systems.stage_manager import StageManager
from systems.ui_manager import UIManager
from utils import (
    check_rect_collision,
    get_attack_box,
    get_entity_box,
    check_collision,
    create_particle_burst,
    update_particles,
    draw_particles,
    shake_screen,
)


class Game:
    def __init__(self):
        # 플레이어
        self.player = Player(100, 500)

        # 매니저
        self.stage_manager = StageManager()
        self.ui_manager = UIManager()

        # 보스
        self.boss = None

        # 투사체 및 효과
        self.projectiles = []
        self.fires = []  # 바닥 불길
        self.particles = []

        # 게임 상태
        self.game_state = GAME_STATE_MENU
        self.deaths = 0
        self.start_time = time.time()
        self.stage_start_time = time.time()
        self.items_collected = 0
        self.victory_time = None  # 승리 시점의 시간 저장

        # 체크포인트 시스템
        self.checkpoint_stage = 1  # 마지막 체크포인트 스테이지
        self.stage_checkpoints = {1: False, 2: False, 3: False}  # 각 스테이지 체크포인트 도달 여부

        # 화면 효과
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 0

        # 보스전 특수 상태
        self.platform_collapse_triggered = False

        # 배경음악 초기화
        self.init_music()

        # 초기 스테이지 로드 (메뉴에서 시작하므로 로드 안함)

    def init_music(self):
        """배경음악 초기화"""
        try:
            pygame.mixer.music.load("Mixdown.mp3")
            pygame.mixer.music.set_volume(0.5)  # 볼륨 50%
        except pygame.error as e:
            print(f"배경음악 로드 실패: {e}")

    def play_music(self):
        """배경음악 재생 (무한 루프)"""
        try:
            pygame.mixer.music.play(-1)  # -1은 무한 루프
        except pygame.error as e:
            print(f"배경음악 재생 실패: {e}")

    def stop_music(self):
        """배경음악 정지"""
        pygame.mixer.music.stop()

    def start_game(self):
        self.game_state = GAME_STATE_PLAYING
        self.deaths = 0
        self.start_time = time.time()
        self.items_collected = 0
        self.checkpoint_stage = 1
        self.stage_checkpoints = {1: False, 2: False, 3: False}
        self.load_stage(1)

    def load_stage(self, stage_num):
        self.stage_start_time = time.time()
        self.stage_manager.load_stage(stage_num, self.player)

        # 스테이지 진입 시 체크포인트 활성화
        if stage_num not in self.stage_checkpoints or not self.stage_checkpoints[stage_num]:
            self.stage_checkpoints[stage_num] = True
            self.checkpoint_stage = stage_num

        # 배경음악 제어 (스테이지 1, 2에서만 재생)
        if stage_num in [1, 2]:
            if not pygame.mixer.music.get_busy():
                self.play_music()
        else:
            self.stop_music()

        # 보스 생성 (스테이지 3) - 항상 새로운 보스 생성하여 HP 초기화
        if stage_num == 3:
            # 기존 보스 제거
            self.boss = None
            # 새로운 보스 생성 (HP 완전 초기화)
            self.boss = Boss(SCREEN_WIDTH // 2 - 25, 480)
            self.platform_collapse_triggered = False
        else:
            self.boss = None

        # 투사체 및 효과 초기화
        self.projectiles = []
        self.fires = []
        self.particles = []

    def restart_stage(self):
        self.deaths += 1
        self.player.hearts = self.player.max_hearts
        self.player.invincible_time = 60
        # 마지막 체크포인트 스테이지에서 재시작
        self.load_stage(self.checkpoint_stage)

    def update(self, keys):
        if self.game_state != GAME_STATE_PLAYING:
            return

        # 플레이어 업데이트
        self.player.update(keys, self.stage_manager.platforms)
        
        # 원거리 공격 자동 발사 (X 키를 누르고 있으면)
        if keys[pygame.K_x]:
            self.ranged_attack()
        
        # 근접 공격 자동 발사 (Z 키를 누르고 있으면)
        if keys[pygame.K_z]:
            self.melee_attack()

        # 발판 업데이트
        self.stage_manager.update_platforms(self.player)

        # 적 업데이트
        for enemy in self.stage_manager.enemies:
            enemy.update(self.stage_manager.platforms, self.player)

            # 적과 플레이어 충돌
            if enemy.alive and self.player.invincible_time <= 0:
                if check_rect_collision(
                    self.player.x,
                    self.player.y,
                    self.player.width,
                    self.player.height,
                    enemy.x,
                    enemy.y,
                    enemy.width,
                    enemy.height,
                ):
                    self.player.take_damage()

            # 마법사 공격
            if enemy.type == "mage" and enemy.attack_timer > MAGE_ATTACK_INTERVAL:
                direction = 1 if self.player.x > enemy.x else -1
                self.projectiles.append(
                    Projectile(enemy.x + 15, enemy.y + 15, direction, "magic")
                )
                enemy.attack_timer = 0

        # 투사체 업데이트
        for projectile in self.projectiles[:]:
            projectile.update()

            if not projectile.active:
                self.projectiles.remove(projectile)
                continue

            # 플레이어 투사체
            if projectile.from_player:
                # 적 공격
                for enemy in self.stage_manager.enemies:
                    if enemy.alive and check_rect_collision(
                        projectile.x,
                        projectile.y,
                        projectile.width,
                        projectile.height,
                        enemy.x,
                        enemy.y,
                        enemy.width,
                        enemy.height,
                    ):
                        enemy.alive = False
                        projectile.active = False
                        self.particles.extend(
                            create_particle_burst(
                                enemy.x + enemy.width // 2,
                                enemy.y + enemy.height // 2,
                                15,
                                [YELLOW, ORANGE, WHITE],
                            )
                        )
                        break

                # 보스 공격
                if self.boss and check_rect_collision(
                    projectile.x,
                    projectile.y,
                    projectile.width,
                    projectile.height,
                    self.boss.x,
                    self.boss.y,
                    self.boss.width,
                    self.boss.height,
                ):
                    if self.boss.take_damage(5):  # 원거리 공격 데미지 5배
                        projectile.active = False
                        self.particles.extend(
                            create_particle_burst(
                                self.boss.x + self.boss.width // 2,
                                self.boss.y + self.boss.height // 2,
                                10,
                                [RED, ORANGE, YELLOW],
                            )
                        )
                        if self.boss.health <= 0:
                            self.victory_time = time.time()
                            self.game_state = GAME_STATE_VICTORY
                    else:
                        # 막힘
                        projectile.active = False
                        self.particles.extend(
                            create_particle_burst(
                                projectile.x, projectile.y, 5, [WHITE, LIGHT_BLUE]
                            )
                        )

            # 적 투사체
            else:
                if self.player.invincible_time <= 0 and check_rect_collision(
                    projectile.x,
                    projectile.y,
                    projectile.width,
                    projectile.height,
                    self.player.x,
                    self.player.y,
                    self.player.width,
                    self.player.height,
                ):
                    self.player.take_damage()
                    projectile.active = False

            # 화염구가 발판에 닿으면 불길 생성
            if projectile.type == "fireball" and projectile.active:
                platform, fire_x, fire_y = projectile.check_platform_collision(
                    self.stage_manager.platforms
                )
                if platform:
                    projectile.active = False
                    self.fires.append(Fire(fire_x, fire_y, platform.width))
                    self.start_screen_shake(5)

        # 불길 업데이트
        for fire in self.fires[:]:
            fire.update()
            if not fire.active:
                self.fires.remove(fire)
                continue

            # 플레이어가 불길 위에 있으면 피해
            if self.player.invincible_time <= 0 and check_rect_collision(
                self.player.x,
                self.player.y,
                self.player.width,
                self.player.height,
                fire.x,
                fire.y - fire.height,
                fire.width,
                fire.height,
            ):
                if fire.can_damage():
                    self.player.take_damage()

        # 함정 업데이트
        for trap in self.stage_manager.traps:
            fire_signal = trap.update(self.player)
            if fire_signal:
                direction = 1 if self.player.x > trap.x else -1
                self.projectiles.append(
                    Projectile(trap.x, trap.y, direction, "fireball")
                )

            # 함정 충돌
            if trap.active and self.player.invincible_time <= 0:
                if check_rect_collision(
                    self.player.x,
                    self.player.y,
                    self.player.width,
                    self.player.height,
                    trap.x,
                    trap.y,
                    trap.width,
                    trap.height,
                ):
                    if trap.type == "blade":
                        self.player.hearts = 0  # 즉사
                    else:
                        self.player.take_damage()

        # 상자 업데이트
        for chest in self.stage_manager.chests:
            if not chest.opened:
                if check_rect_collision(
                    self.player.x,
                    self.player.y,
                    self.player.width,
                    self.player.height,
                    chest.x,
                    chest.y,
                    chest.width,
                    chest.height,
                ):
                    chest.opened = True
                    self.collect_item(chest.item)
        
        # 체크포인트 업데이트
        for checkpoint in self.stage_manager.checkpoints:
            if checkpoint.check_activation(self.player):
                # 체크포인트 활성화 시 파티클 효과
                self.particles.extend(
                    create_particle_burst(
                        checkpoint.x + checkpoint.width // 2,
                        checkpoint.y + checkpoint.height // 2,
                        20,
                        [GREEN, YELLOW, WHITE]
                    )
                )

        # 보스 업데이트
        if self.boss:
            pattern, actions = self.boss.update(
                self.player, self.stage_manager.platforms, self.projectiles
            )

            # 보스 액션 처리
            if actions:
                for action in actions:
                    self.handle_boss_action(action)

            # 보스 접촉 피해
            if self.player.invincible_time <= 0 and check_rect_collision(
                self.player.x,
                self.player.y,
                self.player.width,
                self.player.height,
                self.boss.x,
                self.boss.y,
                self.boss.width,
                self.boss.height,
            ):
                self.player.take_damage()

            # 지면 붕괴 트리거 (HP 50% 이하)
            if (
                not self.platform_collapse_triggered
                and self.boss.health <= PLATFORM_COLLAPSE_HP_THRESHOLD
            ):
                self.trigger_platform_collapse()

            # 보스 사망
            if self.boss.health <= 0:
                self.victory_time = time.time()
                self.game_state = GAME_STATE_VICTORY

        # 파티클 업데이트
        update_particles(self.particles)

        # 화면 흔들림 업데이트
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1

        # 플레이어 사망
        if self.player.hearts <= 0 or self.player.y > SCREEN_HEIGHT:
            self.restart_stage()

        # 스테이지 클리어
        if self.stage_manager.is_at_exit(self.player):
            next_stage = self.stage_manager.get_next_stage()
            if next_stage:
                self.load_stage(next_stage)

    def handle_boss_action(self, action):
        action_type, data = action

        if action_type == "shockwave":
            # 충격파 생성
            if self.player.on_ground and abs(self.player.x - data["x"]) < 200:
                if self.player.invincible_time <= 0:
                    self.player.take_damage()

            # 충격파 파티클
            for i in range(3):
                delay = i * 10
                radius = 100 + i * 100
                # 간단한 파티클로 대체
                self.particles.extend(
                    create_particle_burst(data["x"], data["y"], 20, [YELLOW, ORANGE])
                )

            self.start_screen_shake(10)

        elif action_type == "flame":
            # 화염구 발사
            direction = data["direction"]
            angle = data.get("angle", 0)
            self.projectiles.append(
                Projectile(
                    self.boss.x + 25,
                    self.boss.y + 30,
                    direction,
                    "fireball",
                    angle=angle,
                )
            )

        elif action_type == "slash":
            # 검 휘두르기
            direction = data["direction"]
            slash_range = 80
            slash_x = (
                self.boss.x + self.boss.width
                if direction > 0
                else self.boss.x - slash_range
            )

            # 근접 공격 판정
            if check_rect_collision(
                slash_x,
                self.boss.y,
                slash_range,
                self.boss.height,
                self.player.x,
                self.player.y,
                self.player.width,
                self.player.height,
            ):
                if self.player.invincible_time <= 0:
                    self.player.take_damage()

            # 검기 발사 (3번째 베기)
            if data.get("num", 0) == 2:
                self.projectiles.append(
                    Projectile(
                        self.boss.x + 25,
                        self.boss.y + 30,
                        direction,
                        "sword_beam",
                        from_player=False,
                    )
                )

        elif action_type == "teleport":
            # 텔레포트 이펙트
            self.particles.extend(
                create_particle_burst(
                    self.boss.x + self.boss.width // 2,
                    self.boss.y + self.boss.height // 2,
                    30,
                    [PURPLE, PINK, CYAN],
                )
            )

    def melee_attack(self):
        if not self.player.start_attack():
            return

        # 공격 히트박스 생성
        attack_box = get_attack_box(
            self.player.x,
            self.player.y,
            self.player.width,
            self.player.height,
            self.player.facing_right,
            PLAYER_ATTACK_RANGE,
        )

        # 적 공격
        for enemy in self.stage_manager.enemies:
            if enemy.alive:
                enemy_box = get_entity_box(enemy.x, enemy.y, enemy.width, enemy.height)
                if check_collision(attack_box, enemy_box):
                    enemy.alive = False
                    self.particles.extend(
                        create_particle_burst(
                            enemy.x + enemy.width // 2,
                            enemy.y + enemy.height // 2,
                            15,
                            [YELLOW, WHITE],
                        )
                    )

        # 보스 공격
        if self.boss:
            boss_box = get_entity_box(
                self.boss.x, self.boss.y, self.boss.width, self.boss.height
            )
            if check_collision(attack_box, boss_box):
                if self.boss.take_damage(1):
                    # 공격 성공
                    self.particles.extend(
                        create_particle_burst(
                            self.boss.x + self.boss.width // 2,
                            self.boss.y + self.boss.height // 2,
                            15,
                            [RED, ORANGE, YELLOW],
                        )
                    )
                    self.start_screen_shake(5)

                    if self.boss.health <= 0:
                        self.victory_time = time.time()
                        self.game_state = GAME_STATE_VICTORY
                else:
                    # 막힘!
                    self.particles.extend(
                        create_particle_burst(
                            self.boss.x + self.boss.width // 2,
                            self.boss.y + self.boss.height // 2,
                            10,
                            [WHITE, LIGHT_BLUE, PURPLE],
                        )
                    )

    def ranged_attack(self):
        if not self.player.start_ranged_attack():
            return

        direction = 1 if self.player.facing_right else -1
        projectile_x = (
            self.player.x + self.player.width
            if self.player.facing_right
            else self.player.x
        )
        projectile_y = self.player.y + 15

        self.projectiles.append(
            Projectile(
                projectile_x, projectile_y, direction, "player_energy", from_player=True
            )
        )

    def collect_item(self, item):
        if item.type == "health":
            self.player.heal()
        elif item.type == "max_health":
            self.player.max_hearts += 1
            self.player.hearts = self.player.max_hearts
        elif item.type == "speed":
            self.player.speed_boost = 3
        elif item.type == "sword":
            self.player.has_sword = True

        self.items_collected += 1

        # 아이템 획득 파티클
        self.particles.extend(
            create_particle_burst(
                item.x + item.width // 2, item.y + item.height // 2, 20, [GOLD, YELLOW]
            )
        )

    def trigger_platform_collapse(self):
        self.platform_collapse_triggered = True
        collapsed = self.stage_manager.collapse_platforms()

        if collapsed:
            # 화면 흔들림
            self.start_screen_shake(30)

    def start_screen_shake(self, duration, intensity=SCREEN_SHAKE_INTENSITY):
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity

    def get_shake_offset(self):
        if self.screen_shake_timer > 0:
            return shake_screen(self.screen_shake_intensity)
        return (0, 0)

    def draw_game_screen(self, screen):
        """게임 화면 그리기 (개발 메뉴와 공유)"""
        # 배경
        screen.fill(BLACK)

        # 화면 흔들림
        shake_offset = self.get_shake_offset()

        # 발판
        for platform in self.stage_manager.platforms:
            platform.draw(screen, shake_offset)

        # 함정
        for trap in self.stage_manager.traps:
            trap.draw(screen, shake_offset)
        
        # 체크포인트
        for checkpoint in self.stage_manager.checkpoints:
            checkpoint.draw(screen, shake_offset)

        for chest in self.stage_manager.chests:
            chest.draw(screen, shake_offset)
            if not chest.opened and chest.item:
                item_offset_y = -5 if (pygame.time.get_ticks() // 500) % 2 == 0 else 0
                chest.item.draw(
                    screen, (shake_offset[0], shake_offset[1] + item_offset_y)
                )

        # 불길
        for fire in self.fires:
            fire.draw(screen, shake_offset)

        # 적
        for enemy in self.stage_manager.enemies:
            enemy.draw(screen, shake_offset)

        # 투사체
        for projectile in self.projectiles:
            projectile.draw(screen, shake_offset)

        # 보스
        if self.boss:
            self.boss.draw(screen, shake_offset)

        # 플레이어
        self.player.draw(screen, shake_offset)

        # 파티클
        draw_particles(screen, self.particles)

        # HUD
        self.ui_manager.draw_hud(
            screen,
            self.player,
            self.stage_manager.current_stage,
            self.deaths,
            self.start_time,
            self.checkpoint_stage,
        )

        # 보스 HUD
        if self.boss:
            self.ui_manager.draw_boss_hud(screen, self.boss)

        # 게임 오버 / 승리
        if self.game_state == GAME_STATE_GAME_OVER:
            elapsed = time.time() - self.start_time
            self.ui_manager.draw_game_over(screen, self.deaths, elapsed)
        elif self.game_state == GAME_STATE_VICTORY:
            # 승리 시점의 고정된 시간 사용
            if self.victory_time:
                elapsed = self.victory_time - self.start_time
            else:
                elapsed = time.time() - self.start_time
            self.ui_manager.draw_victory(
                screen, self.deaths, elapsed, self.items_collected
            )
    
    def draw(self, screen):
        if self.game_state == GAME_STATE_MENU:
            self.ui_manager.draw_menu(screen)
            return
        
        if self.game_state == GAME_STATE_DEV_MENU:
            # 게임 화면 위에 개발 메뉴 표시
            self.draw_game_screen(screen)
            self.ui_manager.draw_dev_menu(screen)
            return
        
        # 일반 게임 화면
        self.draw_game_screen(screen)

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.ui_manager.menu_selection = (
                    self.ui_manager.menu_selection - 1
                ) % 2
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.ui_manager.menu_selection = (
                    self.ui_manager.menu_selection + 1
                ) % 2
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.ui_manager.menu_selection == 0:
                    self.start_game()
                    return "start"
                elif self.ui_manager.menu_selection == 1:
                    return "quit"
        return None

    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC로 개발 메뉴 열기/닫기
                if self.game_state == GAME_STATE_PLAYING:
                    self.game_state = GAME_STATE_DEV_MENU
                elif self.game_state == GAME_STATE_DEV_MENU:
                    self.game_state = GAME_STATE_PLAYING
            elif event.key == pygame.K_r:
                if self.game_state == GAME_STATE_VICTORY:
                    self.__init__()
            elif event.key == pygame.K_f:
                self.player.start_dash()
            # Z, X 키는 update()에서 자동 연사 처리
    
    def handle_dev_menu_input(self, event):
        """개발 메뉴 입력 처리"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.ui_manager.dev_menu_selection = (
                    self.ui_manager.dev_menu_selection - 1
                ) % 4
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.ui_manager.dev_menu_selection = (
                    self.ui_manager.dev_menu_selection + 1
                ) % 4
            elif event.key == pygame.K_RETURN:
                selection = self.ui_manager.dev_menu_selection
                if selection == 0:  # Stage 1
                    self.load_stage(1)
                    self.game_state = GAME_STATE_PLAYING
                elif selection == 1:  # Stage 2
                    self.load_stage(2)
                    self.game_state = GAME_STATE_PLAYING
                elif selection == 2:  # Stage 3
                    self.load_stage(3)
                    self.game_state = GAME_STATE_PLAYING
                elif selection == 3:  # Resume
                    self.game_state = GAME_STATE_PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.game_state = GAME_STATE_PLAYING
