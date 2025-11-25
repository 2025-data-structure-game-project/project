from patterns.base_pattern import BasePattern


class SlashPattern(BasePattern):
    def __init__(self, boss):
        super().__init__(boss)
        self.slash_count = 0

    def start(self):
        super().start()
        self.slash_count = 0

    def update(self, player, projectiles):
        self.timer += 1

        if self.phase == 0:
            if self.timer >= 15:
                self.phase = 1
                self.timer = 0

        elif self.phase == 1:
            if self.timer % 15 == 0 and self.slash_count < 3:
                self.slash_count += 1
                direction = 1 if self.boss.facing_right else -1

                self.timer = 0
                return ("slash", {"num": self.slash_count - 1, "direction": direction})

            if self.slash_count >= 3 and self.timer >= 15:
                self.phase = 2
                self.timer = 0
                self.boss.vulnerable = True
                self.boss.vulnerable_timer = 60

        elif self.phase == 2:
            if self.timer >= 60:
                self.completed = True

        return None
