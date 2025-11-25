
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from entities.enemy import Enemy
from entities.items import Platform, Trap, Item, Chest, Checkpoint


class StageManager:
    def __init__(self):
        self.current_stage = 1
        self.platforms = []
        self.enemies = []
        self.traps = []
        self.chests = []
        self.checkpoints = []  # 체크포인트
        self.collapsed_platforms = set()  # 붕괴된 발판 인덱스

    def load_stage(self, stage_num, player):
        
        self.current_stage = stage_num
        self.platforms = []
        self.enemies = []
        self.traps = []
        self.chests = []
        self.checkpoints = []

        if stage_num == 1:
            self._load_stage_1(player)
        elif stage_num == 2:
            self._load_stage_2(player)
        elif stage_num == 3:
            self._load_stage_3(player)

    def _load_stage_1(self, player):
        
        player.x = 100
        player.y = 500
        player.has_sword = False

        # 발판
        self.platforms = [
            Platform(0, 650, SCREEN_WIDTH, 50),  # 바닥
            Platform(200, 550, 150, 20),
            Platform(420, 470, 130, 20),
            Platform(620, 390, 130, 20),
            Platform(400, 310, 150, 20),
            Platform(150, 230, 150, 20),
            Platform(450, 150, 150, 20),
            Platform(750, 150, 200, 20),  # 출구
        ]

        # 적
        self.enemies = [
            Enemy(250, 500, "skeleton"),
            Enemy(500, 400, "slime"),
        ]

        # 상자
        self.chests = [
            Chest(470, 430, Item(470, 430, "health")),
            Chest(250, 510, Item(250, 510, "speed")),
        ]
        
        # 체크포인트 (스테이지 시작 지점)
        self.checkpoints = [
            Checkpoint(50, 590)
        ]

    def _load_stage_2(self, player):
        
        player.x = 50
        player.y = 500
        player.has_sword = False

        # 발판
        self.platforms = [
            Platform(0, 650, 250, 50),  # 시작 바닥
            Platform(280, 580, 120, 20),
            Platform(450, 500, 120, 20, disappearing=True),
            Platform(620, 420, 120, 20),
            Platform(480, 340, 120, 20),
            Platform(280, 260, 120, 20, disappearing=True),
            Platform(100, 180, 150, 20),
            Platform(320, 120, 150, 20),
            Platform(550, 80, 150, 20),
            Platform(780, 50, 200, 20),  # 출구
        ]

        # 적
        self.enemies = [
            Enemy(300, 530, "skeleton"),
            Enemy(640, 370, "slime"),
        ]

        # 함정
        self.traps = [
            Trap(550, 360, "blade"),
            Trap(250, 200, "spike"),
            Trap(400, 80, "spike"),
            Trap(480, 280, "fireball"),
        ]

        # 상자
        self.chests = [
            Chest(820, 10, Item(820, 10, "sword")),  # 검 획득
            Chest(140, 140, Item(140, 140, "max_health")),
        ]
        
        # 체크포인트 (스테이지 시작 지점)
        self.checkpoints = [
            Checkpoint(10, 590)
        ]

    def _load_stage_3(self, player):
        
        player.x = 100
        player.y = 500
        player.has_sword = True  # 보스전에서는 검 기본 제공

        # 발판
        self.platforms = [
            Platform(0, 650, SCREEN_WIDTH, 50),  # 바닥
            Platform(200, 550, 600, 30),  # 중앙 메인 발판
            Platform(50, 450, 130, 20),  # 왼쪽 회피 발판
            Platform(820, 450, 130, 20),  # 오른쪽 회피 발판
            Platform(100, 350, 150, 20),  # 왼쪽 중간
            Platform(425, 350, 150, 20),  # 중앙 중간
            Platform(750, 350, 150, 20),  # 오른쪽 중간
            Platform(250, 250, 150, 20),  # 왼쪽 상단
            Platform(550, 250, 150, 20),  # 오른쪽 상단
        ]

        # 보스전에는 일반 적 없음
        self.enemies = []
        self.traps = []
        self.chests = []

        # 체크포인트 (스테이지 시작 지점)
        self.checkpoints = [
            Checkpoint(50, 590)
        ]

    def collapse_platforms(self):
        
        if self.current_stage != 3:
            return []

        import random

        # 바닥을 제외한 발판 중에서 랜덤 선택
        collapsible = [
            i
            for i in range(1, len(self.platforms))
            if i not in self.collapsed_platforms
        ]

        if len(collapsible) < PLATFORM_COLLAPSE_COUNT:
            return []

        # 랜덤으로 선택
        to_collapse = random.sample(collapsible, PLATFORM_COLLAPSE_COUNT)

        collapsed = []
        for idx in to_collapse:
            self.platforms[idx].start_collapse()
            self.collapsed_platforms.add(idx)
            collapsed.append(self.platforms[idx])

        return collapsed

    def update_platforms(self, player):
        
        for platform in self.platforms:
            if platform.disappearing:
                platform.update(player)
            if platform.collapsing:
                platform.update_collapse()

    def get_next_stage(self):
        
        if self.current_stage < 3:
            return self.current_stage + 1
        return None

    def is_at_exit(self, player):
        
        # 보스 스테이지(3)에서는 출구 없음
        if self.current_stage == 3:
            return False
        
        # 스테이지 1, 2에서만 출구 체크
        if self.current_stage in [1, 2]:
            return player.x > SCREEN_WIDTH - 50
        
        return False
