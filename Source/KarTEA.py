# Setup Python ----------------------------------------------- #
import pygame
import sys
import os
import cv2

import arquivo
import settings
from settings import *
from game import Game
from menu import Menu

# Setup pygame/window --------------------------------------------- #
# os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 32) # windows position
pygame.init()
pygame.display.set_caption(WINDOW_NAME)
_modo = settings.modo_tela_cheia()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), _modo['flags'], display=_modo['display'])

mainClock = pygame.time.Clock()

# Fonts ----------------------------------------------------------- #
fps_font = pygame.font.SysFont("coopbl", 22)
"""
# Music ----------------------------------------------------------- #
pygame.mixer.music.load("Assets/Kartea/Sounds/Komiku_-_12_-_Bicycle.mp3")
pygame.mixer.music.set_volume(MUSIC_VOLUME)
pygame.mixer.music.play(-1)
"""


# Creation -------------------------------------------------------- #
pygame.mixer.init()
game = Game(SCREEN)
menu = Menu(SCREEN)

# Variables ------------------------------------------------------- #
state = "menu"

# Functions ------------------------------------------------------ #
def sair():
    # Encerra o KarTEA de forma limpa e devolve o controle ao menu.
    try:
        game.cap.close_camera()
    except Exception:
        pass
    pygame.display.quit()
    sys.exit()

def user_events():
    global state
    if settings.PARAR_JOGO.is_set():
        sair()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sair()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sair()
            if event.key == pygame.K_q:
                sair()
            if event.key == pygame.K_SPACE:
                state = "menu"


def update():
    global state

    if state != "game":
        # Fora do jogo (menu/pause/feedback), Game.update() nao roda, entao
        # a camera e o rastreamento dos pes precisam ser mantidos aqui para
        # que os botoes possam ser selecionados com os pes (nao so o mouse).
        # Durante o jogo, Game.update() ja cuida disso.
        game.load_camera()
        game.set_feet_position()
        game.cap.show()
    pes_pos = game.get_menu_feet_position()

    if state == "menu":
        if menu.update(pes_pos) == "game":
            state = "game"
        elif menu.update(pes_pos) == "prev":
            if arquivo.get_Nivel() != 1:
                arquivo.set_Nivel(arquivo.get_Nivel()-1)
            game.reset()  # reset the game to start a new game next level
            state = "game"
        elif menu.update(pes_pos) == "rest":
            game.reset()  # reset the game to start a new game
            state = "game"
        elif menu.update(pes_pos) == "next":
            if arquivo.get_Nivel() != 6:
                arquivo.set_Nivel(arquivo.get_Nivel()+1)
            else:
                if arquivo.get_Fase() != 3:
                    arquivo.set_Fase(arquivo.get_Fase()+1)
                    arquivo.set_Nivel(1)
            game.reset()  # reset the game to start a new game prev level
            state = "game"

    elif state == "game":
        settings.TIME_PAST += mainClock.get_time()
        if game.update() == "menu":
            state = "menu"

    pygame.display.update()



def main():
    try:
        pygame.init()
    except:
        print("Erro ao iniciar pygame")

    # Loop ------------------------------------------------------------ #
    while True:

        # Buttons ----------------------------------------------------- #
        user_events()
        # Update ------------------------------------------------------ #
        mainClock.tick(FPS)
        update()

        # FPS
        if DRAW_FPS:
            fps_label = fps_font.render(f"FPS: {int(mainClock.get_fps())}", 1, (255, 200, 20))
            SCREEN.blit(fps_label, (5, 5))

