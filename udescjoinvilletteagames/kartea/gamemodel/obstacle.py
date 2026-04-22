import pygame

# import settings
# from settings import *
from udescjoinvilletteagames.kartea.gamemodel import Image, Target


class Obstacle(Target):
    """Classe que representa um obstáculo no jogo. Herda de Target."""

    def __init__(self, r: int):
        """
        Inicializa um obstáculo com base na pista (r).

        Args:
            r (int): Índice da pista (0, 1 ou 2) onde o obstáculo deve aparecer.
        """
        # Define tamanho
        size = OBSTACLE_SIZES

        # Define posição inicial de spawn
        road, start_pos = self.define_spawn_pos(r)

        # Configurações do obstáculo
        self.tam = size
        self.rect = pygame.Rect(start_pos[0], start_pos[1], size[0], size[1])
        self.images = [Image.load("Assets/Kartea/Obstaculo.png", size=size)]
        self.current_frame = 0
        self.current_pos = start_pos
        self.current_road = road
        self.animation_timer = 0

    def move(self):
        """Move o obstáculo para baixo com variação lateral dependendo da pista e velocidade."""
        ve = TARGETS_MOVE_SPEED
        vel = [0, ve]

        if ve == 1:
            if self.current_pos[1] % 10 == 0:
                if self.current_road == 0:
                    vel = [-3, ve]
                elif self.current_road == 2:
                    vel = [3, ve]
            elif self.current_pos[1] % 5 == 0:
                self.rect.inflate_ip(3, 3)
                self.tam = (int(self.tam[0] + 3), int(self.tam[1] + 3))
                self.images = [
                    Image.load("Assets/Kartea/Obstaculo.png", size=self.tam)
                ]
                if self.current_road == 0:
                    vel = [-3, ve]
                elif self.current_road == 2:
                    vel = [3, ve]
            else:
                vel = [0, ve]

        elif ve == 2:
            if self.current_pos[1] % 8 == 0:
                if self.current_road == 0:
                    vel = [-2, ve]
                elif self.current_road == 2:
                    vel = [2, ve]
            elif self.current_pos[1] % 4 == 0:
                self.rect.inflate_ip(3, 3)
                self.tam = (int(self.tam[0] + 3), int(self.tam[1] + 3))
                self.images = [
                    Image.load("Assets/Kartea/Obstaculo.png", size=self.tam)
                ]
                if self.current_road == 0:
                    vel = [-2, ve]
                elif self.current_road == 2:
                    vel = [2, ve]
            else:
                vel = [0, ve]

        elif ve == 3:
            if self.current_pos[1] % 12 == 0:
                if self.current_road == 0:
                    vel = [-1, ve]
                elif self.current_road == 2:
                    vel = [1, ve]
            elif self.current_pos[1] % 6 == 0:
                self.rect.inflate_ip(3, 3)
                self.tam = (int(self.tam[0] + 3), int(self.tam[1] + 3))
                self.images = [
                    Image.load("Assets/Kartea/Obstaculo.png", size=self.tam)
                ]
                if self.current_road == 0:
                    vel = [-1, ve]
                elif self.current_road == 2:
                    vel = [1, ve]
            else:
                vel = [0, ve]

        elif ve == 4:
            if self.current_pos[1] % 16 == 0:
                if self.current_road == 0:
                    vel = [-1, ve]
                elif self.current_road == 2:
                    vel = [1, ve]
            elif self.current_pos[1] % 8 == 0:
                self.rect.inflate_ip(3, 3)
                self.tam = (int(self.tam[0] + 3), int(self.tam[1] + 3))
                self.images = [
                    Image.load("Assets/Kartea/Obstaculo.png", size=self.tam)
                ]
                if self.current_road == 0:
                    vel = [-1, ve]
                elif self.current_road == 2:
                    vel = [1, ve]
            else:
                vel = [0, ve]

        else:  # velocidade padrão
            if self.current_pos[1] % 10 == 0:
                if self.current_road == 0:
                    vel = [-3, ve]
                elif self.current_road == 2:
                    vel = [3, ve]
            else:
                self.rect.inflate_ip(3, 3)
                self.tam = (int(self.tam[0] + 3), int(self.tam[1] + 3))
                self.images = [
                    Image.load("Assets/Kartea/Obstaculo.png", size=self.tam)
                ]
                if self.current_road == 0:
                    vel = [-3, ve]
                elif self.current_road == 2:
                    vel = [3, ve]

        # Aplica o movimento
        self.rect.move_ip(vel)
        self.current_pos = (
            self.current_pos[0] + vel[0],
            self.current_pos[1] + vel[1],
        )

    def kill(
        self, surface: pygame.Surface, objects: list, sounds: dict
    ) -> int:
        """
        Remove o obstáculo da lista e retorna pontos.
        - Se saiu da tela por baixo → Desviou (10 pontos)
        - Se colidiu com o carro → Colidiu (0 pontos)
        """
        triste_fig = Image.load("Assets/Kartea/triste.png")
        feliz_fig = Image.load("Assets/Kartea/feliz.png")

        if self.current_pos[1] > SCREEN_HEIGHT:
            # Desviou do obstáculo
            objects.remove(self)
            sounds["slap"].play()
            Image.draw(surface, feliz_fig, (0, 0))
            arquivo.grava_Detalhado(
                arquivo.get_Player(),
                arquivo.get_Sessao(),
                arquivo.get_Fase(),
                arquivo.get_Nivel(),
                settings.pista,
                self.current_road,
                "Desviou de Obstaculo",
            )
            settings.Obst_d += 1
            return 10
        else:
            # Colidiu com o obstáculo
            objects.remove(self)
            sounds["screaming"].play()
            Image.draw(surface, triste_fig, (0, 0))
            arquivo.grava_Detalhado(
                arquivo.get_Player(),
                arquivo.get_Sessao(),
                arquivo.get_Fase(),
                arquivo.get_Nivel(),
                settings.pista,
                self.current_road,
                "Colidiu com Obstaculo",
            )
            settings.Obst_c += 1
            return 0
