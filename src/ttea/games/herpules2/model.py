"""Game state of Herpules 2: hero, obstacles, scenery and score."""

import pygame
from entidades.hercules import Hercules
from entidades.obstaculos import Obstaculo
from entidades.ceu import Ceu
from entidades.chao import Chao


class GameModel:
    """Game state, physics and rules.

    Parameters
    ----------
    largura : int
        Screen width in pixels.
    altura : int
        Screen height in pixels.
    velocidade_obstaculo : int, optional
        Obstacle speed. Default is 5.

    Attributes
    ----------
    largura, altura : int
        Screen size in pixels.
    velocidade_obstaculo : int
        Obstacle speed given to the model.
    score : int
        Obstacles passed in the current game.
    estado : str
        Game state: ``"menu"``, ``"calibracao"``, ``"contagem"``,
        ``"jogando"`` or ``"game_over"``.
    contagem_numero : int
        Current countdown number (starts at 3).
    grupo_jogador : pygame.sprite.GroupSingle
        Group with the hero.
    hercules : Hercules
        The hero, standing at (70, 400).
    grupo_obstaculos : pygame.sprite.Group
        Obstacles on screen.
    chao : Chao
        Ground at y = 400 px, speed 3.
    ceu : Ceu
        Sky, speed 1.
    """

    def __init__(self, largura, altura, velocidade_obstaculo=5):
        self.largura = largura
        self.altura = altura
        self.velocidade_obstaculo = velocidade_obstaculo
        self.score = 0
        self.estado = 'menu'
        self.contagem_numero = 3

        self.grupo_jogador = pygame.sprite.GroupSingle()
        self.hercules = Hercules(pos=(70, 400))
        self.grupo_jogador.add(self.hercules)

        self.grupo_obstaculos = pygame.sprite.Group()
        self.chao = Chao(y_pos=400, vel=3)
        self.ceu = Ceu(vel=1, largura_tela=largura)

    def iniciar_jogo(self):
        """Start the countdown (from 3) before the game."""
        self.estado = 'contagem'
        self.contagem_numero = 3

    def iniciar_calibracao(self):
        """Enter the calibration state."""
        self.estado = 'calibracao'

    def resetar_jogo(self):
        """Reset score, obstacles and hero, and go back to the menu."""
        self.score = 0
        self.grupo_obstaculos.empty()
        self.hercules.rect.midbottom = (70, 400)
        self.hercules.vel_y = 0
        self.hercules.no_chao = True
        self.hercules.image = self.hercules.imagem_parado
        self.hercules.esta_abaixado = False
        self.hercules.esta_correndo = False
        self.hercules.anim_index = 0
        self.estado = 'menu'
        self.contagem_numero = 3

    def adicionar_obstaculo(self):
        """Add an obstacle if the last one is far enough.

        Notes
        -----
        Nothing is added while the rightmost obstacle is within 300 px
        of the right edge. New obstacles always move at speed 5:
        ``velocidade_obstaculo`` is not used. TODO(doc): should it be?
        """
        distancia_minima = 300

        if len(self.grupo_obstaculos) > 0:
            ultimo = max(self.grupo_obstaculos, key=lambda obs: obs.rect.x)

            if ultimo.rect.x > self.largura - distancia_minima:
                return

        obs = Obstaculo(vel=5, largura_tela=self.largura, altura_chao=400)
        self.grupo_obstaculos.add(obs)

    def update(self, input_state):
        """Update the game for one frame.

        Parameters
        ----------
        input_state : InputState
            Input of the frame.

        Returns
        -------
        str | None
            ``"colisao"`` when the hero hits an obstacle (pixel-perfect,
            by mask); otherwise None.

        Notes
        -----
        While playing, the hero jumps and crouches, the obstacles move
        and each obstacle that passes the hero adds one point. In the
        menu, calibration and countdown only the hero animates. The sky
        and ground scroll while the hero moves. Nothing changes on the
        game over screen.
        """
        if self.estado == "jogando":
            if input_state.pular:
                self.hercules.pular()

            self.hercules.abaixar(input_state.abaixar)

            self.grupo_jogador.update()
            self.grupo_obstaculos.update()

            for obstaculo in self.grupo_obstaculos:
                if not obstaculo.ja_pontuou and obstaculo.rect.right < self.hercules.rect.left:
                    self.score += 1
                    obstaculo.ja_pontuou = True

            if self.hercules.esta_em_movimento():
                self.ceu.update()
                self.chao.update()

            if pygame.sprite.spritecollide(
                self.hercules,
                self.grupo_obstaculos,
                False,
                pygame.sprite.collide_mask
            ):
                return "colisao"

        elif self.estado in ["menu", "calibracao", "contagem"]:
            self.grupo_jogador.update()

            if self.hercules.esta_em_movimento():
                self.ceu.update()
                self.chao.update()

        elif self.estado == "game_over":
            # Nothing is updated, so the scene stays frozen.
            pass

        return None
