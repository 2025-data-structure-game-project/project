import time

import pygame

from config import *
from systems.asset_manager import get_asset_manager
from utils.effects import draw_health_bar, draw_text, draw_text_outline, format_time


class UIManager:
    def __init__(self):
        self.assets = get_asset_manager()
        self.menu_selection = 0
        self.dev_menu_selection = 0

    def draw_hearts(self, surface, player, x, y):
        for i in range(player.max_health):
            heart_x = x + i * (HEART_SIZE + HEART_SPACING)
            heart_y = y

            if i < player.health:
                sprite = self.assets.get_sprite("ui_heart_full")
            else:
                sprite = self.assets.get_sprite("ui_heart_empty")

            if sprite:
                surface.blit(sprite, (heart_x, heart_y))
            else:
                filled = i < player.health
                color = RED if filled else DARK_GRAY

                pygame.draw.circle(
                    surface,
                    color,
                    (int(heart_x + HEART_SIZE // 4), int(heart_y + HEART_SIZE // 2)),
                    HEART_SIZE // 4,
                )
                pygame.draw.circle(
                    surface,
                    color,
                    (
                        int(heart_x + HEART_SIZE * 3 // 4),
                        int(heart_y + HEART_SIZE // 2),
                    ),
                    HEART_SIZE // 4,
                )

                points = [
                    (heart_x, heart_y + HEART_SIZE // 2),
                    (heart_x + HEART_SIZE, heart_y + HEART_SIZE // 2),
                    (heart_x + HEART_SIZE // 2, heart_y + HEART_SIZE),
                ]
                pygame.draw.polygon(surface, color, points)

    def draw_hud(self, surface, player, stage, deaths, start_time, checkpoint_stage):
        self.draw_hearts(surface, player, UI_PADDING, UI_PADDING)

        stage_text = f"Stage {stage}"
        draw_text(
            surface, stage_text, SCREEN_WIDTH - 120, UI_PADDING, FONT_MEDIUM, WHITE
        )

        elapsed = time.time() - start_time
        time_text = format_time(elapsed)
        draw_text(
            surface, time_text, SCREEN_WIDTH // 2 - 40, UI_PADDING, FONT_MEDIUM, WHITE
        )

        deaths_text = f"Deaths: {deaths}"
        draw_text(
            surface, deaths_text, UI_PADDING, SCREEN_HEIGHT - 40, FONT_SMALL, WHITE
        )

        if checkpoint_stage > 1:
            checkpoint_text = f"Checkpoint: Stage {checkpoint_stage}"
            draw_text(
                surface,
                checkpoint_text,
                UI_PADDING,
                SCREEN_HEIGHT - 60,
                FONT_SMALL,
                YELLOW,
            )

        if player.has_sword:
            sword_icon = self.assets.get_sprite("icon_sword")
            if sword_icon:
                surface.blit(sword_icon, (UI_PADDING, 60))
            else:
                pygame.draw.rect(surface, GRAY, (UI_PADDING, 60, 25, 25))

        if player.speed_boost > 0:
            speed_icon = self.assets.get_sprite("icon_speed")
            if speed_icon:
                surface.blit(speed_icon, (UI_PADDING + 35, 60))
            else:
                pygame.draw.rect(surface, CYAN, (UI_PADDING + 35, 60, 25, 25))

    def draw_boss_hud(self, surface, boss):
        bar_x = (SCREEN_WIDTH - BOSS_HP_BAR_WIDTH) // 2
        bar_y = 50

        boss_name = "Dark Lord"
        draw_text_outline(
            surface,
            boss_name,
            SCREEN_WIDTH // 2,
            bar_y - 20,
            FONT_MEDIUM,
            WHITE,
            BLACK,
            center=True,
        )

        draw_health_bar(
            surface,
            bar_x,
            bar_y,
            BOSS_HP_BAR_WIDTH,
            BOSS_HP_BAR_HEIGHT,
            boss.health,
            boss.max_health,
            BLACK,
            RED,
            GOLD,
        )

        hp_text = f"{boss.health}/{boss.max_health}"
        draw_text(
            surface,
            hp_text,
            bar_x + BOSS_HP_BAR_WIDTH // 2 - 30,
            bar_y + 2,
            FONT_SMALL,
            WHITE,
        )

        if boss.berserk_mode:
            berserk_text = "BERSERK MODE!"
            draw_text_outline(
                surface,
                berserk_text,
                SCREEN_WIDTH // 2,
                bar_y + 30,
                FONT_MEDIUM,
                RED,
                BLACK,
                center=True,
            )

        if boss.vulnerable and boss.health > BOSS_VULNERABLE_THRESHOLD:
            vuln_text = "VULNERABLE!"
            draw_text_outline(
                surface,
                vuln_text,
                SCREEN_WIDTH // 2,
                bar_y + 50,
                FONT_SMALL,
                YELLOW,
                BLACK,
                center=True,
            )

    def draw_menu(self, surface):
        surface.fill((20, 20, 40))

        title = "DARKSPIRE"
        subtitle = "Tower of Darkness"

        draw_text_outline(
            surface,
            title,
            SCREEN_WIDTH // 2,
            150,
            FONT_TITLE,
            WHITE,
            BLACK,
            center=True,
        )
        draw_text(surface, subtitle, SCREEN_WIDTH // 2 - 100, 220, FONT_MEDIUM, GRAY)

        start_color = YELLOW if self.menu_selection == 0 else WHITE
        quit_color = YELLOW if self.menu_selection == 1 else WHITE

        draw_text_outline(
            surface,
            "Start Game",
            SCREEN_WIDTH // 2,
            350,
            FONT_LARGE,
            start_color,
            BLACK,
            center=True,
        )
        draw_text_outline(
            surface,
            "Quit",
            SCREEN_WIDTH // 2,
            420,
            FONT_LARGE,
            quit_color,
            BLACK,
            center=True,
        )

        controls_y = 520
        draw_text(
            surface, "Controls:", SCREEN_WIDTH // 2 - 150, controls_y, FONT_SMALL, GRAY
        )
        draw_text(
            surface,
            "Arrow Keys / WASD: Move",
            SCREEN_WIDTH // 2 - 150,
            controls_y + 25,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            surface,
            "Space: Jump",
            SCREEN_WIDTH // 2 - 150,
            controls_y + 45,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            surface,
            "F: Dash",
            SCREEN_WIDTH // 2 - 150,
            controls_y + 65,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            surface,
            "Z: Attack (with sword)",
            SCREEN_WIDTH // 2 - 150,
            controls_y + 85,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            surface,
            "X: Ranged Attack",
            SCREEN_WIDTH // 2 - 150,
            controls_y + 105,
            FONT_SMALL,
            WHITE,
        )

    def draw_game_over(self, surface, deaths, elapsed):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        screen_img = self.assets.get_sprite("screen_gameover")
        if screen_img:
            surface.blit(screen_img, (0, 0))

        draw_text_outline(
            surface,
            "GAME OVER",
            SCREEN_WIDTH // 2,
            200,
            FONT_TITLE,
            RED,
            BLACK,
            center=True,
        )

        stats_y = 350
        draw_text_outline(
            surface,
            f"Deaths: {deaths}",
            SCREEN_WIDTH // 2,
            stats_y,
            FONT_LARGE,
            WHITE,
            BLACK,
            center=True,
        )
        draw_text_outline(
            surface,
            f"Time: {format_time(elapsed)}",
            SCREEN_WIDTH // 2,
            stats_y + 60,
            FONT_LARGE,
            WHITE,
            BLACK,
            center=True,
        )

        draw_text_outline(
            surface,
            "Press R to Restart",
            SCREEN_WIDTH // 2,
            500,
            FONT_MEDIUM,
            YELLOW,
            BLACK,
            center=True,
        )
        draw_text_outline(
            surface,
            "Press ESC for Menu",
            SCREEN_WIDTH // 2,
            550,
            FONT_SMALL,
            GRAY,
            BLACK,
            center=True,
        )

    def draw_victory(self, surface, deaths, elapsed, items_collected):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        victory_img = self.assets.get_sprite("screen_victory")
        if victory_img:
            surface.blit(victory_img, (0, 0))
        else:
            ending_img = self.assets.get_sprite("cutscene_ending")
            if ending_img:
                surface.blit(ending_img, (0, 0))

        draw_text_outline(
            surface,
            "VICTORY!",
            SCREEN_WIDTH // 2,
            150,
            FONT_TITLE,
            GOLD,
            BLACK,
            center=True,
        )

        draw_text_outline(
            surface,
            "The Dark Lord has been defeated!",
            SCREEN_WIDTH // 2,
            230,
            FONT_MEDIUM,
            WHITE,
            BLACK,
            center=True,
        )

        stats_y = 320
        draw_text_outline(
            surface,
            f"Deaths: {deaths}",
            SCREEN_WIDTH // 2,
            stats_y,
            FONT_LARGE,
            WHITE,
            BLACK,
            center=True,
        )
        draw_text_outline(
            surface,
            f"Time: {format_time(elapsed)}",
            SCREEN_WIDTH // 2,
            stats_y + 50,
            FONT_LARGE,
            WHITE,
            BLACK,
            center=True,
        )
        draw_text_outline(
            surface,
            f"Items Collected: {items_collected}",
            SCREEN_WIDTH // 2,
            stats_y + 100,
            FONT_LARGE,
            WHITE,
            BLACK,
            center=True,
        )

        rank = self._get_rank(deaths, elapsed)
        rank_color = self._get_rank_color(rank)
        draw_text_outline(
            surface,
            f"Rank: {rank}",
            SCREEN_WIDTH // 2,
            stats_y + 150,
            FONT_LARGE,
            rank_color,
            BLACK,
            center=True,
        )

        draw_text_outline(
            surface,
            "Press R to Restart",
            SCREEN_WIDTH // 2,
            550,
            FONT_MEDIUM,
            YELLOW,
            BLACK,
            center=True,
        )
        draw_text_outline(
            surface,
            "Press ESC for Menu",
            SCREEN_WIDTH // 2,
            600,
            FONT_SMALL,
            GRAY,
            BLACK,
            center=True,
        )

    def draw_dev_menu(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        menu_width = 400
        menu_height = 350
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        pygame.draw.rect(
            surface, (40, 40, 60), (menu_x, menu_y, menu_width, menu_height)
        )
        pygame.draw.rect(surface, WHITE, (menu_x, menu_y, menu_width, menu_height), 3)

        draw_text_outline(
            surface,
            "DEVELOPER MENU",
            SCREEN_WIDTH // 2,
            menu_y + 30,
            FONT_LARGE,
            CYAN,
            BLACK,
            center=True,
        )

        options = ["Stage 1", "Stage 2", "Stage 3 (Boss)", "Resume"]

        for i, option in enumerate(options):
            y = menu_y + 100 + i * 50
            color = YELLOW if i == self.dev_menu_selection else WHITE
            draw_text_outline(
                surface,
                option,
                SCREEN_WIDTH // 2,
                y,
                FONT_MEDIUM,
                color,
                BLACK,
                center=True,
            )

        draw_text(
            surface,
            "ESC: Close Menu",
            menu_x + 20,
            menu_y + menu_height - 30,
            FONT_SMALL,
            GRAY,
        )

    def _get_rank(self, deaths, elapsed):
        if deaths == 0 and elapsed < 180:
            return "S"
        elif deaths <= 2 and elapsed < 300:
            return "A"
        elif deaths <= 5 and elapsed < 480:
            return "B"
        elif deaths <= 10:
            return "C"
        else:
            return "D"

    def _get_rank_color(self, rank):
        rank_colors = {"S": GOLD, "A": CYAN, "B": GREEN, "C": YELLOW, "D": GRAY}
        return rank_colors.get(rank, WHITE)
