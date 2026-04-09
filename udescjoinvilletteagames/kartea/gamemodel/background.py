from typing import TYPE_CHECKING, List

import pygame

from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.service import PlayerKarteaConfigService
from udescjoinvilletteagames.kartea.util import KarteaPathConfig

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.gamemodel import KarTEATheme


class Background:
    def __init__(self, theme: "KarTEATheme" = None):
        from udescjoinvilletteagames.kartea.gamemodel import KarTEATheme

        self.settings = GameSettings()
        self.theme = theme or KarTEATheme()
        self._pos = 0
        self._speed = 0
        self.player_x = self.settings.PLAYERX_INITIAL_VALUE
        self.player_y = self.settings.PLAYERY_INITIAL_VALUE

        # Inject assets and generate road segments
        self.service = PlayerKarteaConfigService()
        self.default_config = self.service.get_kartea_ini_config()
        self._load_assets()
        self._generate_road(self.settings.ROAD_TOTAL_SEGMENTS)

    def _load_assets(self):
        from udescjoinvilletteagames.kartea.gamemodel import Image

        # TODO: Refatorar a parte de carregamento do ini também no
        # edit colocar um campo para o lado direito e esquero do ambiente
        # hoje só tem um campo.

        """Carrega e prepara superfícies de imagem."""
        img_name = self.default_config["visual_resources"][
            "environment_image_default"
        ]

        # self.sprite_env_left = pygame.image.load(
        #    KarteaPathConfig.kartea_image(img_name)
        # ).convert_alpha()
        self.sprite_env_left = Image.load_image_resource(img_name)
        # self.sprite_env_right = pygame.image.load(
        #    KarteaPathConfig.kartea_image(img_name)
        # ).convert_alpha()
        self.sprite_env_right = self.sprite_env_left.copy()

        # Background infinito (Parallax)
        # TODO: Colocar campo para backgroud no ini e na tela de edição
        horizon_img = pygame.image.load(
            KarteaPathConfig.game_image("horizon.png")
        ).convert_alpha()
        self.bg_surface = pygame.Surface(
            (horizon_img.get_width() * 2, horizon_img.get_height())
        )
        self.bg_surface.blit(horizon_img, (0, 0))
        self.bg_surface.blit(horizon_img, (horizon_img.get_width(), 0))
        self.bg_rect = self.bg_surface.get_rect()

    def _generate_road(self, total_segments: int):
        """Inicializa a estrutura de dados da pista."""
        from udescjoinvilletteagames.kartea.gamemodel import Line

        self.lines: List[Line] = []
        for i in range(total_segments):
            line = Line()
            line.z = i * self.settings.SEGMENT_LENGTH + 0.00001

            # Lógica de cores baseada em alternância (modulo)
            is_alternate = (i // 3) % 2
            line.grass_color = self.theme.grass[
                "light" if is_alternate else "dark"
            ]
            line.rumble_color = self.theme.rumble[
                "light" if is_alternate else "dark"
            ]
            line.road_color = self.theme.road["light"]
            line.div_color = (
                self.theme.rumble["light"]
                if is_alternate
                else self.theme.road["light"]
            )

            # Decoração (Árvores)
            if i % 70 == 0:
                self._add_scenery(
                    line, -2.5, self.sprite_env_left, 1, self.sprite_env_right
                )
                # line.sprite_x = -2.5
                # line.sprite = self.sprite_env_left
                # line.sprite_2x = 1.0
                # line.sprite2 = self.sprite_env_right

            self.lines.append(line)
        self.total_lines = len(self.lines)

    def _add_scenery(self, line, x1, s1, x2, s2):
        line.sprite_x, line.sprite = x1, s1
        line.sprite_2x, line.sprite2 = x2, s2

    def set_speed_by_level(self, level: int):
        """Mapeia o nível do jogo para a velocidade da pista (Encapsulamento)."""
        speeds = {
            1: self.settings.SEGMENT_LENGTH,
            2: 2 * self.settings.SEGMENT_LENGTH,
            3: 3 * self.settings.SEGMENT_LENGTH,
        }
        self._speed = speeds.get(level, self.settings.SEGMENT_LENGTH)

    def stop(self):
        self._speed = 0

    def get_start_pos_index(self):
        """Retorna o índice da linha onde o jogador está."""
        return (self._pos // self.settings.SEGMENT_LENGTH) % self.total_lines

    def _update_position(self):
        self._pos = (self._pos + self._speed) % (
            self.total_lines * self.settings.SEGMENT_LENGTH
        )

    def draw(self, surface: pygame.Surface):
        """Método principal de renderização."""
        self._update_position()

        # 1. Desenha o fundo estático/parallax
        surface.blit(self.bg_surface, self.bg_rect)

        start_idx = self.get_start_pos_index()
        cam_h = self.player_y + self.lines[start_idx].y
        max_y = self.settings.SCREEN_HEIGHT * 2

        x_offset = dx = 0.0

        # 2. Renderização da Geometria (Frente para trás ou baixo para cima)
        for n in range(start_idx, start_idx + 300):
            curr = self.lines[n % self.total_lines]
            # Ajuste de perspectiva
            curr.project(self.player_x - x_offset, cam_h, self._pos)
            x_offset += dx
            dx += curr.curve
            curr.clip = max_y

            if curr.Y >= max_y:
                continue

            prev = self.lines[(n - 1) % self.total_lines]
            self._draw_road_segment(surface, prev, curr)

        # 3. Renderização de Sprites/Objetos (Trás para frente
        # para sobreposição correta)
        for n in range(start_idx + 300, start_idx, -1):
            line = self.lines[n % self.total_lines]
            line.draw_sprite(surface)
            line.draw_sprite2(surface)
            if line.target is not None:
                line.draw_target(surface)
                line.target.att_current_pos(line.X, line.Y)

    def _draw_road_segment(self, surface, p, c):
        """Abstração do desenho de um polígono da pista."""
        # Grama
        Background.draw_quad(
            surface,
            c.grass_color,
            0,
            p.Y,
            self.settings.SCREEN_WIDTH,
            0,
            c.Y,
            self.settings.SCREEN_WIDTH,
        )
        # Rumble (Zebra)
        Background.draw_quad(
            surface, c.rumble_color, p.X, p.Y, p.W * 1.2, c.X, c.Y, c.W * 1.2
        )
        # Pista Principal
        Background.draw_quad(
            surface, c.road_color, p.X, p.Y, p.W, c.X, c.Y, c.W
        )

        # Faixas centrais
        Background.draw_quad(
            surface, c.div_color, p.X, p.Y, p.W * 0.35, c.X, c.Y, c.W * 0.35
        )
        Background.draw_quad(
            surface, c.road_color, p.X, p.Y, p.W * 0.3, c.X, c.Y, c.W * 0.3
        )

    @staticmethod
    def draw_quad(surface, color, x1, y1, w1, x2, y2, w2):
        """
        Desenha o polígono que forma os segmentos da estrada.
        Mantemos como staticmethod pois é uma função utilitária de desenho.
        """
        pygame.draw.polygon(
            surface,
            color,
            [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)],
        )
