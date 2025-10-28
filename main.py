import pygame
import sys
from config import *
from systems.game import Game

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Darkspire - Tower of Darkness")
clock = pygame.time.Clock()


def main():
    game = Game()
    running = True

    while running:
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
                        game = Game()  # 메인 메뉴로 돌아가기

        if game.game_state == GAME_STATE_PLAYING:
            game.update(keys)

        game.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
