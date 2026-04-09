import numpy as np
import pygame

from udescjoinvilletteaapp import AppConfig


# TODO ajustar a classe para pegar as configurações de .ini
# calibração e configuração de jogo
class GameSettings:
    """Classe central de configurações do jogo KarTEA."""

    def __init__(self):
        # ==================== Configurações da Janela ====================
        self.WINDOW_NAME = AppConfig.get_title() + " - KarTEA"
        self.GAME_TITLE = self.WINDOW_NAME
        self.FPS = 60
        self.DRAW_FPS = False

        # TODO os dados da tela width e height ler do arquivo de calibração
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # ==================== Câmera ====================
        self.CAMERA = 0
        self.CAMERA_FLIP = 0
        self.CAMERA_DEPTH = 3

        # ==================== Calibração ====================
        self.calibration_points = np.zeros((4, 2), dtype=int)

        self.div0_road = 0
        self.div1_road = self.SCREEN_WIDTH // 3
        self.div2_road = 2 * (self.SCREEN_WIDTH // 3)
        self.div3_road = self.SCREEN_WIDTH

        self.road = 1  # pista atual do jogador

        # ==================== Estado do Jogo ====================
        self.score = 0
        self.move = 0
        self.target = 0
        self.target_c = 0
        self.target_d = 0
        self.obstacle = 0
        self.obstacle_c = 0
        self.obstacle_d = 0

        self.TIME_PAST = 0
        self.GAME_DURATION = 30

        # ==================== Tamanhos ====================
        self.BUTTONS_SIZES = (150, 45)
        # TODO assim como o tamanho do carro e do hitbox
        self.CAR_SIZE = int(self.SCREEN_WIDTH / 5)
        self.CAR_HITBOX_SIZE = (self.CAR_SIZE + 50, self.CAR_SIZE + 50)
        self.TARGETS_SIZES = (100, 100)
        self.OBSTACLE_SIZES = (100, 100)
        # PROJECTION_SCALE_FACTOR = 266
        self.PROJECTION_SCALE_FACTOR = int(self.SCREEN_WIDTH / 3)
        self.PERSPECTIVE_DIVISOR = 5
        self.ROAD_WIDTH = 400
        self.SEGMENT_LENGTH = 200
        self.PLAYERX_INITIAL_VALUE = 0
        self.PLAYERY_INITIAL_VALUE = 1500
        self.ROAD_TOTAL_SEGMENTS = 5000

        # ==================== Desenho e Debug ====================
        self.DRAW_HITBOX = False
        self.ANIMATION_SPEED = 0.01

        # ==================== Dificuldade ====================
        self.TARGETS_SPAWN_TIME = 8
        self.TARGETS_MOVE_SPEED = 1
        self.OBSTACLE_PENALITY = 0

        # ==================== Cores ====================
        self.COLORS = {
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

        self.blue = (0, 0, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.yellow = (255, 255, 0)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        # ==================== Fontes ====================
        pygame.font.init()
        self.FONTS = {
            "small": pygame.font.Font(None, 20),
            "medium": pygame.font.Font(None, 25),
            "big": pygame.font.Font(None, 50),
        }

        # ==================== Estado do Menu ====================
        self.MENU = "Inicial"

        # ==================== Configurações de Hardware ====================
        self.projector_width = self.SCREEN_WIDTH
        self.projector_height = self.SCREEN_HEIGHT
        self.control_screen_width = 640
        self.control_screen_height = 480

        self.width_ratio = self.projector_width / self.control_screen_width
        self.height_ratio = self.projector_height / self.control_screen_height

        # Telas OpenCV para calibração
        self.calibration_screen = np.zeros(
            (self.projector_height, self.projector_width, 3), np.uint8
        )
        self.control_screen = np.zeros(
            (self.control_screen_height, self.control_screen_width, 3),
            np.uint8,
        )

    # ====================== Métodos de Conveniência ======================
    def reset_game_state(self):
        """Reinicia as variáveis de estado do jogo."""
        self.score = 0
        self.move = 0
        self.target = self.target_c = self.target_d = 0
        self.obstacle = self.obstacle_c = self.obstacle_d = 0
        self.TIME_PAST = 0

    def update_pista_divisions(self):
        """Atualiza as divisões das pistas caso a resolução mude."""
        self.div1_road = self.SCREEN_WIDTH // 3
        self.div2_road = 2 * (self.SCREEN_WIDTH // 3)
        self.div3_road = self.SCREEN_WIDTH
