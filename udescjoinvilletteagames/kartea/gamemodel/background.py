import time
from typing import List

import pygame

from udescjoinvilletteagames.kartea.gamemodel import Image, Line
from udescjoinvilletteagames.kartea.gametheme import KarTEATheme
from udescjoinvilletteagames.kartea.gameutil import GameSettings

# Constantes de cores (mantidas globais como no original)
roadW = 400  # Tamanho da pista
segL = 200  # Tamanho do segmento
camD = 3  # Camera depth

dark_grass = pygame.Color(0, 154, 0)
light_grass = pygame.Color(16, 200, 16)
dark_rumble = pygame.Color(255, 0, 0)
light_rumble = pygame.Color(255, 255, 255)
dark_road = pygame.Color(75, 75, 75)
light_road = pygame.Color(107, 107, 107)
finish_light = pygame.Color(255, 255, 255)
finish_dark = pygame.Color(0, 0, 0)


class Background:
    """Classe responsável pela renderização do fundo, estrada e sprites do jogo."""

    def __init__(self):
        self.theme = KarTEATheme()
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.time_left = time.time()
        self.dt = 0

        # Sprites laterais
        self.sprite_arv_esq = pygame.image.load(
            "Assets/Kartea/5.png"
        ).convert_alpha()
        self.sprite_arv_dir = pygame.image.load(
            "Assets/Kartea/5,1.png"
        ).convert_alpha()

        # Background image (usado no menu e no jogo)
        self.background_image = pygame.image.load(
            "Assets/Kartea/bg.png"
        ).convert_alpha()
        self.background_surface = pygame.Surface(
            (
                self.background_image.get_width() * 2,
                self.background_image.get_height(),
            )
        )
        self.background_surface.blit(self.background_image, (0, 0))
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width(), 0)
        )
        self.background_rect = self.background_surface.get_rect(topleft=(0, 0))

        # Imagem específica para o menu
        self.menu_image = None

        # Lista de linhas da estrada (pseudo-3D)
        self.lines: List[Line] = []
        self._create_road_lines()

        self.N = len(self.lines)
        self.pos = 0
        self.playerX = 0
        self.playerY = 1500

        self.speed = 0

    def _create_road_lines(self):
        """Cria as 5000 linhas que compõem a estrada (mantido exatamente como original)."""
        for i in range(5000):
            line = Line()
            line.z = i * segL + 0.00001

            grass_color = light_grass if (i // 3) % 2 else dark_grass
            rumble_color = light_rumble if (i // 3) % 2 else dark_rumble
            road_color = light_road
            div_color = light_rumble if (i // 3) % 2 else light_road

            line.grass_color = grass_color
            line.rumble_color = rumble_color
            line.road_color = road_color
            line.div_color = div_color

            # Árvores a cada 70 segmentos
            if i % 70 == 0:
                line.spriteX = -2.5
                line.sprite = self.sprite_arv_esq
                line.sprite2X = 1
                line.sprite2 = self.sprite_arv_dir

            self.lines.append(line)

    def speed1(self):
        """Velocidade lenta."""
        self.speed = segL

    def speed2(self):
        """Velocidade média."""
        self.speed = 2 * segL

    def speed3(self):
        """Velocidade rápida."""
        self.speed = 3 * segL

    def stop(self):
        """Para o movimento da estrada."""
        self.speed = 0

    def background_menu(self):
        """Carrega a imagem de fundo específica para o menu."""
        self.menu_image = Image.load(
            "Assets/Kartea/Background_Menu.png",
            size=(GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
            convert="default",
        )

    def get_startPos(self) -> int:
        """Retorna a posição inicial para spawn de alvos/obstáculos."""
        return (self.pos // segL) + 200

    def draw(self, surface: pygame.Surface):
        """Desenha o background, estrada e sprites (lógica original mantida)."""
        # Desenha o background fixo
        surface.blit(self.background_surface, self.background_rect)

        # Limpa com preto e redesenha (efeito original)
        surface.fill("black")
        surface.blit(self.background_surface, self.background_rect)

        # Atualiza posição da estrada
        self.pos += self.speed

        # Loop infinito da estrada
        while self.pos >= self.N * segL:
            self.pos -= self.N * segL
        while self.pos < 0:
            self.pos += self.N * segL

        startPos = self.pos // segL

        x = dx = 0.0
        camH = self.playerY + self.lines[startPos].y
        maxy = GameSettings.SCREEN_HEIGHT * 2

        # Renderiza os segmentos da estrada
        for n in range(startPos, startPos + 300):
            current = self.lines[n % self.N]
            current.project(
                self.playerX - x,
                camH,
                self.pos - (self.N * segL if n >= self.N else 0),
            )
            x += dx
            dx += current.curve

            current.clip = maxy

            if current.Y >= maxy:
                continue
            maxy = current.Y

            prev = self.lines[(n - 1) % self.N]

            # Desenha camadas da estrada
            self.drawQuad(
                surface,
                current.grass_color,
                0,
                prev.Y,
                GameSettings.SCREEN_WIDTH,
                0,
                current.Y,
                GameSettings.SCREEN_WIDTH,
            )
            self.drawQuad(
                surface,
                current.rumble_color,
                prev.X,
                prev.Y,
                prev.W * 1.2,
                current.X,
                current.Y,
                current.W * 1.2,
            )
            self.drawQuad(
                surface,
                current.road_color,
                prev.X,
                prev.Y,
                prev.W,
                current.X,
                current.Y,
                current.W,
            )
            self.drawQuad(
                surface,
                current.div_color,
                prev.X,
                prev.Y,
                prev.W * 0.35,
                current.X,
                current.Y,
                current.W * 0.35,
            )
            self.drawQuad(
                surface,
                current.road_color,
                prev.X,
                prev.Y,
                prev.W * 0.3,
                current.X,
                current.Y,
                current.W * 0.3,
            )

        # Desenha sprites, árvores e targets (de trás para frente)
        for n in range(startPos + 300, startPos, -1):
            line = self.lines[n % self.N]

            if line.sprite is not None:
                line.drawSprite(surface)
            if line.sprite2 is not None:
                line.drawSprite2(surface)
            if line.target is not None:
                line.drawTarget(surface)
                line.target.att_current_pos(line.target.current_pos[0], line.Y)

    def drawQuad(
        self,
        surface: pygame.Surface,
        color: pygame.Color,
        x1: int,
        y1: int,
        w1: int,
        x2: int,
        y2: int,
        w2: int,
    ):
        """Desenha um quadrilátero (trapézio) usado para renderizar a estrada."""
        pygame.draw.polygon(
            surface,
            color,
            [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)],
        )
