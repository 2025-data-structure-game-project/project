import os
import sys
import time

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from entities.boss import Boss
from entities.player import Player
from entities.projectile import Fire, Projectile
from systems.asset_manager import get_asset_manager
from systems.stage_manager import StageManager
from systems.ui_manager import UIManager
from utils import (
    check_collision,
    check_rect_collision,
    create_particle_burst,
    draw_particles,
    get_attack_box,
    get_entity_box,
    shake_screen,
    update_particles,
)


class Game:
    def __init__(self):
        self.assets = get_asset_manager()
        self.player = Player(100, 500)
        self.stage_manager = StageManager()
        self.ui_manager = UIManager()

        self.boss = None
        self.projectiles = []
        self.fires = []
        self.particles = []

        self.game_state = GAME_STATE_MENU
        self.deaths = 0
        self.start_time = time.time()
        self.items_collected = 0
        self.victory_time = None

        self.checkpoint_stage = 1
        self.stage_checkpoints = {1: False, 2: False, 3: False}

        self.screen_shake_timer = 0
        self.screen_shake_intensity = 0
        self.platform_collapse_triggered = False

        self.item_message = ""
        self.item_message_timer = 0

    def play_music(self):
        self.assets.play_music("bgm", loops=-1, volume=0.5)

    def stop_music(self):
        self.assets.stop_music()

    def start_game(self):
        self.game_state = GAME_STATE_PLAYING
        self.deaths = 0
        self.start_time = time.time()
        self.items_collected = 0
        self.checkpoint_stage = 1
        self.stage_checkpoints = {1: False, 2: False, 3: False}
        self.load_stage(1)

    def load_stage(self, stage_num):
        self.stage_manager.load_stage(stage_num, self.player)

        if (
            stage_num not in self.stage_checkpoints
            or not self.stage_checkpoints[stage_num]
        ):
            self.stage_checkpoints[stage_num] = True
            self.checkpoint_stage = stage_num

        if stage_num in [1, 2]:
            self.play_music()
        else:
            self.stop_music()

        if stage_num == 3:
            self.boss = Boss(SCREEN_WIDTH // 2 - 48, 480)
            self.platform_collapse_triggered = False
        else:
            self.boss = None

        self.projectiles = []
        self.fires = []
        self.particles = []

    def restart_stage(self):
        self.deaths += 1
        self.player.health = self.player.max_health
        self.player.invincible_time = 60
        self.load_stage(self.checkpoint_stage)

    def update(self, keys):
        if self.game_state != GAME_STATE_PLAYING:
            return

        self.player.update(keys, self.stage_manager.platforms)

        if keys[pygame.K_x]:
            self.ranged_attack()
        if keys[pygame.K_z]:
            self.melee_attack()

        self.stage_manager.update_platforms(self.player)

        for enemy in self.stage_manager.enemies:
            enemy.update(self.stage_manager.platforms, self.player)

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

        for projectile in self.projectiles[:]:
            projectile.update()

            if not projectile.active:
                self.projectiles.remove(projectile)
                continue

            if projectile.from_player:
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
                    if self.boss.take_damage(5):
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
                        projectile.active = False
                        self.particles.extend(
                            create_particle_burst(
                                projectile.x, projectile.y, 5, [WHITE, LIGHT_BLUE]
                            )
                        )
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

            if projectile.type == "fireball" and projectile.active:
                platform, fire_x, fire_y = projectile.check_platform_collision(
                    self.stage_manager.platforms
                )
                if platform:
                    projectile.active = False
                    self.fires.append(Fire(fire_x, fire_y, platform.width))
                    self.start_screen_shake(5)

        for fire in self.fires[:]:
            fire.update()
            if not fire.active:
                self.fires.remove(fire)
                continue

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

        for trap in self.stage_manager.traps:
            fire_signal = trap.update(self.player)
            if fire_signal:
                direction = 1 if self.player.x > trap.x else -1
                self.projectiles.append(
                    Projectile(trap.x, trap.y, direction, "fireball")
                )

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
                        self.player.health = 0
                    else:
                        self.player.take_damage()

        for checkpoint in self.stage_manager.checkpoints:
            if checkpoint.check_activation(self.player):
                self.particles.extend(
                    create_particle_burst(
                        checkpoint.x + checkpoint.width // 2,
                        checkpoint.y + checkpoint.height // 2,
                        20,
                        [GREEN, YELLOW, WHITE],
                    )
                )

        if self.boss:
            pattern, actions = self.boss.update(
                self.player, self.stage_manager.platforms, self.projectiles
            )

            if actions:
                for action in actions:
                    self.handle_boss_action(action)

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

            if (
                not self.platform_collapse_triggered
                and self.boss.health <= PLATFORM_COLLAPSE_HP_THRESHOLD
            ):
                self.trigger_platform_collapse()

            if self.boss.health <= 0:
                self.victory_time = time.time()
                self.game_state = GAME_STATE_VICTORY

        update_particles(self.particles)

        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1

        if self.item_message_timer > 0:
            self.item_message_timer -= 1

        if self.player.health <= 0 or self.player.y > SCREEN_HEIGHT:
            self.restart_stage()

        if self.stage_manager.is_at_exit(self.player):
            next_stage = self.stage_manager.get_next_stage()
            if next_stage:
                self.load_stage(next_stage)

    def handle_boss_action(self, action):
        action_type, data = action

        if action_type == "shockwave":
            if self.player.on_ground and abs(self.player.x - data["x"]) < 200:
                if self.player.invincible_time <= 0:
                    self.player.take_damage()

            for i in range(3):
                self.particles.extend(
                    create_particle_burst(data["x"], data["y"], 20, [YELLOW, ORANGE])
                )

            self.start_screen_shake(10)

        elif action_type == "flame":
            direction = data["direction"]
            angle = data.get("angle", 0)
            self.projectiles.append(
                Projectile(
                    self.boss.x + 48,
                    self.boss.y + 48,
                    direction,
                    "fireball",
                    angle=angle,
                )
            )

        elif action_type == "slash":
            direction = data["direction"]
            slash_range = 80
            slash_x = (
                self.boss.x + self.boss.width
                if direction > 0
                else self.boss.x - slash_range
            )

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

            if data.get("num", 0) == 2:
                self.projectiles.append(
                    Projectile(
                        self.boss.x + 48,
                        self.boss.y + 48,
                        direction,
                        "sword_beam",
                        from_player=False,
                    )
                )

        elif action_type == "teleport":
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

        attack_box = get_attack_box(
            self.player.x,
            self.player.y,
            self.player.width,
            self.player.height,
            self.player.facing_right,
            PLAYER_ATTACK_RANGE,
        )

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

        if self.boss:
            boss_box = get_entity_box(
                self.boss.x, self.boss.y, self.boss.width, self.boss.height
            )
            if check_collision(attack_box, boss_box):
                if self.boss.take_damage(1):
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
        messages = {
            "health": "HP 회복!",
            "max_health": "최대 HP 증가!",
            "speed": "속도 증가!",
            "sword": "검 획득!",
        }

        if item.type == "health":
            self.player.heal()
        elif item.type == "max_health":
            self.player.max_health += 1
            self.player.health = self.player.max_health
        elif item.type == "speed":
            self.player.speed_boost = 3
        elif item.type == "sword":
            self.player.has_sword = True

        self.items_collected += 1
        self.item_message = messages.get(item.type, "아이템 획득!")
        self.item_message_timer = 120

        self.particles.extend(
            create_particle_burst(
                item.x + item.width // 2, item.y + item.height // 2, 20, [GOLD, YELLOW]
            )
        )

    def trigger_platform_collapse(self):
        self.platform_collapse_triggered = True
        collapsed = self.stage_manager.collapse_platforms()
        if collapsed:
            self.start_screen_shake(30)

    def start_screen_shake(self, duration, intensity=SCREEN_SHAKE_INTENSITY):
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity

    def get_shake_offset(self):
        if self.screen_shake_timer > 0:
            return shake_screen(self.screen_shake_intensity)
        return (0, 0)

    def draw_game_screen(self, screen):
        screen.fill(BLACK)

        bg_sprite = self.assets.get_sprite(
            f"bg_stage{self.stage_manager.current_stage}"
        )
        if bg_sprite:
            screen.blit(bg_sprite, (0, 0))

        shake_offset = self.get_shake_offset()

        for platform in self.stage_manager.platforms:
            platform.draw(screen, shake_offset)

        for trap in self.stage_manager.traps:
            trap.draw(screen, shake_offset)

        for checkpoint in self.stage_manager.checkpoints:
            checkpoint.draw(screen, shake_offset)

        for fire in self.fires:
            fire.draw(screen, shake_offset)

        for enemy in self.stage_manager.enemies:
            enemy.draw(screen, shake_offset)

        for projectile in self.projectiles:
            projectile.draw(screen, shake_offset)

        if self.boss:
            self.boss.draw(screen, shake_offset)

        self.player.draw(screen, shake_offset)

        draw_particles(screen, self.particles)

        self.ui_manager.draw_hud(
            screen,
            self.player,
            self.stage_manager.current_stage,
            self.deaths,
            self.start_time,
            self.checkpoint_stage,
        )

        if self.item_message_timer > 0:
            from utils.effects import draw_text_outline

            draw_text_outline(
                screen,
                self.item_message,
                SCREEN_WIDTH // 2,
                100,
                36,
                YELLOW,
                BLACK,
                center=True,
            )

        if self.boss:
            self.ui_manager.draw_boss_hud(screen, self.boss)

        if self.game_state == GAME_STATE_VICTORY:
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
            self.draw_game_screen(screen)
            self.ui_manager.draw_dev_menu(screen)
            return

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
                if self.game_state == GAME_STATE_PLAYING:
                    self.game_state = GAME_STATE_DEV_MENU
                elif self.game_state == GAME_STATE_DEV_MENU:
                    self.game_state = GAME_STATE_PLAYING
            elif event.key == pygame.K_r:
                if self.game_state == GAME_STATE_VICTORY:
                    self.__init__()
            elif event.key == pygame.K_f:
                self.player.start_dash()

    def handle_dev_menu_input(self, event):
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
                if selection == 0:
                    self.load_stage(1)
                    self.game_state = GAME_STATE_PLAYING
                elif selection == 1:
                    self.load_stage(2)
                    self.game_state = GAME_STATE_PLAYING
                elif selection == 2:
                    self.load_stage(3)
                    self.game_state = GAME_STATE_PLAYING
                elif selection == 3:
                    self.game_state = GAME_STATE_PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.game_state = GAME_STATE_PLAYING
