from patterns.base_pattern import BasePattern


class FlamePattern(BasePattern):
    def update(self, player, projectiles):
        self.timer += 1

        if self.phase == 0:
            if self.timer >= 40:
                self.phase = 1
                self.timer = 0

        elif self.phase == 1:
            if self.timer in [10, 20, 30]:
                direction = 1 if self.boss.facing_right else -1
                angle_offset = [0, -0.3, 0.3][self.timer // 10 - 1]
                return ("flame", {"direction": direction, "angle": angle_offset})

            if self.timer >= 40:
                self.phase = 2
                self.timer = 0
                self.boss.vulnerable = True
                self.boss.vulnerable_timer = 60

        elif self.phase == 2:
            if self.timer >= 60:
                self.completed = True

        return None
