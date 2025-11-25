from typing import Any, Dict, Optional, Tuple


class BasePattern:
    def __init__(self, boss):
        self.boss = boss
        self.timer = 0
        self.phase = 0
        self.completed = False

    def start(self):
        self.timer = 0
        self.phase = 0
        self.completed = False

    def update(self, player, projectiles) -> Optional[Tuple[str, Dict[str, Any]]]:
        self.timer += 1
        return None

    def is_complete(self) -> bool:
        return self.completed

    def reset(self):
        self.timer = 0
        self.phase = 0
        self.completed = False
