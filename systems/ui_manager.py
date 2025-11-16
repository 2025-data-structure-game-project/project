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

        # 메뉴 배경 이미지 로드
        self.menu_image = None
        try:
            self.menu_image = pygame.image.load("static/Gemini_Generated_Image_lpcj8tlpcj8tlpcj.png")
            # 화면 크기에 맞게 조정
            self.menu_image = pygame.transform.scale(self.menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"메뉴 이미지 로드 실패: {e}")

    def draw_menu(self, screen):
        # 배경 이미지 또는 검은색 배경
        if self.menu_image:
            screen.blit(self.menu_image, (0, 0))
            # 이미지 위에 반투명 오버레이 추가 (텍스트 가독성 향상)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((*BLACK, 150))  # 더 어둡게 조정
            screen.blit(overlay, (0, 0))
        else:
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
        draw_text_outline(
            screen,
            "Tower of Darkness",
            SCREEN_WIDTH // 2,
            220,
            FONT_SMALL,
            GRAY,
            BLACK,
            center=True,
        )

        # 메뉴 옵션
        options = ["Start Game", "Quit"]
        for i, option in enumerate(options):
            y = 350 + i * 80
            if self.menu_selection == i:
                # 선택된 옵션 - 화살표 추가
                draw_text_outline(
                    screen,
                    f"> {option} <",
                    SCREEN_WIDTH // 2,
                    y,
                    FONT_MEDIUM,
                    GOLD,
                    BLACK,
                    center=True,
                )
            else:
                draw_text_outline(
                    screen,
                    option,
                    SCREEN_WIDTH // 2,
                    y,
                    FONT_MEDIUM,
                    WHITE,
                    BLACK,
                    center=True,
                )

        # 조작법 안내
        draw_text_outline(
            screen,
            "Move: Arrow Keys/WASD  |  Jump: Space  |  Dash: F",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            FONT_SMALL - 2,
            LIGHT_BLUE,
            BLACK,
            center=True,
        )
        draw_text_outline(
            screen,
            "Melee: Z (with sword)  |  Ranged: X",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            FONT_SMALL - 2,
            LIGHT_BLUE,
            BLACK,
            center=True,
        )

    def draw_hud(self, screen, player, stage, deaths, start_time, checkpoint_stage=None):
        top_y = UI_PADDING + 10

        # 왼쪽: 체력 (빨간색 원으로 표시)
        hp_x = UI_PADDING + 15
        circle_radius = 10
        circle_spacing = 28

        for i in range(player.max_hearts):
            x_pos = hp_x + i * circle_spacing
            if i < player.hearts:
                # 체력 있음 - 채워진 빨간색 원
                pygame.draw.circle(screen, RED, (x_pos, top_y), circle_radius)
                pygame.draw.circle(screen, DARK_RED, (x_pos, top_y), circle_radius, 2)
            else:
                # 체력 없음 - 빈 원
                pygame.draw.circle(screen, DARK_GRAY, (x_pos, top_y), circle_radius)
                pygame.draw.circle(screen, BLACK, (x_pos, top_y), circle_radius, 2)

        # 중앙 왼쪽: 스테이지 정보
        stage_x = UI_PADDING + 200
        draw_text_outline(
            screen,
            f"STAGE {stage}",
            stage_x,
            top_y - 5,
            FONT_SMALL,
            CYAN,
            BLACK,
        )

        # 중앙: 체크포인트 정보
        if checkpoint_stage is not None:
            draw_text_outline(
                screen,
                f"Checkpoint: Stage {checkpoint_stage}",
                SCREEN_WIDTH // 2,
                top_y - 5,
                FONT_SMALL - 4,
                GREEN,
                BLACK,
                center=True,
            )

        # 오른쪽: 시간과 사망 횟수
        info_x = SCREEN_WIDTH - UI_PADDING - 150

        elapsed = time.time() - start_time
        time_str = format_time(elapsed)
        draw_text_outline(
            screen,
            f"Time: {time_str}",
            info_x,
            top_y - 5,
            FONT_SMALL - 4,
            LIGHT_BLUE,
            BLACK,
        )

        draw_text_outline(
            screen,
            f"Deaths: {deaths}",
            info_x + 100,
            top_y - 5,
            FONT_SMALL - 4,
            RED,
            BLACK,
        )

        # 상단 두 번째 줄: 스킬 쿨다운
        skill_y = top_y + 25
        skill_x = UI_PADDING + 15

        # 대시 쿨다운
        draw_cooldown_indicator(
            screen,
            skill_x,
            skill_y,
            10,
            player.dash_cooldown,
            PLAYER_DASH_COOLDOWN,
            CYAN,
        )
        draw_text_outline(screen, "Dash(F)", skill_x + 20, skill_y - 5, FONT_SMALL - 6, WHITE, BLACK)
        skill_x += 90

        # 검 공격 쿨다운 (검 보유 시)
        if player.has_sword:
            draw_cooldown_indicator(
                screen,
                skill_x,
                skill_y,
                10,
                player.attack_cooldown,
                PLAYER_ATTACK_COOLDOWN,
                YELLOW,
            )
            draw_text_outline(screen, "Melee(Z)", skill_x + 20, skill_y - 5, FONT_SMALL - 6, WHITE, BLACK)
            skill_x += 95

        # 원거리 공격 쿨다운
        draw_cooldown_indicator(
            screen,
            skill_x,
            skill_y,
            10,
            player.ranged_attack_cooldown,
            PLAYER_RANGED_COOLDOWN,
            PINK,
        )
        draw_text_outline(screen, "Ranged(X)", skill_x + 20, skill_y - 5, FONT_SMALL - 6, WHITE, BLACK)

    def draw_boss_hud(self, screen, boss):
        if not boss:
            return

        # 보스 이름
        draw_text_outline(
            screen,
            "DARK KNIGHT",
            SCREEN_WIDTH // 2,
            UI_PADDING + 15,
            FONT_MEDIUM,
            RED,
            BLACK,
            center=True,
        )

        # 체력바 배경 - 얇은 테두리만
        bar_x = (SCREEN_WIDTH - 400) // 2
        bar_y = UI_PADDING + 50
        bar_bg = pygame.Surface((400, 25), pygame.SRCALPHA)
        bar_bg.fill((*BLACK, 150))
        pygame.draw.rect(bar_bg, RED, (0, 0, 400, 25), 2, border_radius=5)
        screen.blit(bar_bg, (bar_x, bar_y))

        # 체력바
        health_percent = boss.health / boss.max_health
        bar_width = int(390 * health_percent)
        if bar_width > 0:
            # 체력바 색상 (체력에 따라 변화)
            if health_percent > 0.5:
                hp_color = GREEN
            elif health_percent > 0.25:
                hp_color = YELLOW
            else:
                hp_color = RED

            health_bar = pygame.Surface((bar_width, 17), pygame.SRCALPHA)
            health_bar.fill(hp_color)
            screen.blit(health_bar, (bar_x + 4, bar_y + 4))

        # HP 텍스트
        hp_text = f"{boss.health} / {boss.max_health}"
        draw_text_outline(
            screen,
            hp_text,
            SCREEN_WIDTH // 2,
            bar_y + 4,
            FONT_SMALL,
            WHITE,
            BLACK,
            center=True,
        )

        # 상태 표시
        status_y = bar_y + 32
        if boss.berserk_mode:
            draw_text_outline(
                screen,
                "!! BERSERK MODE !!",
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
                    ">>> ATTACK NOW! <<<",
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
                LIGHT_BLUE,
                BLACK,
                center=True,
            )

        # 방어막 아이콘 - 더 작게
        icon_x = bar_x - 35
        icon_y = bar_y + 12
        if boss.health > BOSS_VULNERABLE_THRESHOLD and not boss.vulnerable:
            # 방어 중 - 방패 아이콘
            pygame.draw.circle(screen, PURPLE, (icon_x, icon_y), 15)
            pygame.draw.circle(screen, LIGHT_BLUE, (icon_x, icon_y), 15, 3)
            pygame.draw.circle(screen, PURPLE, (icon_x, icon_y), 8)
        elif boss.vulnerable or boss.health <= BOSS_VULNERABLE_THRESHOLD:
            # 공격 가능 - 타겟 아이콘
            pygame.draw.circle(screen, YELLOW, (icon_x, icon_y), 15)
            pygame.draw.circle(screen, RED, (icon_x, icon_y), 15, 3)
            pygame.draw.circle(screen, RED, (icon_x, icon_y), 6, 2)
            pygame.draw.line(
                screen, RED, (icon_x - 10, icon_y), (icon_x + 10, icon_y), 3
            )
            pygame.draw.line(
                screen, RED, (icon_x, icon_y - 10), (icon_x, icon_y + 10), 3
            )

    def draw_game_over(self, screen, deaths, elapsed_time):
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 220))
        screen.blit(overlay, (0, 0))

        # 게임 오버 패널
        panel = pygame.Surface((600, 400), pygame.SRCALPHA)
        panel.fill((*DARK_GRAY, 200))
        pygame.draw.rect(panel, RED, (0, 0, 600, 400), 4, border_radius=15)
        screen.blit(panel, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 200))

        # 게임 오버 텍스트
        draw_text_outline(
            screen,
            "GAME OVER",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 120,
            FONT_LARGE,
            RED,
            BLACK,
            center=True,
        )

        # 구분선
        pygame.draw.line(
            screen,
            RED,
            (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 60),
            (SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 - 60),
            2
        )

        # 통계 박스
        stats_y = SCREEN_HEIGHT // 2 - 20

        # 사망 횟수
        death_box = pygame.Surface((250, 50), pygame.SRCALPHA)
        death_box.fill((*BLACK, 150))
        pygame.draw.rect(death_box, DARK_RED, (0, 0, 250, 50), 2, border_radius=5)
        screen.blit(death_box, (SCREEN_WIDTH // 2 - 125, stats_y))

        draw_text_outline(
            screen,
            f"Deaths: {deaths}",
            SCREEN_WIDTH // 2,
            stats_y + 15,
            FONT_MEDIUM,
            WHITE,
            BLACK,
            center=True,
        )

        # 플레이 시간
        time_str = format_time(elapsed_time)
        time_box = pygame.Surface((250, 50), pygame.SRCALPHA)
        time_box.fill((*BLACK, 150))
        pygame.draw.rect(time_box, CYAN, (0, 0, 250, 50), 2, border_radius=5)
        screen.blit(time_box, (SCREEN_WIDTH // 2 - 125, stats_y + 70))

        draw_text_outline(
            screen,
            f"Time: {time_str}",
            SCREEN_WIDTH // 2,
            stats_y + 85,
            FONT_MEDIUM,
            WHITE,
            BLACK,
            center=True,
        )

        # 안내 박스
        guide_box = pygame.Surface((400, 40), pygame.SRCALPHA)
        guide_box.fill((*GOLD, 120))
        pygame.draw.rect(guide_box, YELLOW, (0, 0, 400, 40), 2, border_radius=5)
        screen.blit(guide_box, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150))

        draw_text(
            screen,
            "Press R to Retry",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 160,
            FONT_SMALL,
            YELLOW,
            center=True,
        )

    def draw_victory(self, screen, deaths, elapsed_time, items_collected):
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 220))
        screen.blit(overlay, (0, 0))

        # 승리 헤더 패널
        header_panel = pygame.Surface((700, 120), pygame.SRCALPHA)
        header_panel.fill((*BLACK, 200))
        pygame.draw.rect(header_panel, GOLD, (0, 0, 700, 120), 4, border_radius=12)
        screen.blit(header_panel, (SCREEN_WIDTH // 2 - 350, 40))

        # 승리 텍스트
        draw_text_outline(
            screen,
            "VICTORY!",
            SCREEN_WIDTH // 2,
            70,
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
            125,
            FONT_SMALL + 2,
            CYAN,
            center=True,
        )

        # 스코어 계산
        score = self._calculate_score(deaths, elapsed_time, items_collected)
        rank = self._calculate_rank(deaths, elapsed_time)
        rank_color = self._get_rank_color(rank)

        # 스코어 박스
        box_y = 180
        box_height = 330
        score_box = pygame.Surface((650, box_height), pygame.SRCALPHA)
        score_box.fill((*DARK_GRAY, 190))
        pygame.draw.rect(score_box, GOLD, (0, 0, 650, box_height), 3, border_radius=10)
        screen.blit(score_box, (SCREEN_WIDTH // 2 - 325, box_y))

        # 통계 표시
        stats_y = box_y + 25

        draw_text_outline(
            screen,
            "MISSION COMPLETE",
            SCREEN_WIDTH // 2,
            stats_y,
            FONT_MEDIUM,
            YELLOW,
            BLACK,
            center=True,
        )

        pygame.draw.line(
            screen,
            GOLD,
            (SCREEN_WIDTH // 2 - 250, stats_y + 30),
            (SCREEN_WIDTH // 2 + 250, stats_y + 30),
            2
        )

        stats_y += 55

        # 통계 항목들을 박스로 깔끔하게 표시
        # 시간 보너스
        time_str = format_time(elapsed_time)
        time_bonus = max(0, 1000 - int(elapsed_time * 2))

        stat_box = pygame.Surface((550, 40), pygame.SRCALPHA)
        stat_box.fill((*BLACK, 120))
        pygame.draw.rect(stat_box, CYAN, (0, 0, 550, 40), 1, border_radius=5)
        screen.blit(stat_box, (SCREEN_WIDTH // 2 - 275, stats_y - 5))

        draw_text(
            screen,
            f"Clear Time: {time_str}",
            SCREEN_WIDTH // 2 - 180,
            stats_y + 5,
            FONT_SMALL,
            WHITE,
        )
        draw_text_outline(
            screen,
            f"+{time_bonus}",
            SCREEN_WIDTH // 2 + 180,
            stats_y + 5,
            FONT_SMALL,
            GREEN,
            BLACK,
        )

        stats_y += 50

        # 사망 페널티
        death_penalty = deaths * 100

        stat_box = pygame.Surface((550, 40), pygame.SRCALPHA)
        stat_box.fill((*BLACK, 120))
        pygame.draw.rect(stat_box, RED, (0, 0, 550, 40), 1, border_radius=5)
        screen.blit(stat_box, (SCREEN_WIDTH // 2 - 275, stats_y - 5))

        draw_text(
            screen,
            f"Deaths: {deaths}",
            SCREEN_WIDTH // 2 - 180,
            stats_y + 5,
            FONT_SMALL,
            WHITE,
        )
        draw_text_outline(
            screen,
            f"-{death_penalty}",
            SCREEN_WIDTH // 2 + 180,
            stats_y + 5,
            FONT_SMALL,
            RED,
            BLACK,
        )

        stats_y += 50

        # 아이템 보너스
        item_bonus = items_collected * 200

        stat_box = pygame.Surface((550, 40), pygame.SRCALPHA)
        stat_box.fill((*BLACK, 120))
        pygame.draw.rect(stat_box, GREEN, (0, 0, 550, 40), 1, border_radius=5)
        screen.blit(stat_box, (SCREEN_WIDTH // 2 - 275, stats_y - 5))

        draw_text(
            screen,
            f"Items Collected: {items_collected}",
            SCREEN_WIDTH // 2 - 180,
            stats_y + 5,
            FONT_SMALL,
            WHITE,
        )
        draw_text_outline(
            screen,
            f"+{item_bonus}",
            SCREEN_WIDTH // 2 + 180,
            stats_y + 5,
            FONT_SMALL,
            GREEN,
            BLACK,
        )

        stats_y += 60

        # 구분선
        pygame.draw.line(
            screen,
            GOLD,
            (SCREEN_WIDTH // 2 - 280, stats_y),
            (SCREEN_WIDTH // 2 + 280, stats_y),
            3
        )

        stats_y += 25

        # 최종 스코어 박스
        score_final_box = pygame.Surface((400, 60), pygame.SRCALPHA)
        score_final_box.fill((*GOLD, 100))
        pygame.draw.rect(score_final_box, GOLD, (0, 0, 400, 60), 3, border_radius=8)
        screen.blit(score_final_box, (SCREEN_WIDTH // 2 - 200, stats_y - 10))

        draw_text_outline(
            screen,
            f"SCORE: {score}",
            SCREEN_WIDTH // 2,
            stats_y + 10,
            FONT_MEDIUM + 4,
            GOLD,
            BLACK,
            center=True,
        )

        stats_y += 75

        # 등급 박스
        rank_box = pygame.Surface((150, 60), pygame.SRCALPHA)
        rank_box.fill((*rank_color, 120))
        pygame.draw.rect(rank_box, rank_color, (0, 0, 150, 60), 3, border_radius=8)
        screen.blit(rank_box, (SCREEN_WIDTH // 2 - 75, stats_y - 10))

        draw_text_outline(
            screen,
            f"RANK {rank}",
            SCREEN_WIDTH // 2,
            stats_y + 10,
            FONT_MEDIUM,
            rank_color,
            BLACK,
            center=True,
        )

        # 안내
        guide_box = pygame.Surface((550, 40), pygame.SRCALPHA)
        guide_box.fill((*GOLD, 120))
        pygame.draw.rect(guide_box, YELLOW, (0, 0, 550, 40), 2, border_radius=5)
        screen.blit(guide_box, (SCREEN_WIDTH // 2 - 275, SCREEN_HEIGHT - 80))

        draw_text(
            screen,
            "R: Play Again  |  ESC: Main Menu",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 65,
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
        overlay.fill((*BLACK, 220))
        screen.blit(overlay, (0, 0))

        # 메뉴 패널
        menu_panel = pygame.Surface((600, 480), pygame.SRCALPHA)
        menu_panel.fill((*DARK_GRAY, 200))
        pygame.draw.rect(menu_panel, CYAN, (0, 0, 600, 480), 4, border_radius=12)
        screen.blit(menu_panel, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 240))

        # 타이틀
        draw_text_outline(
            screen,
            "DEV MENU",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 190,
            FONT_LARGE,
            CYAN,
            BLACK,
            center=True,
        )

        draw_text(
            screen,
            "Stage Select",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 140,
            FONT_SMALL,
            LIGHT_BLUE,
            center=True,
        )

        pygame.draw.line(
            screen,
            CYAN,
            (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 115),
            (SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 - 115),
            2
        )

        # 스테이지 옵션
        options = [
            "Stage 1 - Tower Entrance",
            "Stage 2 - Trap Zone",
            "Stage 3 - Boss Room",
            "Resume Game"
        ]

        option_y = SCREEN_HEIGHT // 2 - 70

        for i, option in enumerate(options):
            y = option_y + i * 75

            # 옵션 박스
            if self.dev_menu_selection == i:
                # 선택된 옵션
                option_box = pygame.Surface((500, 55), pygame.SRCALPHA)
                option_box.fill((*CYAN, 100))
                pygame.draw.rect(option_box, CYAN, (0, 0, 500, 55), 3, border_radius=8)
                screen.blit(option_box, (SCREEN_WIDTH // 2 - 250, y - 10))

                draw_text_outline(
                    screen,
                    option,
                    SCREEN_WIDTH // 2,
                    y + 7,
                    FONT_MEDIUM,
                    CYAN,
                    BLACK,
                    center=True,
                )
            else:
                option_box = pygame.Surface((500, 55), pygame.SRCALPHA)
                option_box.fill((*BLACK, 120))
                pygame.draw.rect(option_box, DARK_GRAY, (0, 0, 500, 55), 2, border_radius=8)
                screen.blit(option_box, (SCREEN_WIDTH // 2 - 250, y - 10))

                draw_text(
                    screen,
                    option,
                    SCREEN_WIDTH // 2,
                    y + 7,
                    FONT_MEDIUM,
                    WHITE,
                    center=True,
                )

        # 조작 안내
        guide_box = pygame.Surface((550, 40), pygame.SRCALPHA)
        guide_box.fill((*BLACK, 150))
        pygame.draw.rect(guide_box, GRAY, (0, 0, 550, 40), 2, border_radius=5)
        screen.blit(guide_box, (SCREEN_WIDTH // 2 - 275, SCREEN_HEIGHT - 80))

        draw_text(
            screen,
            "Arrow Keys: Navigate  |  Enter: Select  |  ESC: Close",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 65,
            FONT_SMALL - 2,
            LIGHT_BLUE,
            center=True,
        )
