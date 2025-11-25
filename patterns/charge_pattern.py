from config import BOSS_CHARGE_SPEED
from patterns.base_pattern import BasePattern


class ChargePattern(BasePattern):
    def update(self, player, projectiles):
        self.timer += 1

        if self.phase == 0:
            if self.timer >= 20:
                self.phase = 1
                self.timer = 0

                charge_direction = 1 if player.x > self.boss.x else -1
                self.boss.velocity_x = charge_direction * BOSS_CHARGE_SPEED

        elif self.phase == 1:
            if abs(self.boss.velocity_x) < 5 or self.boss.stunned:
                self.phase = 2
                self.timer = 0
                self.boss.vulnerable = True
                self.boss.vulnerable_timer = 60

        elif self.phase == 2:
            if self.timer >= 60:
                self.completed = True

        return None
