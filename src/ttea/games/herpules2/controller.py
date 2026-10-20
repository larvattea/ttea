"""Game loop of Herpules 2: input, events, model update and drawing.

Attributes
----------
MODO_INPUT : str
    Input mode: ``"teclado"`` (keyboard), ``"script"`` (fixed test
    sequence) or ``"mediapipe"`` (body movement seen by the camera).

Notes
-----
``MODO_INPUT`` (``"teclado"``, ``"script"`` or ``"mediapipe"``) is
defined both here and in ``view.py`` and must have the same value in
both.
"""

import pygame
from model import GameModel
from view import GameView
from input_providers import KeyboardInputProvider, ScriptedInputProvider, MediapipeInputProvider

MODO_INPUT = 'mediapipe'  # 'teclado', 'script' or 'mediapipe'


class GameController:
    """Main game controller: events, input, model, view and sounds.

    Creates the 800x600 window, the input provider of ``MODO_INPUT``,
    the model and the timers, and starts the background music.

    Attributes
    ----------
    largura, altura : int
        Window size in pixels (800 x 600).
    fps : int
        Frame rate limit (60).
    clock : pygame.time.Clock
        Clock that limits the frame rate.
    running : bool
        False ends the main loop.
    pode_iniciar : bool
        Whether a jump can start the game from the menu (mediapipe
        mode), so one jump starts it only once.
    view : GameView
        Drawing of the screens.
    input_provider : object
        Source of the jump and crouch input: a
        ``KeyboardInputProvider``, ``ScriptedInputProvider`` or
        ``MediapipeInputProvider``.
    pulo_solicitado, aga_solicitado : bool
        Jump and crouch requested by a key press in this frame.
    evento_obstaculo, evento_contagem, evento_calibracao : int
        pygame user events of the obstacle, countdown and calibration
        timers.
    tempo_spawn_obstaculo : int
        Interval between obstacle attempts, in ms (2000).
    velocidade_obstaculo : int
        Obstacle speed passed to the model: 3 in mediapipe mode, 5
        otherwise.
    model : GameModel
        Game state.
    som_pulo, som_colisao : pygame.mixer.Sound
        Jump and collision sounds.

    Notes
    -----
    Music and sounds are read from ``sons/``, relative to the current
    directory. The music loops at 40% volume.
    """

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.largura = 800
        self.altura = 600
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.running = True
        self.pode_iniciar = True

        self.view = GameView(self.largura, self.altura)

        if MODO_INPUT == "teclado":
            self.input_provider = KeyboardInputProvider()
        elif MODO_INPUT == "script":
            self.input_provider = ScriptedInputProvider()
        elif MODO_INPUT == "mediapipe":
            self.input_provider = MediapipeInputProvider()
        else:
            self.input_provider = KeyboardInputProvider()

        self.pulo_solicitado = False
        self.aga_solicitado = False

        self.evento_obstaculo = pygame.USEREVENT + 2
        self.evento_contagem = pygame.USEREVENT + 3
        self.evento_calibracao = pygame.USEREVENT + 4

        if MODO_INPUT == "mediapipe":
            self.tempo_spawn_obstaculo = 2000
            self.velocidade_obstaculo = 3
        else:
            self.tempo_spawn_obstaculo = 2000
            self.velocidade_obstaculo = 5

        self.model = GameModel(self.largura, self.altura, self.velocidade_obstaculo)
        pygame.time.set_timer(self.evento_obstaculo, self.tempo_spawn_obstaculo)

        pygame.mixer.music.load('sons/musica.mp3')
        pygame.mixer.music.play(-1)
        music_volume = 0.4
        pygame.mixer.music.set_volume(music_volume)

        self.som_pulo = pygame.mixer.Sound("sons/pulo.wav")
        self.som_colisao = pygame.mixer.Sound("sons/morte.wav")

    def processar_eventos(self):
        """Handle the pygame events of the frame.

        Notes
        -----
        Closing the window ends the loop. The obstacle timer adds an
        obstacle while playing; the countdown timer advances the
        countdown. The calibration timer (2 s after the start)
        calibrates the input provider, if it can, and starts the
        countdown.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.processar_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.processar_mouse(event)

            elif event.type == self.evento_obstaculo:
                if self.model.estado == "jogando":
                    self.model.adicionar_obstaculo()

            elif event.type == self.evento_contagem:
                self.processar_contagem()

            elif event.type == self.evento_calibracao:
                if self.model.estado == "calibracao":
                    if hasattr(self.input_provider, "calibrar"):
                        self.input_provider.calibrar()
                    self.model.iniciar_jogo()
                    pygame.time.set_timer(self.evento_calibracao, 0)
                    pygame.time.set_timer(self.evento_contagem, 1000)

    def processar_keydown(self, event):
        """Register a jump (Up) or crouch (Down) key while playing.

        Parameters
        ----------
        event : pygame.event.Event
            ``KEYDOWN`` event.
        """
        if self.model.estado == "jogando":
            if event.key == pygame.K_UP:
                self.pulo_solicitado = True
            elif event.key == pygame.K_DOWN:
                self.aga_solicitado = True

    def processar_mouse(self, event):
        """Handle clicks on the start and restart buttons.

        Parameters
        ----------
        event : pygame.event.Event
            ``MOUSEBUTTONDOWN`` event.

        Notes
        -----
        Ignored in mediapipe mode, where jumps start and restart the
        game (so the mediapipe branch inside is never reached). Start
        begins the countdown; restart resets the game to the menu.
        """
        if MODO_INPUT == "mediapipe":
            return

        if self.model.estado == "menu":
            if self.view.rect_botao_iniciar.collidepoint(event.pos):
                if MODO_INPUT == "mediapipe":
                    self.model.iniciar_calibracao()
                    pygame.time.set_timer(self.evento_calibracao, 2000)
                else:
                    self.model.iniciar_jogo()
                    pygame.time.set_timer(self.evento_contagem, 1000)

        elif self.model.estado == "game_over":
            if self.view.rect_botao_reiniciar.collidepoint(event.pos):
                self.model.resetar_jogo()
                pygame.time.set_timer(self.evento_contagem, 0)
                pygame.time.set_timer(self.evento_calibracao, 0)
                self.pulo_solicitado = False
                self.aga_solicitado = False

    def processar_contagem(self):
        """Count down one second and start playing at zero."""
        if self.model.estado == "contagem":
            self.model.contagem_numero -= 1

            if self.model.contagem_numero <= 0:
                self.model.estado = "jogando"
                pygame.time.set_timer(self.evento_contagem, 0)

    def atualizar(self):
        """Update the game for one frame with the current input.

        Notes
        -----
        Key presses of the frame are added to the provider input, and
        the jump sound plays when a jump starts on the ground. In
        mediapipe mode, a jump in the menu starts the calibration (once
        per menu visit) and a jump on the game over screen resets the
        game. A collision plays the death sound and ends the game.
        """
        input_atual = self.input_provider.get_input()

        if self.pulo_solicitado:
            input_atual.pular = True

        if input_atual.pular and self.model.estado == "jogando" and self.model.hercules.no_chao:
            self.som_pulo.play()

        if self.aga_solicitado:
            input_atual.abaixar = True

        if self.model.estado == "menu" and MODO_INPUT == "mediapipe":
            if input_atual.pular and self.pode_iniciar:
                self.model.iniciar_calibracao()
                pygame.time.set_timer(self.evento_calibracao, 2000)
                self.pode_iniciar = False

        if self.model.estado == "menu":
            self.pode_iniciar = True

        if self.model.estado == "game_over" and MODO_INPUT == "mediapipe":
            if input_atual.pular:
                self.model.resetar_jogo()

        resultado = self.model.update(input_atual)

        if resultado == "colisao":
            self.som_colisao.play()
            self.model.estado = "game_over"
            self.model.hercules.esta_correndo = False
            self.model.hercules.esta_abaixado = False
            self.model.hercules.vel_y = 0

        self.pulo_solicitado = False
        self.aga_solicitado = False

    def run(self):
        """Run the main loop until the window is closed.

        Each frame handles events, updates the game and draws it, at
        most ``fps`` times per second. At the end the input provider is
        released, if it can be, and pygame is closed.
        """
        while self.running:
            self.processar_eventos()
            self.atualizar()
            self.view.desenhar(self.model)
            self.clock.tick(self.fps)

        if hasattr(self.input_provider, "release"):
            self.input_provider.release()

        pygame.quit()
