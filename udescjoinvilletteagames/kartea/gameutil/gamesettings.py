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

    # ====================== Desenho e Depuração ======================
    DRAW_HITBOX = False

    # ====================== Animação ======================
    ANIMATION_SPEED = 0.01

    # ====================== Dificuldade ======================
    GAME_DURATION = 30
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


# ====================== Instância Global (para compatibilidade) ======================
# Permite que o resto do código continue usando `settings.VARIAVEL` sem alterações
# settings = Settings()


# ====================== Funções Legacy (para máxima compatibilidade) ======================
# Estas funções/variáveis mantêm o código antigo funcionando sem precisar mudar imports

# WINDOW_NAME = Settings.WINDOW_NAME
# GAME_TITLE = Settings.GAME_TITLE
# CAMERA = Settings.CAMERA
# CAMERA_FLIP = Settings.CAMERA_FLIP
# SCREEN_WIDTH = Settings.SCREEN_WIDTH
# SCREEN_HEIGHT = Settings.SCREEN_HEIGHT
#
# CONTADOR = Settings.CONTADOR
# pontos_calibracao = Settings.pontos_calibracao
# div0_pista = Settings.div0_pista
# div1_pista = Settings.div1_pista
# div2_pista = Settings.div2_pista
# div3_pista = Settings.div3_pista
# pista = Settings.pista
# score = Settings.score
# movimento = Settings.movimento
# Alvo = Settings.Alvo
# Alvo_c = Settings.Alvo_c
# Alvo_d = Settings.Alvo_d
# Obst = Settings.Obst
# Obst_c = Settings.Obst_c
# Obst_d = Settings.Obst_d
#
# FPS = Settings.FPS
# DRAW_FPS = Settings.DRAW_FPS
#
# BUTTONS_SIZES = Settings.BUTTONS_SIZES
# CAR_SIZE = Settings.CAR_SIZE
# CAR_HITBOX_SIZE = Settings.CAR_HITBOX_SIZE
# TARGETS_SIZES = Settings.TARGETS_SIZES
# OBSTACLE_SIZES = Settings.OBSTACLE_SIZES
# OBJ_POS = Settings.OBJ_POS
#
# DRAW_HITBOX = Settings.DRAW_HITBOX
# ANIMATION_SPEED = Settings.ANIMATION_SPEED
# GAME_DURATION = Settings.GAME_DURATION
# TIME_PAST = Settings.TIME_PAST
# TARGETS_SPAWN_TIME = Settings.TARGETS_SPAWN_TIME
# TARGETS_MOVE_SPEED = Settings.TARGETS_MOVE_SPEED
# OBSTACLE_PENALITY = Settings.OBSTACLE_PENALITY
#
# COLORS = Settings.COLORS
# MUSIC_VOLUME = Settings.MUSIC_VOLUME
# SOUNDS_VOLUME = Settings.SOUNDS_VOLUME
# FONTS = Settings.FONTS
# MENU = Settings.MENU
#
# azul = Settings.azul
# verde = Settings.verde
# vermelho = Settings.vermelho
# amarelo = Settings.amarelo
# branco = Settings.branco
# preto = Settings.preto
#
# fonte = Settings.fonte
# font = Settings.font
#
# largura_projetor = Settings.largura_projetor
# altura_projetor = Settings.altura_projetor
# largura_tela_controle = Settings.largura_tela_controle
# altura_tela_controle = Settings.altura_tela_controle
# relacao_largura = Settings.relacao_largura
# relacao_altura = Settings.relacao_altura
# tela_de_calibracao = Settings.tela_de_calibracao
# tela_de_controle = Settings.tela_de_controle
