import json
import pygame
import numpy as np
import cv2
import arquivo
import ttea_log

#Variáveis do Pygame
WINDOW_NAME = "KarTEA"
GAME_TITLE = WINDOW_NAME
CAMERA = 0
CAMERA_FLIP = 0
# Indice do monitor onde os jogos abrem em tela cheia (0 = principal),
# escolhido na engrenagem do menu. Ver pygame.display.get_desktop_sizes().
MONITOR = 0

# A câmera/monitor escolhidos na engrenagem do menu ficam salvos em
# config.json, ao lado do executável. Todos os jogos leem settings.CAMERA e
# settings.MONITOR.
CONFIG_ARQUIVO = 'config.json'

def _carregar_config():
    global CAMERA, MONITOR
    try:
        with open(CONFIG_ARQUIVO, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        CAMERA = int(cfg.get('camera', CAMERA))
        MONITOR = int(cfg.get('monitor', MONITOR))
        ttea_log.debug(f'config.json carregado: camera={CAMERA} monitor={MONITOR}')
    except FileNotFoundError:
        pass
    except Exception as e:
        ttea_log.debug(f'Falha ao ler {CONFIG_ARQUIVO}: {e!r}')

def _salvar_config_chave(chave, valor):
    try:
        try:
            with open(CONFIG_ARQUIVO, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
        cfg[chave] = valor
        with open(CONFIG_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
        ttea_log.debug(f'{chave}={valor} salvo em {CONFIG_ARQUIVO}')
    except Exception as e:
        ttea_log.debug(f'Falha ao salvar {CONFIG_ARQUIVO}: {e!r}')

def salvar_camera(indice):
    global CAMERA
    CAMERA = int(indice)
    _salvar_config_chave('camera', CAMERA)

def salvar_monitor(indice):
    global MONITOR
    MONITOR = int(indice)
    _salvar_config_chave('monitor', MONITOR)

def modo_tela_cheia():
    # Flags/kwargs para abrir os jogos em tela cheia no monitor escolhido,
    # escalando o canvas logico (SCREEN_WIDTH x SCREEN_HEIGHT) para a
    # resolucao real do monitor (pygame.SCALED, disponivel no pygame 2).
    try:
        pygame.display.init()  # idempotente; get_desktop_sizes precisa do subsistema de video
        n_monitores = len(pygame.display.get_desktop_sizes())
    except Exception:
        n_monitores = 1
    display = MONITOR if 0 <= MONITOR < n_monitores else 0
    return {'flags': pygame.FULLSCREEN | pygame.SCALED, 'display': display}

def _monitores_screeninfo():
    try:
        from screeninfo import get_monitors
        return get_monitors()
    except Exception as e:
        ttea_log.debug(f'settings: falha ao listar monitores via screeninfo: {e!r}')
        return []

def janela_operador_pos():
    # (x, y) onde as janelas do operador (preview de camera/mediapipe, em
    # cv2) devem abrir: sempre no monitor OPOSTO ao escolhido para o jogo
    # (MONITOR), para nao ficar por cima da projecao. Só usa o mesmo monitor
    # se nao houver outro disponivel.
    monitores = _monitores_screeninfo()
    if not monitores:
        return (0, 0)
    indice_jogo = MONITOR if 0 <= MONITOR < len(monitores) else 0
    indice_operador = next((i for i in range(len(monitores)) if i != indice_jogo), indice_jogo)
    m = monitores[indice_operador]
    return (m.x, m.y)

_carregar_config()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


CONTADOR = 0
pontos_calibracao = np.zeros((4, 2), int)
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


FPS = 60
DRAW_FPS = False

# sizes
BUTTONS_SIZES = (150, 45)
CAR_SIZE = int(SCREEN_WIDTH/5)
CAR_HITBOX_SIZE = (CAR_SIZE+50, CAR_SIZE+50)
TARGETS_SIZES = (100, 100)
OBSTACLE_SIZES = (100, 100)

OBJ_POS = [(368, 80), (393, 80),(419, 80)]
"""
OBJ_POS_F = [(104, 600), (337, 600),(570, 600)]

264, 56, 151
0.5, 0.1, 0.3
"""

# drawing
DRAW_HITBOX = False  # will draw all the hitbox

# animation
ANIMATION_SPEED = 0.01 # the frame of the insects will change every X sec

# difficulty
GAME_DURATION = 30  # the game will last X sec
TIME_PAST = 0

TARGETS_SPAWN_TIME = 8
TARGETS_MOVE_SPEED = 1
OBSTACLE_PENALITY = 0  # will remove X of the score of the player (if he colides with a obstacle)

# colors
COLORS = {"title": (38, 61, 39), "score": (38, 61, 39),
          "timer": (38, 61, 39), "buttons": {"default": (56, 67, 209), "second":  (87, 99, 255), "text": (255, 255, 255), "shadow": (46, 54, 163)}}  # second is the color when the mouse is on the button

# sounds / music
MUSIC_VOLUME = 0  # value between 0 and 1
SOUNDS_VOLUME = 1

# fonts
pygame.font.init()
FONTS = {}
FONTS["small"] = pygame.font.Font(None, 10)
FONTS["medium"] = pygame.font.Font(None, 25)
FONTS["big"] = pygame.font.Font(None, 50)

#

MENU = 'Inicial'

#################################################################################
################################## CORES & FONTES ###############################
#################################################################################
azul = 0, 0, 255
verde = 0, 255, 0
vermelho = 255, 0, 0
amarelo = 255, 255, 0
branco = 255, 255, 255
preto = 0, 0, 0

fonte = cv2.FONT_HERSHEY_SIMPLEX
font = pygame.font.SysFont(None, 25)


#################################################################################
#################################### Hardware ###################################
#################################################################################
# Tamanho das Telas:
largura_projetor = SCREEN_WIDTH  # A ltere este valor de acordo com a resolução da projeção do jogo.
altura_projetor = SCREEN_HEIGHT  # A ltere este valor de acordo com a resolução da projeção do jogo.
largura_tela_controle = 640  # Esta tela é usada pelo terapeuta/operador. Altere o valor caso necessário.
altura_tela_controle = 480  # Esta tela é usada pelo terapeuta/operador. Altere o valor caso necessário.
relacao_largura = (largura_projetor / largura_tela_controle)  # Esta relação é usada na correção de perspectiva.
relacao_altura = (altura_projetor / altura_tela_controle)  # Esta relação é usada na correção de perspectiva.
tela_de_calibracao = np.zeros((altura_projetor, largura_projetor, 3),
                              np.uint8)  # Tela que será usada para o projetar o jogo.
tela_de_controle = np.zeros((altura_tela_controle, largura_tela_controle, 3),
                            np.uint8)  # Tela que será usada para o projetar o jogo.

