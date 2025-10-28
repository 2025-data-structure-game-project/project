import pygame
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from utils import (
    draw_text,
    draw_text_outline,
    draw_heart,
    draw_health_bar,
    draw_cooldown_indicator,
    format_time,
)


class UIManager:
    def __init__(self):
        self.menu_selection = 0
        self.flash_timer = 0
        self.dev_menu_selection = 0  # 개발 메뉴 선택

    def draw_menu(self, screen):
        screen.fill(BLACK)

        # 타이틀
        draw_text_outline(
            screen,
            "DARKSPIRE",
            SCREEN_WIDTH // 2,
            150,
            FONT_TITLE,
            GOLD,
            BLACK,
            center=True,
        )

        # 부제
        draw_text(
            screen,
            "Tower of Darkness",
            SCREEN_WIDTH // 2,
            220,
            FONT_SMALL,
            GRAY,
            center=True,
        )

        # 메뉴 옵션
        options = ["Start Game", "Quit"]
        for i, option in enumerate(options):
            y = 350 + i * 80
            if self.menu_selection == i:
                # 선택된 옵션
                draw_text_outline(
                    screen,
                    f"> {option} <",
                    SCREEN_WIDTH // 2,
                    y,
                    FONT_MEDIUM,
                    YELLOW,
                    BLACK,
                    center=True,
                )
            else:
                draw_text(
                    screen,
                    option,
                    SCREEN_WIDTH // 2,
                    y,
                    FONT_MEDIUM,
                    WHITE,
                    center=True,
                )

        # 조작법 안내
        draw_text(
            screen,
            "Controls: Arrow Keys / WASD - Move, Space - Jump, F - Dash",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            FONT_SMALL,
            GRAY,
            center=True,
        )
        draw_text(
            screen,
            "Z - Melee Attack (with sword), X - Ranged Attack",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            FONT_SMALL,
            GRAY,
            center=True,
        )

    def draw_hud(self, screen, player, stage, deaths, start_time, checkpoint_stage=None):
        # 하트 그리기
        heart_x = UI_PADDING
        heart_y = UI_PADDING
        for i in range(player.max_hearts):
            filled = i < player.hearts
            draw_heart(
                screen,
                heart_x + i * (HEART_SIZE + HEART_SPACING),
                heart_y,
                HEART_SIZE,
                filled,
            )

        # 스테이지 정보
        draw_text_outline(
            screen,
            f"Stage {stage}",
            SCREEN_WIDTH - UI_PADDING - 100,
            UI_PADDING,
            FONT_SMALL,
            WHITE,
            BLACK,
        )
        
        # 체크포인트 정보
        if checkpoint_stage is not None:
            draw_text_outline(
                screen,
                f"Checkpoint: Stage {checkpoint_stage}",
                SCREEN_WIDTH // 2,
                UI_PADDING,
                FONT_SMALL,
                GREEN,
                BLACK,
                center=True,
            )

        # 사망 횟수
        draw_text_outline(
            screen,
            f"Deaths: {deaths}",
            SCREEN_WIDTH - UI_PADDING - 100,
            UI_PADDING + 30,
            FONT_SMALL,
            RED,
            BLACK,
        )

        # 플레이 시간
        elapsed = time.time() - start_time
        time_str = format_time(elapsed)
        draw_text_outline(
            screen,
            f"Time: {time_str}",
            SCREEN_WIDTH - UI_PADDING - 100,
            UI_PADDING + 60,
            FONT_SMALL,
            CYAN,
            BLACK,
        )

        # 대시 쿨다운 인디케이터
        dash_x = UI_PADDING
        dash_y = UI_PADDING + HEART_SIZE + 20
        draw_cooldown_indicator(
            screen,
            dash_x + 20,
            dash_y + 20,
            15,
            player.dash_cooldown,
            PLAYER_DASH_COOLDOWN,
            CYAN,
        )
        draw_text(screen, "Dash", dash_x + 45, dash_y + 10, FONT_SMALL, WHITE)

        # 검 공격 쿨다운 (검 보유 시)
        if player.has_sword:
            attack_x = UI_PADDING
            attack_y = dash_y + 50
            draw_cooldown_indicator(
                screen,
                attack_x + 20,
                attack_y + 20,
                15,
                player.attack_cooldown,
                PLAYER_ATTACK_COOLDOWN,
                YELLOW,
            )
            draw_text(screen, "Attack", attack_x + 45, attack_y + 10, FONT_SMALL, WHITE)

        # 원거리 공격 쿨다운
        ranged_x = UI_PADDING
        ranged_y = dash_y + 100 if player.has_sword else dash_y + 50
        draw_cooldown_indicator(
            screen,
            ranged_x + 20,
            ranged_y + 20,
            15,
            player.ranged_attack_cooldown,
            PLAYER_RANGED_COOLDOWN,
            PINK,
        )
        draw_text(screen, "Ranged", ranged_x + 45, ranged_y + 10, FONT_SMALL, WHITE)

    def draw_boss_hud(self, screen, boss):
        if not boss:
            return

        # 보스 이름
        draw_text_outline(
            screen,
            "Dark Knight",
            SCREEN_WIDTH // 2,
            UI_PADDING,
            FONT_MEDIUM,
            RED,
            BLACK,
            center=True,
        )

        # 체력바
        bar_x = (SCREEN_WIDTH - BOSS_HP_BAR_WIDTH) // 2
        bar_y = UI_PADDING + 40
        draw_health_bar(
            screen,
            bar_x,
            bar_y,
            BOSS_HP_BAR_WIDTH,
            BOSS_HP_BAR_HEIGHT,
            boss.health,
            boss.max_health,
            BLACK,
            GREEN,
            WHITE,
        )

        # HP 텍스트
        hp_text = f"{boss.health} / {boss.max_health}"
        draw_text(
            screen,
            hp_text,
            SCREEN_WIDTH // 2,
            bar_y + 5,
            FONT_SMALL,
            WHITE,
            center=True,
        )

        # 상태 표시
        status_y = bar_y + BOSS_HP_BAR_HEIGHT + 10
        if boss.berserk_mode:
            draw_text_outline(
                screen,
                "BERSERK MODE!",
                SCREEN_WIDTH // 2,
                status_y,
                FONT_SMALL,
                RED,
                BLACK,
                center=True,
            )
        elif boss.vulnerable and boss.health > BOSS_VULNERABLE_THRESHOLD:
            self.flash_timer += 1
            if self.flash_timer % 20 < 10:
                draw_text_outline(
                    screen,
                    "ATTACK NOW!",
                    SCREEN_WIDTH // 2,
                    status_y,
                    FONT_SMALL,
                    YELLOW,
                    BLACK,
                    center=True,
                )
        elif boss.stunned:
            draw_text_outline(
                screen,
                "STUNNED",
                SCREEN_WIDTH // 2,
                status_y,
                FONT_SMALL,
                GRAY,
                BLACK,
                center=True,
            )

        # 방어막 아이콘
        icon_x = bar_x - 30
        icon_y = bar_y + 5
        if boss.health > BOSS_VULNERABLE_THRESHOLD and not boss.vulnerable:
            # 방어 중
            pygame.draw.circle(screen, PURPLE, (icon_x, icon_y), 12)
            pygame.draw.circle(screen, LIGHT_BLUE, (icon_x, icon_y), 12, 2)
        elif boss.vulnerable or boss.health <= BOSS_VULNERABLE_THRESHOLD:
            # 공격 가능
            pygame.draw.circle(screen, YELLOW, (icon_x, icon_y), 12)
            pygame.draw.line(
                screen, RED, (icon_x - 8, icon_y - 8), (icon_x + 8, icon_y + 8), 3
            )
            pygame.draw.line(
                screen, RED, (icon_x - 8, icon_y + 8), (icon_x + 8, icon_y - 8), 3
            )

    def draw_game_over(self, screen, deaths, elapsed_time):
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 200))
        screen.blit(overlay, (0, 0))

        # 게임 오버 텍스트
        draw_text_outline(
            screen,
            "GAME OVER",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 100,
            FONT_LARGE,
            RED,
            BLACK,
            center=True,
        )

        # 통계
        draw_text(
            screen,
            f"Deaths: {deaths}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            FONT_MEDIUM,
            WHITE,
            center=True,
        )

        time_str = format_time(elapsed_time)
        draw_text(
            screen,
            f"Time: {time_str}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            FONT_MEDIUM,
            WHITE,
            center=True,
        )

        # 안내
        draw_text(
            screen,
            "Press R to Retry",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 120,
            FONT_SMALL,
            YELLOW,
            center=True,
        )

    def draw_victory(self, screen, deaths, elapsed_time, items_collected):
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 200))
        screen.blit(overlay, (0, 0))

        # 승리 텍스트
        draw_text_outline(
            screen,
            "VICTORY!",
            SCREEN_WIDTH // 2,
            80,
            FONT_TITLE,
            GOLD,
            BLACK,
            center=True,
        )

        # 엔딩 스토리
        draw_text(
            screen,
            "The Dark Knight has been defeated!",
            SCREEN_WIDTH // 2,
            150,
            FONT_MEDIUM,
            CYAN,
            center=True,
        )
        
        draw_text(
            screen,
            "The tower's darkness fades away...",
            SCREEN_WIDTH // 2,
            185,
            FONT_SMALL,
            GRAY,
            center=True,
        )

        # 스코어 계산
        score = self._calculate_score(deaths, elapsed_time, items_collected)
        rank = self._calculate_rank(deaths, elapsed_time)
        rank_color = self._get_rank_color(rank)

        # 스코어 박스
        box_y = 230
        box_height = 280
        score_box = pygame.Surface((600, box_height), pygame.SRCALPHA)
        score_box.fill((*DARK_GRAY, 180))
        pygame.draw.rect(score_box, GOLD, (0, 0, 600, box_height), 3)
        screen.blit(score_box, (SCREEN_WIDTH // 2 - 300, box_y))

        # 통계 표시
        stats_y = box_y + 30
        
        draw_text_outline(
            screen,
            "=== MISSION COMPLETE ===",
            SCREEN_WIDTH // 2,
            stats_y,
            FONT_MEDIUM,
            YELLOW,
            BLACK,
            center=True,
        )

        stats_y += 50
        
        # 시간 보너스
        time_str = format_time(elapsed_time)
        time_bonus = max(0, 1000 - int(elapsed_time * 2))
        draw_text(
            screen,
            f"Clear Time: {time_str}",
            SCREEN_WIDTH // 2 - 150,
            stats_y,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            screen,
            f"+{time_bonus}",
            SCREEN_WIDTH // 2 + 150,
            stats_y,
            FONT_SMALL,
            GREEN,
        )

        stats_y += 35
        
        # 사망 페널티
        death_penalty = deaths * 100
        draw_text(
            screen,
            f"Deaths: {deaths}",
            SCREEN_WIDTH // 2 - 150,
            stats_y,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            screen,
            f"-{death_penalty}",
            SCREEN_WIDTH // 2 + 150,
            stats_y,
            FONT_SMALL,
            RED,
        )

        stats_y += 35
        
        # 아이템 보너스
        item_bonus = items_collected * 200
        draw_text(
            screen,
            f"Items Collected: {items_collected}",
            SCREEN_WIDTH // 2 - 150,
            stats_y,
            FONT_SMALL,
            WHITE,
        )
        draw_text(
            screen,
            f"+{item_bonus}",
            SCREEN_WIDTH // 2 + 150,
            stats_y,
            FONT_SMALL,
            GREEN,
        )

        stats_y += 50
        
        # 구분선
        pygame.draw.line(
            screen,
            GOLD,
            (SCREEN_WIDTH // 2 - 250, stats_y),
            (SCREEN_WIDTH // 2 + 250, stats_y),
            2
        )

        stats_y += 20
        
        # 최종 스코어
        draw_text_outline(
            screen,
            f"TOTAL SCORE: {score}",
            SCREEN_WIDTH // 2,
            stats_y,
            FONT_LARGE,
            GOLD,
            BLACK,
            center=True,
        )

        stats_y += 50
        
        # 등급
        draw_text_outline(
            screen,
            f"RANK: {rank}",
            SCREEN_WIDTH // 2,
            stats_y,
            FONT_LARGE,
            rank_color,
            BLACK,
            center=True,
        )

        # 안내
        draw_text(
            screen,
            "Press R to Play Again  |  Press ESC to Main Menu",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            FONT_SMALL,
            YELLOW,
            center=True,
        )

    def draw_warning(self, screen, message):
        draw_text_outline(
            screen,
            message,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            FONT_LARGE,
            RED,
            BLACK,
            center=True,
        )

    def draw_message(self, screen, message, y=None):
        if y is None:
            y = SCREEN_HEIGHT // 2 + 100

        draw_text_outline(
            screen,
            message,
            SCREEN_WIDTH // 2,
            y,
            FONT_MEDIUM,
            WHITE,
            BLACK,
            center=True,
        )

    def _calculate_score(self, deaths, elapsed_time, items_collected):
        """최종 스코어 계산"""
        base_score = 5000
        time_bonus = max(0, 1000 - int(elapsed_time * 2))
        death_penalty = deaths * 100
        item_bonus = items_collected * 200
        
        total_score = base_score + time_bonus + item_bonus - death_penalty
        return max(0, total_score)
    
    def _calculate_rank(self, deaths, elapsed_time):
        score = 1000
        score -= deaths * 50
        score -= int(elapsed_time / 10)

        if score >= 900:
            return "S"
        elif score >= 800:
            return "A"
        elif score >= 700:
            return "B"
        elif score >= 600:
            return "C"
        else:
            return "D"

    def _get_rank_color(self, rank):
        colors = {"S": GOLD, "A": YELLOW, "B": GREEN, "C": CYAN, "D": GRAY}
        return colors.get(rank, WHITE)

    def draw_stage_transition(self, screen, stage_num):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 220))
        screen.blit(overlay, (0, 0))

        stage_names = {1: "Tower Entrance", 2: "Trap Zone", 3: "Boss Room"}

        draw_text_outline(
            screen,
            f"Stage {stage_num}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 50,
            FONT_LARGE,
            CYAN,
            BLACK,
            center=True,
        )

        draw_text(
            screen,
            stage_names.get(stage_num, "Unknown"),
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 20,
            FONT_MEDIUM,
            WHITE,
            center=True,
        )

    def draw_tutorial(self, screen, stage):
        if stage == 1:
            hints = [
                "Use Arrow Keys to Move",
                "Press Space to Jump",
                "Press F to Dash (Has Cooldown)",
                "Collect items from chests!",
            ]
        elif stage == 2:
            hints = [
                "Watch out for traps!",
                "Some platforms disappear when stepped on",
                "Get the sword from the chest at the end",
            ]
        elif stage == 3:
            hints = [
                "Boss Fight!",
                "Attack when the boss is vulnerable (Yellow Stars)",
                "Use Z for melee, D for ranged attack",
            ]
        else:
            return

        y = SCREEN_HEIGHT - 150
        for hint in hints:
            draw_text(
                screen, hint, SCREEN_WIDTH // 2, y, FONT_SMALL, YELLOW, center=True
            )
            y += 25

    def draw_dev_menu(self, screen):
        """개발자 메뉴 - 스테이지 선택"""
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 200))
        screen.blit(overlay, (0, 0))

        # 타이틀
        draw_text_outline(
            screen,
            "DEV MENU",
            SCREEN_WIDTH // 2,
            100,
            FONT_LARGE,
            CYAN,
            BLACK,
            center=True,
        )

        draw_text(
            screen,
            "Stage Select",
            SCREEN_WIDTH // 2,
            160,
            FONT_SMALL,
            GRAY,
            center=True,
        )

        # 스테이지 옵션
        options = [
            "Stage 1 - Tower Entrance",
            "Stage 2 - Trap Zone", 
            "Stage 3 - Boss Room",
            "Resume Game"
        ]
        
        for i, option in enumerate(options):
            y = 250 + i * 70
            if self.dev_menu_selection == i:
                # 선택된 옵션
                draw_text_outline(
                    screen,
                    f"> {option} <",
                    SCREEN_WIDTH // 2,
                    y,
                    FONT_MEDIUM,
                    YELLOW,
                    BLACK,
                    center=True,
                )
            else:
                draw_text(
                    screen,
                    option,
                    SCREEN_WIDTH // 2,
                    y,
                    FONT_MEDIUM,
                    WHITE,
                    center=True,
                )

        # 조작 안내
        draw_text(
            screen,
            "Arrow Keys: Navigate | Enter: Select | ESC: Close",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 50,
            FONT_SMALL,
            GRAY,
            center=True,
        )
