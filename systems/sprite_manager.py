from typing import Dict, List, Optional

import pygame


class Animation:
    def __init__(
        self, frames: List[pygame.Surface], frame_duration: int = 5, loop: bool = True
    ):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False

    def update(self):
        if self.finished and not self.loop:
            return

        self.frame_timer += 1
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_current_frame(self) -> pygame.Surface:
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False
