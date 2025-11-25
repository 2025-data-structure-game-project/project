import os
from typing import Dict, Optional, Tuple

import pygame


class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_paths: Dict[str, str] = {}
        self.base_path = "assets"

        self.dummy_colors = {
            "player": (100, 150, 255),
            "enemy": (255, 100, 100),
            "boss": (200, 0, 0),
            "item": (255, 215, 0),
            "projectile": (255, 255, 0),
            "ui": (200, 200, 200),
            "slime": (100, 255, 100),
            "skeleton": (200, 200, 200),
            "bg": (50, 50, 50),
            "cutscene": (20, 20, 40),
            "icon": (180, 180, 180),
            "default": (150, 150, 150),
        }

        self._load_all_assets()

    def _load_all_assets(self):
        self._load_sprites()
        self._load_audio()

    def _load_sprites(self):
        # UI 하트
        self._load_sprite("ui_heart_full", "ui/hearts/heart_full.png", (25, 25))
        self._load_sprite("ui_heart_empty", "ui/hearts/heart_empty.png", (25, 25))
        self._load_sprite(
            "ui_heart_container", "ui/hearts/heart_container.png", (25, 25)
        )

        # UI 아이콘
        self._load_sprite("icon_sword", "ui/icons/sword.png", (30, 30))
        self._load_sprite("icon_speed", "ui/icons/speed.png", (30, 30))
        self._load_sprite("icon_health", "ui/icons/health.png", (30, 30))

        # 플레이어
        self._load_sprite("player_idle", "sprites/player/idle.png", (64, 64))
        self._load_sprite("player_run", "sprites/player/run.png", (64, 64))
        self._load_sprite("player_jump", "sprites/player/jump.png", (64, 64))
        self._load_sprite("player_fall", "sprites/player/fall.png", (64, 64))
        self._load_sprite("player_dash", "sprites/player/dash.png", (64, 64))
        self._load_sprite("player_attack", "sprites/player/attack.png", (64, 64))
        self._load_sprite("player_hit", "sprites/player/hit.png", (64, 64))
        self._load_sprite("player_death", "sprites/player/death.png", (64, 64))

        # 슬라임 (파랑)
        self._load_sprite(
            "slime_blue_idle", "sprites/enemies/slime/blue_idle.png", (48, 48)
        )
        self._load_sprite(
            "slime_blue_jump", "sprites/enemies/slime/blue_jump.png", (48, 48)
        )
        self._load_sprite(
            "slime_blue_hurt", "sprites/enemies/slime/blue_hurt.png", (48, 48)
        )
        self._load_sprite(
            "slime_blue_death", "sprites/enemies/slime/blue_death.png", (48, 48)
        )

        # 슬라임 (초록)
        self._load_sprite(
            "slime_green_idle", "sprites/enemies/slime/green_idle.png", (48, 48)
        )
        self._load_sprite(
            "slime_green_jump", "sprites/enemies/slime/green_jump.png", (48, 48)
        )
        self._load_sprite(
            "slime_green_hurt", "sprites/enemies/slime/green_hurt.png", (48, 48)
        )
        self._load_sprite(
            "slime_green_death", "sprites/enemies/slime/green_death.png", (48, 48)
        )

        # 슬라임 (빨강)
        self._load_sprite(
            "slime_red_idle", "sprites/enemies/slime/red_idle.png", (48, 48)
        )
        self._load_sprite(
            "slime_red_jump", "sprites/enemies/slime/red_jump.png", (48, 48)
        )
        self._load_sprite(
            "slime_red_hurt", "sprites/enemies/slime/red_hurt.png", (48, 48)
        )
        self._load_sprite(
            "slime_red_death", "sprites/enemies/slime/red_death.png", (48, 48)
        )

        # 스켈레톤
        self._load_sprite(
            "skeleton_idle", "sprites/enemies/skeleton/idle.png", (48, 48)
        )
        self._load_sprite(
            "skeleton_walk", "sprites/enemies/skeleton/walk.png", (48, 48)
        )
        self._load_sprite(
            "skeleton_attack", "sprites/enemies/skeleton/attack.png", (48, 48)
        )
        self._load_sprite(
            "skeleton_hurt", "sprites/enemies/skeleton/hurt.png", (48, 48)
        )
        self._load_sprite(
            "skeleton_death", "sprites/enemies/skeleton/death.png", (48, 48)
        )

        # 보스
        self._load_sprite("boss_idle", "sprites/boss/idle.png", (96, 96))
        self._load_sprite("boss_attack", "sprites/boss/attack.png", (96, 96))
        self._load_sprite("boss_hurt", "sprites/boss/hurt.png", (96, 96))
        self._load_sprite("boss_death", "sprites/boss/death.png", (96, 96))

        # 아이템
        self._load_sprite("item_health", "sprites/items/health_potion.png", (30, 30))
        self._load_sprite(
            "item_max_health", "sprites/items/heart_container.png", (30, 30)
        )
        self._load_sprite("item_sword", "sprites/items/sword.png", (30, 30))
        self._load_sprite("item_speed", "sprites/items/speed_boots.png", (30, 30))
        self._load_sprite(
            "item_chest_closed", "sprites/items/chest_closed.png", (40, 35)
        )
        self._load_sprite("item_chest_open", "sprites/items/chest_open.png", (40, 35))

        # 투사체
        self._load_sprite(
            "projectile_energy", "sprites/projectiles/energy_shot.png", (20, 20)
        )
        self._load_sprite(
            "projectile_fireball", "sprites/projectiles/fireball.png", (30, 30)
        )

        # 배경
        self._load_sprite("bg_stage1", "backgrounds/stage1.png", (1000, 700))
        self._load_sprite("bg_stage2", "backgrounds/stage2.png", (1000, 700))
        self._load_sprite("bg_stage3", "backgrounds/stage3.png", (1000, 700))

        # 컷신
        self._load_sprite("cutscene_ending", "cutscenes/ending.png", (1000, 700))

    def _load_audio(self):
        self._register_music("bgm", "audio/music/bgm.mp3")

    def _load_sprite(self, name: str, path: str, size: Tuple[int, int]):
        full_path = os.path.join(self.base_path, path)
        try:
            if os.path.exists(full_path):
                sprite = pygame.image.load(full_path).convert_alpha()
                if sprite.get_size() != size:
                    sprite = pygame.transform.scale(sprite, size)
                self.sprites[name] = sprite
            else:
                self._create_dummy_sprite(name, size)
        except:
            self._create_dummy_sprite(name, size)

    def _create_dummy_sprite(self, name: str, size: Tuple[int, int]):
        sprite_type = name.split("_")[0]
        color = self.dummy_colors.get(sprite_type, self.dummy_colors["default"])
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        self.sprites[name] = surface

    def _register_music(self, name: str, path: str):
        full_path = os.path.join(self.base_path, path)
        self.music_paths[name] = full_path

    def _load_sound(self, name: str, path: str):
        full_path = os.path.join(self.base_path, path)
        self.sounds[name] = pygame.mixer.Sound(full_path)

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        return self.sprites.get(name)

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        return self.sounds.get(name)

    def get_music_path(self, name: str) -> Optional[str]:
        return self.music_paths.get(name)

    def play_sound(self, name: str, volume: float = 1.0):
        sound = self.get_sound(name)
        if sound:
            sound.set_volume(volume)
            sound.play()

    def play_music(self, name: str, loops: int = -1, volume: float = 0.5):
        music_path = self.get_music_path(name)
        if music_path:
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops)
            except:
                pass

    def stop_music(self):
        pygame.mixer.music.stop()

    def fade_out_music(self, milliseconds: int = 1000):
        pygame.mixer.music.fadeout(milliseconds)


def get_asset_manager() -> AssetManager:
    return AssetManager()
