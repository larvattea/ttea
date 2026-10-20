"""Drawing of the Herpules 2 screens.

Attributes
----------
MODO_INPUT : str
    Input mode, used to choose between buttons and "jump" hints.

Notes
-----
``MODO_INPUT`` (``"teclado"``, ``"script"`` or ``"mediapipe"``) is
defined both here and in ``view.py`` and must have the same value in
both.
"""

import pygame

MODO_INPUT = 'mediapipe'  # 'teclado', 'script' or 'mediapipe'


class GameView:
    """Draw the menu, calibration, countdown, game and end screens.

    Parameters
    ----------
    largura : int
        Window width in pixels.
    altura : int
        Window height in pixels.

    Attributes
    ----------
    fonte_padrao : str, class attribute
        Font file of the texts (``fontes/8BIT.TTF``).
    tela : pygame.Surface
        The game window ("HerPULEs").
    largura, altura : int
        Window size in pixels.
    fonte_jogo, fonte_contagem, fonte_gameover : pygame.font.Font
        Fonts of 30, 100 and 80 points.
    fundo : pygame.Surface
        Background, stretched to the window, 150/255 opaque.
    imagem_menu : pygame.Surface
        Game title image, half the window size.
    botao_iniciar, botao_reiniciar : pygame.Surface
        Start and restart button images (200x100).
    rect_botao_iniciar, rect_botao_reiniciar : pygame.Rect
        Button areas, centered 70 px above the bottom.
    retangulo_tela : pygame.Rect
        Purple area under the ground (from y = 400).

    Notes
    -----
    Images and fonts are read relative to the current directory. The
    texts are fixed in Portuguese (no translation).
    """

    fonte_padrao = 'fontes/8BIT.TTF'

    def __init__(self, largura, altura):
        self.tela = pygame.display.set_mode((largura, altura))
        pygame.display.set_caption("HerPULEs")
        self.largura = largura
        self.altura = altura

        self.fonte_jogo = pygame.font.Font(self.fonte_padrao, 30)
        self.fonte_contagem = pygame.font.Font(self.fonte_padrao, 100)
        self.fonte_gameover = pygame.font.Font(self.fonte_padrao, 80)

        self.fundo = pygame.image.load('Imagens/fundonovo.png').convert()
        self.fundo = pygame.transform.scale(self.fundo, (largura, altura))
        self.fundo.set_alpha(150)

        self.imagem_menu = pygame.image.load('Imagens/herpules.png').convert_alpha()
        self.imagem_menu = pygame.transform.scale(self.imagem_menu, (largura//2, altura//2))

        self.botao_iniciar = pygame.image.load("Imagens/iniciar.png").convert_alpha()
        self.botao_iniciar = pygame.transform.scale(self.botao_iniciar, (200, 100))
        self.rect_botao_iniciar = self.botao_iniciar.get_rect(center=(largura // 2, altura - 70))

        self.botao_reiniciar = pygame.image.load("Imagens/reiniciar.png").convert_alpha()
        self.botao_reiniciar = pygame.transform.scale(self.botao_reiniciar, (200, 100))
        self.rect_botao_reiniciar = self.botao_reiniciar.get_rect(
            center=(largura // 2, altura - 70))

        self.retangulo_tela = pygame.Rect(0, 400, largura, altura/3)

    def desenhar(self, model):
        """Draw the current screen of the game.

        Parameters
        ----------
        model : GameModel
            Game state to draw.

        Notes
        -----
        In mediapipe mode, the menu and game over screens show "Pule
        para iniciar" / "Pule para reiniciar" instead of the buttons. On
        the game over screen the hero's image is set to the dead frame.
        """
        self.tela.blit(self.fundo, (0, 0))
        model.ceu.draw(self.tela)

        pygame.draw.rect(self.tela, (86, 50, 168), self.retangulo_tela)
        model.chao.draw(self.tela)

        if model.estado == 'menu':
            rect_menu = self.imagem_menu.get_rect(center=(self.largura / 2, self.altura / 3))
            self.tela.blit(self.imagem_menu, rect_menu)

            if MODO_INPUT == "mediapipe":
                texto = self.fonte_jogo.render('Pule para iniciar', True, (255, 255, 255))
                rect = texto.get_rect(center=(self.largura / 2, self.altura - 70))
                self.tela.blit(texto, rect)
            else:
                self.tela.blit(self.botao_iniciar, self.rect_botao_iniciar)

            model.grupo_jogador.draw(self.tela)

        elif model.estado == 'calibracao':
            texto = self.fonte_jogo.render("Calibrando...", True, 'black')
            rect = texto.get_rect(center=(self.largura/2, self.altura/2))
            self.tela.blit(texto, rect)

        elif model.estado == 'contagem':
            model.grupo_jogador.draw(self.tela)
            model.grupo_obstaculos.draw(self.tela)

            texto = self.fonte_contagem.render(str(model.contagem_numero), True, 'black')
            rect = texto.get_rect(center=(self.largura/2, self.altura/3))
            self.tela.blit(texto, rect)

        elif model.estado == 'jogando':
            model.grupo_jogador.draw(self.tela)
            model.grupo_obstaculos.draw(self.tela)

            texto_score = self.fonte_jogo.render(f"{model.score:05d}", True, (255, 128, 0))
            self.tela.blit(texto_score, (self.largura - texto_score.get_width() - 20, 20))

        elif model.estado == "game_over": 
            model.hercules.image = model.hercules.imagem_morto
            model.grupo_jogador.draw(self.tela)
            model.grupo_obstaculos.draw(self.tela)
  
            texto_go = self.fonte_gameover.render('GAME OVER', True, (0, 0, 0))
            rect_go = texto_go.get_rect(center=(self.largura//2, self.altura//4))
            self.tela.blit(texto_go, rect_go)

            if MODO_INPUT == "mediapipe":
                texto = self.fonte_jogo.render('Pule para reiniciar', True, (255, 255, 255))
                rect = texto.get_rect(center=(self.largura / 2, self.altura - 70))
                self.tela.blit(texto, rect)
            else:
                self.tela.blit(self.botao_reiniciar, self.rect_botao_reiniciar)

        pygame.display.flip()
