import cv2
import numpy as np
import pygame

# import arquivo


class GameSettings:
    """Classe central que contém todas as configurações do jogo KarTEA."""

    # ====================== Configurações Gerais ======================
    WINDOW_NAME = "KarTEA"
    GAME_TITLE = WINDOW_NAME
    CAMERA = 0
    CAMERA_FLIP = 0
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    FPS = 60
    DRAW_FPS = False

    CURRENT_LANG = "pt_BR"
    PLAYER_ID = 0
    PROFESSIONAL_ID = 0

    PHASE = 1
    LEVEL = 1
    LEVEL_TIME = 120

    SOUND = False
    HUD = False

    # ====================== Variáveis de Jogo ======================
    CONTADOR = 0
    pontos_calibracao = np.zeros((4, 2), dtype=int)

    div0_pista = 0
    div1_pista = SCREEN_WIDTH // 3
    div2_pista = 2 * (SCREEN_WIDTH // 3)
    div3_pista = SCREEN_WIDTH

    pista = 1
    score = 0
    movimento = 0
    Alvo = 0
    Alvo_c = 0
    Alvo_d = 0
    Obst = 0
    Obst_c = 0
    Obst_d = 0

    # ====================== Tamanhos ======================
    BUTTONS_SIZES = (150, 45)
    CAR_SIZE = int(SCREEN_WIDTH / 5)
    CAR_HITBOX_SIZE = (CAR_SIZE + 50, CAR_SIZE + 50)
    TARGETS_SIZES = (100, 100)
    OBSTACLE_SIZES = (100, 100)

    OBJ_POS = [(368, 80), (393, 80), (419, 80)]

    ROAD_WIDTH = 400
    SEGMENT_LENGTH = 200
    CAMERA_DEPTH = 3

    # ====================== Desenho e Depuração ======================
    DRAW_HITBOX = False

    # ====================== Animação ======================
    ANIMATION_SPEED = 0.01

    # ====================== Dificuldade ======================
    # GAME_DURATION = 30
    TIME_PAST = 0

    TARGETS_SPAWN_TIME = 8
    TARGETS_MOVE_SPEED = 1
    OBSTACLE_PENALITY = 0

    # ====================== Cores ======================
    COLORS = {
        "title": (38, 61, 39),
        "score": (38, 61, 39),
        "timer": (38, 61, 39),
        "buttons": {
            "default": (56, 67, 209),
            "second": (87, 99, 255),
            "text": (255, 255, 255),
            "shadow": (46, 54, 163),
        },
    }

    # ====================== Som e Música ======================
    MUSIC_VOLUME = 0
    SOUNDS_VOLUME = 1

    # ====================== Fontes ======================
    pygame.font.init()
    FONTS = {
        "small": pygame.font.Font(None, 10),
        "medium": pygame.font.Font(None, 25),
        "big": pygame.font.Font(None, 50),
    }

    # ====================== Estado do Menu ======================
    MENU = "Inicial"

    # ====================== Cores para OpenCV ======================
    azul = (0, 0, 255)
    verde = (0, 255, 0)
    vermelho = (255, 0, 0)
    amarelo = (255, 255, 0)
    branco = (255, 255, 255)
    preto = (0, 0, 0)

    fonte = cv2.FONT_HERSHEY_SIMPLEX
    font = pygame.font.SysFont(None, 25)

    # ====================== Configurações de Hardware ======================
    # Tamanhos das telas
    largura_projetor = SCREEN_WIDTH
    altura_projetor = SCREEN_HEIGHT

    largura_tela_controle = 640
    altura_tela_controle = 480

    relacao_largura = largura_projetor / largura_tela_controle
    relacao_altura = altura_projetor / altura_tela_controle

    # Telas para calibração e controle
    tela_de_calibracao = np.zeros(
        (altura_projetor, largura_projetor, 3), np.uint8
    )
    tela_de_controle = np.zeros(
        (altura_tela_controle, largura_tela_controle, 3), np.uint8
    )

    @classmethod
    def setup(cls, args, player_config, default_config):
        cls.CURRENT_LANG = args.lang
        cls.PLAYER_ID = args.player_id
        cls.PROFESSIONAL_ID = args.professional_id

        if not player_config or player_config.phase.id is None:
            cls.PHASE = int(default_config["game_settings"]["phase_default"])
        else:
            cls.PHASE = player_config.phase.id

        if not player_config or player_config.phase.id is None:
            cls.LEVEL = int(default_config["game_settings"]["level_default"])
        else:
            cls.LEVEL = player_config.level.id

        if not player_config or player_config.level_time is None:
            cls.LEVEL_TIME = int(
                default_config["game_settings"]["level_time_default"]
            )
        else:
            cls.LEVEL_TIME = player_config.level_time

        if not player_config or player_config.sound is None:
            cls.SOUND = default_config["interface_settings"]["sound_default"]
        else:
            cls.SOUND = player_config.sound

        if not player_config or player_config.hud is None:
            cls.HUD = default_config["interface_settings"]["hud_default"]
        else:
            cls.HUD = player_config.hud
