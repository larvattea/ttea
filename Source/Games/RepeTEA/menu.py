import pygame
from button import *
from config import *


class Menu:

    def __init__(self, image):
        self.image = pygame.transform.scale(image, (WIDHT * 0.8, HEIGHT * 0.3))
        self.button_start = Button(
            (HEIGHT * 0.1, WIDHT * 0.3),
            (WIDHT * 0.5, HEIGHT * 0.5),
            TESTE,
            "Começar",
        )
        self.button_config = Button(
            (HEIGHT * 0.1, WIDHT * 0.3),
            (WIDHT * 0.5, HEIGHT * 0.65),
            TESTE,
            "Configurar",
        )
        self.button_exit = Button(
            (HEIGHT * 0.1, WIDHT * 0.3),
            (WIDHT * 0.5, HEIGHT * 0.8),
            TESTE,
            "Sair",
        )

    def draw(self, screen):
        screen.blit(self.image, (WIDHT * 0.1, HEIGHT * 0.05))
        self.button_start.draw(screen)
        self.button_config.draw(screen)
        self.button_exit.draw(screen)
