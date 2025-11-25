import pygame

from config import *
from entities.base_entity import BaseEntity
from systems.asset_manager import get_asset_manager


class Item(BaseEntity):
    def __init__(self, x, y, item_type):
        super().__init__(x, y, ITEM_WIDTH, ITEM_HEIGHT)
        self.assets = get_asset_manager()
        self.type = item_type
        self.collected = False
        self.float_offset = 0
        self.float_timer = 0

    def update(self):
        self.float_timer += 1
        self.float_offset = -5 if (self.float_timer // 30) % 2 == 0 else 0


def draw(self, screen, shake_offset=(0, 0)):
    if not self.active:
        return
    draw_x = self.x + shake_offset[0]
    draw_y = self.y + shake_offset[1]
    if self.type == "blade":
        import math

        angle = (self.timer * 10) % 360
        center_x = draw_x + self.width // 2
        center_y = draw_y + self.height // 2
        pygame.draw.circle(screen, (100, 100, 110), (int(center_x), int(center_y)), 22)
        pygame.draw.circle(screen, (140, 140, 150), (int(center_x), int(center_y)), 20)
        pygame.draw.circle(screen, (60, 60, 70), (int(center_x), int(center_y)), 18)
        for i in range(12):
            blade_angle = math.radians(angle + i * 30)
            blade_x = center_x + 28 * math.cos(blade_angle)
            blade_y = center_y + 28 * math.sin(blade_angle)
            blade_base_angle1 = math.radians(angle + i * 30 - 5)
            blade_base_angle2 = math.radians(angle + i * 30 + 5)
            base1_x = center_x + 18 * math.cos(blade_base_angle1)
            base1_y = center_y + 18 * math.sin(blade_base_angle1)
            base2_x = center_x + 18 * math.cos(blade_base_angle2)
            base2_y = center_y + 18 * math.sin(blade_base_angle2)
            pygame.draw.polygon(
                screen,
                (180, 30, 30),
                [
                    (int(blade_x), int(blade_y)),
                    (int(base1_x), int(base1_y)),
                    (int(base2_x), int(base2_y)),
                ],
            )
        pygame.draw.circle(screen, (40, 40, 50), (int(center_x), int(center_y)), 6)
        pygame.draw.circle(screen, (20, 20, 30), (int(center_x), int(center_y)), 4)
    elif self.type == "spike":
        if not self.falling and self.timer % 60 < 30:
            pygame.draw.rect(screen, RED, (draw_x - 5, draw_y - 8, self.width + 10, 4))
            pygame.draw.polygon(
                screen,
                RED,
                [
                    (draw_x + self.width // 2 - 8, draw_y - 15),
                    (draw_x + self.width // 2, draw_y - 8),
                    (draw_x + self.width // 2 + 8, draw_y - 15),
                ],
            )
        spike_count = 5
        spike_width = self.width // spike_count
        for i in range(spike_count):
            spike_x = draw_x + i * spike_width
            points = [
                (spike_x + spike_width // 2, draw_y),
                (spike_x + 2, draw_y + self.height),
                (spike_x + spike_width - 2, draw_y + self.height),
            ]
            pygame.draw.polygon(screen, (90, 90, 100), points)
            pygame.draw.line(
                screen,
                (130, 130, 140),
                (spike_x + spike_width // 2, draw_y),
                (spike_x + 2, draw_y + self.height),
                2,
            )
            pygame.draw.line(
                screen,
                (50, 50, 60),
                (spike_x + spike_width // 2, draw_y),
                (spike_x + spike_width - 2, draw_y + self.height),
                2,
            )
            pygame.draw.circle(
                screen, (150, 50, 50), (spike_x + spike_width // 2, draw_y + 2), 3
            )
    elif self.type == "fireball":
        pygame.draw.rect(
            screen, (60, 40, 40), (draw_x, draw_y, self.width, self.height)
        )
        pygame.draw.rect(
            screen,
            (100, 60, 60),
            (draw_x + 3, draw_y + 3, self.width - 6, self.height - 6),
        )
        hole_center_x = draw_x + self.width // 2
        hole_center_y = draw_y + self.height // 2
        pygame.draw.circle(screen, BLACK, (hole_center_x, hole_center_y), 12)
        pygame.draw.circle(screen, (40, 20, 20), (hole_center_x, hole_center_y), 10)
        if self.timer > FIREBALL_INTERVAL - 30:
            import math

            charge = (self.timer - (FIREBALL_INTERVAL - 30)) / 30
            pygame.draw.circle(
                screen, ORANGE, (hole_center_x, hole_center_y), int(8 * charge)
            )
            pygame.draw.circle(
                screen, RED, (hole_center_x, hole_center_y), int(15 + charge * 8), 2
            )
            for i in range(8):
                angle = math.radians(i * 45 + self.timer * 10)
                px = hole_center_x + int((12 + charge * 8) * math.cos(angle))
                py = hole_center_y + int((12 + charge * 8) * math.sin(angle))
                pygame.draw.circle(screen, YELLOW, (px, py), int(2 + charge * 2))


class Chest(BaseEntity):
    def __init__(self, x, y, item):
        super().__init__(x, y, CHEST_WIDTH, CHEST_HEIGHT)
        self.assets = get_asset_manager()
        self.item = item
        self.opened = False
        self.open_animation = 0

    def draw(self, screen, shake_offset=(0, 0)):
        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        sprite_key = "item_chest_open" if self.opened else "item_chest_closed"
        sprite = self.assets.get_sprite(sprite_key)

        if sprite:
            screen.blit(sprite, (draw_x, draw_y))
        else:
            if self.opened:
                color = DARK_GRAY
                pygame.draw.rect(
                    screen, color, (draw_x, draw_y + 15, self.width, self.height - 15)
                )
                pygame.draw.rect(screen, ORANGE, (draw_x, draw_y, self.width, 15), 2)
            else:
                color = ORANGE
                pygame.draw.rect(
                    screen, color, (draw_x, draw_y, self.width, self.height)
                )
                pygame.draw.rect(screen, GOLD, (draw_x + 15, draw_y + 15, 10, 10))

                if pygame.time.get_ticks() % 1000 < 500:
                    pygame.draw.circle(
                        screen, YELLOW, (int(draw_x + 10), int(draw_y + 10)), 3
                    )


class Trap(BaseEntity):
    def __init__(self, x, y, trap_type):
        super().__init__(x, y, TRAP_WIDTH, TRAP_HEIGHT)
        self.type = trap_type
        self.timer = 0
        self.active = True
        self.falling = False
        self.original_x = x
        self.original_y = y

    def update(self, player):
        self.timer += 1

        if self.type == "blade":
            self.x = self.original_x + 100 * (1 if (self.timer // 60) % 2 == 0 else -1)

        elif self.type == "spike":
            if not self.falling:
                if abs(player.x - self.x) < 50 and player.y > self.y:
                    self.falling = True
            else:
                self.velocity_y += 0.5
                self.y += self.velocity_y
                if self.y > SCREEN_HEIGHT:
                    self.active = False

        elif self.type == "fireball":
            if self.timer >= FIREBALL_INTERVAL:
                self.timer = 0
                return True

        return False

    def draw(self, screen, shake_offset=(0, 0)):
        if not self.active:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.type == "blade":
            import math

            angle = (self.timer * 10) % 360
            center_x = draw_x + self.width // 2
            center_y = draw_y + self.height // 2

            pygame.draw.circle(screen, GRAY, (int(center_x), int(center_y)), 20)

            for i in range(8):
                blade_angle = math.radians(angle + i * 45)
                blade_x = center_x + 25 * math.cos(blade_angle)
                blade_y = center_y + 25 * math.sin(blade_angle)
                pygame.draw.line(
                    screen,
                    RED,
                    (int(center_x), int(center_y)),
                    (int(blade_x), int(blade_y)),
                    3,
                )

        elif self.type == "spike":
            if not self.falling and self.timer % 60 < 30:
                pygame.draw.rect(screen, RED, (draw_x, draw_y - 5, self.width, 3))

            for i in range(4):
                spike_x = draw_x + i * 10
                points = [
                    (spike_x, draw_y + self.height),
                    (spike_x + 5, draw_y),
                    (spike_x + 10, draw_y + self.height),
                ]
                pygame.draw.polygon(screen, GRAY, points)

        elif self.type == "fireball":
            pygame.draw.rect(
                screen, DARK_GRAY, (draw_x, draw_y, self.width, self.height)
            )

            if self.timer > FIREBALL_INTERVAL - 30:
                charge = (self.timer - (FIREBALL_INTERVAL - 30)) / 30
                pygame.draw.circle(
                    screen,
                    ORANGE,
                    (int(draw_x + self.width // 2), int(draw_y + self.height // 2)),
                    int(5 + charge * 10),
                    2,
                )


class Checkpoint(BaseEntity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60)
        self.activated = False
        self.animation_timer = 0

    def check_activation(self, player):
        if not self.activated:
            if (
                player.x < self.x + self.width
                and player.x + player.width > self.x
                and player.y < self.y + self.height
                and player.y + player.height > self.y
            ):
                self.activated = True
                return True
        return False

    def draw(self, screen, shake_offset=(0, 0)):
        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        self.animation_timer += 1

        if self.activated:
            color = GREEN
            wave = 3 * (1 if (self.animation_timer // 10) % 2 == 0 else -1)

            pygame.draw.rect(screen, DARK_GRAY, (draw_x + 5, draw_y, 5, self.height))

            flag_points = [
                (draw_x + 10, draw_y + 5),
                (draw_x + 35 + wave, draw_y + 15),
                (draw_x + 10, draw_y + 25),
            ]
            pygame.draw.polygon(screen, color, flag_points)

            if self.animation_timer % 60 < 30:
                pygame.draw.circle(
                    screen, YELLOW, (int(draw_x + 20), int(draw_y + 15)), 5, 2
                )
        else:
            color = GRAY
            pygame.draw.rect(screen, DARK_GRAY, (draw_x + 5, draw_y, 5, self.height))
            flag_points = [
                (draw_x + 10, draw_y + 5),
                (draw_x + 35, draw_y + 15),
                (draw_x + 10, draw_y + 25),
            ]
            pygame.draw.polygon(screen, color, flag_points)


class Platform(BaseEntity):
    def __init__(self, x, y, width, height, disappearing=False):
        super().__init__(x, y, width, height)
        self.disappearing = disappearing
        self.timer = 0
        self.visible = True
        self.original_visible = True
        self.warning = False
        self.collapsing = False
        self.collapse_timer = 0

    def update(self, player):
        if not self.disappearing or not self.visible:
            return

        if (
            player.x < self.x + self.width
            and player.x + player.width > self.x
            and player.y + player.height >= self.y
            and player.y + player.height <= self.y + 10
            and player.on_ground
        ):
            self.timer += 1
            if self.timer > DISAPPEARING_PLATFORM_TIMER:
                self.visible = False
                self.timer = 0
        else:
            if self.timer > 0:
                self.timer = max(0, self.timer - 1)
            if not self.visible and self.timer == 0:
                self.visible = True

    def start_collapse(self):
        if not self.collapsing:
            self.collapsing = True
            self.collapse_timer = 0
            self.warning = True

    def update_collapse(self):
        if not self.collapsing:
            return False

        self.collapse_timer += 1

        if self.collapse_timer < PLATFORM_COLLAPSE_WARNING:
            self.warning = True
        elif self.collapse_timer < PLATFORM_COLLAPSE_WARNING + 30:
            pass
        else:
            self.visible = False
            return True

        return False

    def draw(self, screen, shake_offset=(0, 0)):
        if not self.visible:
            return

        draw_x = self.x + shake_offset[0]
        draw_y = self.y + shake_offset[1]

        if self.collapsing and self.warning:
            if self.collapse_timer % 20 < 10:
                color = RED
                edge_color = DARK_RED
            else:
                color = DARK_GRAY
                edge_color = BLACK
        elif self.disappearing:
            color = (100, 120, 160)
            edge_color = (60, 80, 120)
            if self.timer > 0:
                alpha = int(255 * (1 - self.timer / DISAPPEARING_PLATFORM_TIMER))
                platform_surface = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA
                )
                platform_surface.fill((*color, alpha))
                screen.blit(platform_surface, (draw_x, draw_y))

                border_surface = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    border_surface,
                    (*edge_color, alpha),
                    (0, 0, self.width, self.height),
                    3,
                )
                screen.blit(border_surface, (draw_x, draw_y))
                return
        else:
            color = (80, 80, 90)
            edge_color = (50, 50, 60)

        pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))

        pygame.draw.rect(screen, (120, 120, 130), (draw_x, draw_y, self.width, 3))

        pygame.draw.rect(
            screen, (40, 40, 50), (draw_x, draw_y + self.height - 3, self.width, 3)
        )

        pygame.draw.rect(
            screen, edge_color, (draw_x, draw_y, self.width, self.height), 2
        )

        if not self.collapsing and not self.disappearing:
            import random

            random.seed(int(self.x + self.y))
            for i in range(2):
                crack_x = draw_x + random.randint(5, self.width - 5)
                crack_y = draw_y + random.randint(3, self.height - 3)
                pygame.draw.line(
                    screen,
                    (60, 60, 70),
                    (crack_x, crack_y),
                    (crack_x + random.randint(10, 30), crack_y + random.randint(-3, 3)),
                    1,
                )

        if self.collapsing and self.collapse_timer >= PLATFORM_COLLAPSE_WARNING:
            import random

            for _ in range(5):
                crack_x1 = draw_x + random.randint(0, int(self.width))
                crack_y1 = draw_y + random.randint(0, int(self.height))
                crack_x2 = crack_x1 + random.randint(-30, 30)
                crack_y2 = crack_y1 + random.randint(-20, 20)
                pygame.draw.line(
                    screen, BLACK, (crack_x1, crack_y1), (crack_x2, crack_y2), 2
                )
