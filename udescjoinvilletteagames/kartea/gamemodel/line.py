from typing import TYPE_CHECKING, Optional

import pygame

from udescjoinvilletteagames.kartea.gameutil import GameSettings

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.gamemodel import Target


class Line:

    def __init__(self):
        self.settings = GameSettings()
        self.x = self.y = self.z = 0.0
        self.X = self.Y = self.W = 0.0

        self.scale = 0.0
        self.curve = 0.0
        self.clip = 0.0

        self.grass_color = self.rumble_color = self.road_color = (
            self.div_color
        ) = None

        # Sprites de Ambiente (Lado Esquerdo e Direito)
        self.sprite_x = 0.0
        self.sprite: Optional[pygame.Surface] = None
        self.sprite_2x = 0.0
        self.sprite2: Optional[pygame.Surface] = None

        # Objetivos (Targets)
        self.target_x = 0.0
        self.target: Optional["Target"] = None  # pode ser Target ou Obstacle

    def project(self, cam_x: float, cam_y: float, cam_z: float):
        """Projeta as coordenadas 3D para o plano 2D da tela."""
        self.scale = self.settings.CAMERA_DEPTH / (self.z - cam_z)
        self.X = (
            (1 + self.scale * (self.x - cam_x))
            * self.settings.SCREEN_WIDTH
            / 2
        )
        self.Y = (
            (1 - self.scale * (self.y - cam_y))
            * self.settings.SCREEN_HEIGHT
            / self.settings.PERSPECTIVE_DIVISOR
        )
        self.W = (
            self.scale
            * self.settings.ROAD_WIDTH
            * self.settings.SCREEN_WIDTH
            / 2
        )

    def draw_sprite(self, draw_surface: pygame.Surface):
        """Desenha o sprite de ambiente principal (ex: árvore esquerda)."""
        if self.sprite is None:
            return
        self._render_sprite(draw_surface, self.sprite, self.sprite_x)

    def draw_sprite2(self, draw_surface: pygame.Surface):
        """Desenha o segundo sprite de ambiente (ex: árvore direita)."""
        if self.sprite2 is None:
            return
        self._render_sprite(draw_surface, self.sprite2, self.sprite_2x)

    def _render_sprite(
        self, surface: pygame.Surface, sprite: pygame.Surface, sprite_x: float
    ):
        """Lógica interna de renderização de sprites com escala e clip."""
        w = sprite.get_width()
        h = sprite.get_height()

        dest_x = (
            self.X + self.scale * sprite_x * self.settings.SCREEN_WIDTH / 2
        )
        dest_y = self.Y + 4
        dest_w = w * self.W / self.settings.PROJECTION_SCALE_FACTOR
        dest_h = h * self.W / self.settings.PROJECTION_SCALE_FACTOR

        dest_x += dest_w * sprite_x
        dest_y += dest_h * -1

        # Clip para não desenhar abaixo da linha do horizonte ou fora da tela
        if dest_y + dest_h < self.clip or dest_w <= 0 or dest_h <= 0:
            return

        # Redimensiona o sprite conforme a distância
        scaled = pygame.transform.scale(sprite, (int(dest_w), int(dest_h)))
        surface.blit(scaled, (dest_x, dest_y))

    def draw_target(self, surface: pygame.Surface):
        """Desenha o alvo na pista e atualiza sua posição lógica."""
        if self.target is None:
            return

        # Define a posição X baseada na 'estrada' (lane) que o alvo está
        if self.target.current_road == 0:
            self.target_x = -2.25
        elif self.target.current_road == 1:
            self.target_x = -0.5
        else:
            self.target_x = 1.25

        dest_x = (
            self.X
            + self.scale * self.target_x * self.settings.SCREEN_WIDTH / 2
        )
        dest_y = self.Y + 4
        base_w = self.target.images[0].get_width()
        base_h = self.target.images[0].get_height()

        dest_w = base_w * self.W / self.settings.PROJECTION_SCALE_FACTOR
        dest_h = base_h * self.W / self.settings.PROJECTION_SCALE_FACTOR

        dest_x += dest_w * self.target_x
        dest_y += dest_h * -1

        # Atualiza a posição do objeto Target para detecção de colisão no Game.py
        self.target.define_pos(dest_x, dest_y)
        self.target.animate()

        if dest_w > 0 and dest_h > 0:
            sprite = self.target.images[self.target.current_frame]
            scaled = pygame.transform.scale(sprite, (int(dest_w), int(dest_h)))
            surface.blit(scaled, (dest_x, dest_y))

        if self.settings.DRAW_HITBOX:
            self.target.draw_debug_hitbox(surface)
