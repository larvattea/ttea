from typing import TYPE_CHECKING, List

import pygame

from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.service import PlayerKarteaConfigService
from udescjoinvilletteagames.kartea.util import KarteaPathConfig

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.gamemodel import Line
    from udescjoinvilletteagames.kartea.gametheme import KarTEATheme


class Background:
    def __init__(self, theme: "KarTEATheme" = None):
        from udescjoinvilletteagames.kartea.gametheme import KarTEATheme

        self.settings = GameSettings()
        self.theme = theme or KarTEATheme()
        self._pos = 0
        self._speed = 0
        self.player_x = self.settings.PLAYERX_INITIAL_VALUE
        self.player_y = self.settings.PLAYERY_INITIAL_VALUE

        self.service = PlayerKarteaConfigService()
        self.default_config = self.service.get_kartea_ini_config()

        self._load_assets()
        self._generate_road(self.settings.ROAD_TOTAL_SEGMENTS)

        # Compatibilidade com código antigo que usava clock/dt
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks() / 1000.0

    def _load_assets(self):
        from udescjoinvilletteagames.kartea.gamemodel import Image

        # TODO: Refatorar a parte de carregamento do ini também no
        # edit colocar um campo para o lado direito e esquero do ambiente
        # hoje só tem um campo.
        img_name = self.default_config["visual_resources"][
            "environment_image_default"
        ]
        self.sprite_env_left = Image.load(img_name)
        self.sprite_env_right = self.sprite_env_left.copy()

        # Background Parallax (otimizado - sem duplicar superfície em memória)
        # TODO: Colocar campo para backgroud no ini e na tela de edição
        self.bg_image = pygame.image.load(
            KarteaPathConfig.game_image("horizon.png")
        ).convert_alpha()
        self.bg_width = self.bg_image.get_width()

    def _generate_road(self, total_segments: int):
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

            if i % 70 == 0:
                self._add_scenery(
                    line,
                    -2.5,
                    self.sprite_env_left,
                    1.0,
                    self.sprite_env_right,
                )

            self.lines.append(line)

        self.total_lines = len(self.lines)

    def _add_scenery(
        self,
        line: "Line",
        x1: float,
        s1: pygame.Surface,
        x2: float,
        s2: pygame.Surface,
    ):
        line.sprite_x = x1
        line.sprite = s1
        line.sprite_2x = x2
        line.sprite2 = s2

    def set_speed_by_level(self, level: int):
        speeds = {1: 1, 2: 2, 3: 3}
        self._speed = speeds.get(level, 1) * self.settings.SEGMENT_LENGTH

    def stop(self):
        self._speed = 0

    def get_start_pos_index(self) -> int:
        return (self._pos // self.settings.SEGMENT_LENGTH) % self.total_lines

    def _update_position(self):
        self._pos = (self._pos + self._speed) % (
            self.total_lines * self.settings.SEGMENT_LENGTH
        )

    def background_menu(self):
        """Mantido para compatibilidade com o menu."""
        from udescjoinvilletteagames.kartea.gamemodel import Image

        self.image = Image.load(
            "Assets/Kartea/Background_Menu.png",
            size=(self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT),
            convert="default",
        )

    def _draw_parallax_bg(self, surface: pygame.Surface):
        """Desenha o fundo com repetição horizontal (economia de memória)."""
        surface.blit(self.bg_image, (0, 0))
        surface.blit(self.bg_image, (self.bg_width, 0))

    def draw(self, surface: pygame.Surface):
        """Renderização principal - fusão completa das duas versões."""
        self._update_position()

        # Limpeza da tela + background (mantido do original)
        surface.fill("black")
        self._draw_parallax_bg(surface)

        start_idx = self.get_start_pos_index()
        cam_h = self.player_y + self.lines[start_idx].y
        max_y = self.settings.SCREEN_HEIGHT * 2

        x_offset = dx = 0.0

        # Cache do prev_line (otimização da versão anexo)
        prev = self.lines[(start_idx - 1) % self.total_lines]

        # 1. Renderização da estrada
        for n in range(start_idx, start_idx + 300):
            curr = self.lines[n % self.total_lines]

            curr.project(self.player_x - x_offset, cam_h, self._pos)
            x_offset += dx
            dx += curr.curve
            curr.clip = max_y

            if curr.Y >= max_y:
                prev = curr
                continue

            self._draw_road_segment(surface, prev, curr)
            max_y = curr.Y
            prev = curr

        # 2. Renderização de sprites e targets (trás → frente)
        for n in range(start_idx + 300, start_idx, -1):
            line = self.lines[n % self.total_lines]

            if line.sprite is not None:
                line.draw_sprite(surface)
            if line.sprite2 is not None:
                line.draw_sprite2(surface)

            if line.target is not None:
                line.draw_target(surface)
                line.target.current_pos(line.X, line.Y)

    def _draw_road_segment(
        self, surface: pygame.Surface, p: "Line", c: "Line"
    ):
        sw = self.settings.SCREEN_WIDTH

        # Grama
        Background.draw_quad(surface, c.grass_color, 0, p.Y, sw, 0, c.Y, sw)
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
    def draw_quad(
        surface: pygame.Surface, color: pygame.Color, x1, y1, w1, x2, y2, w2
    ):
        pygame.draw.polygon(
            surface,
            color,
            [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)],
        )
