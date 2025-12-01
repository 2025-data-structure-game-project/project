import sys

import pygame

from config import *
from systems.game import Game

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Darkspire - Tower of Darkness")
clock = pygame.time.Clock()


def main():
    game = Game()
    running = True
    dt = 0
    last_time = pygame.time.get_ticks()

    frame_times = []
    max_frame_samples = 60
    fps_font = pygame.font.Font(None, 24)

    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time

        frame_times.append(dt)
        if len(frame_times) > max_frame_samples:
            frame_times.pop(0)

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game.game_state == GAME_STATE_MENU:
                result = game.handle_menu_input(event)
                if result == "quit":
                    running = False

            elif game.game_state == GAME_STATE_PLAYING:
                game.handle_game_input(event)

            elif game.game_state == GAME_STATE_DEV_MENU:
                game.handle_dev_menu_input(event)

            elif game.game_state in [GAME_STATE_VICTORY, GAME_STATE_GAME_OVER]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = Game()
                        game.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        game = Game()

        if game.game_state == GAME_STATE_PLAYING:
            game.update(keys)

        game.draw(screen)

        if SHOW_FPS and frame_times:
            avg_dt = sum(frame_times) / len(frame_times)
            fps = 1.0 / avg_dt if avg_dt > 0 else 60
            fps_text = fps_font.render(f"FPS: {int(fps)}", True, (0, 255, 0))
            screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
