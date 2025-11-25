from config import BOSS_JUMP_POWER
from patterns.base_pattern import BasePattern


class JumpPattern(BasePattern):
    def update(self, player, projectiles):
        self.timer += 1

        if self.phase == 0:
            if self.timer >= 30:
                self.phase = 1
                self.boss.velocity_y = -BOSS_JUMP_POWER
                self.timer = 0

        elif self.phase == 1:
            if self.boss.velocity_y > 0:
                target_x = player.x - self.boss.width // 2
                if abs(self.boss.x - target_x) > 5:
                    self.boss.velocity_x = 3 if target_x > self.boss.x else -3

            if self.boss.on_ground and self.timer > 10:
                self.phase = 2
                self.timer = 0
                self.boss.velocity_x = 0
                self.boss.vulnerable = True
                self.boss.vulnerable_timer = 90

                return (
                    "shockwave",
                    {
                        "x": self.boss.x + self.boss.width // 2,
                        "y": self.boss.y + self.boss.height,
                    },
                )

        elif self.phase == 2:
            if self.timer >= 90:
                self.completed = True

        return None
