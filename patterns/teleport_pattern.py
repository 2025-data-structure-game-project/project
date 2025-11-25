import random

from patterns.base_pattern import BasePattern


class TeleportPattern(BasePattern):
    def update(self, player, projectiles):
        self.timer += 1

        if self.phase == 0:
            if self.timer >= 20:
                offset = 80 if random.random() > 0.5 else -80
                self.boss.x = player.x + offset
                self.boss.y = player.y - 100
                self.phase = 1
                self.timer = 0
                return ("teleport", {})

        elif self.phase == 1:
            if self.timer == 5:
                return (
                    "slash",
                    {"num": 0, "direction": 1 if self.boss.facing_right else -1},
                )

            if self.timer >= 20:
                self.completed = True

        return None
