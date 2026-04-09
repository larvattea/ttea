from typing import TYPE_CHECKING

import pygame

from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.service import PlayerKarteaConfigService

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.gamemodel import Target


class Car:
    POS_MODE = "center"

    def __init__(self):
        from udescjoinvilletteagames.kartea.gamemodel import Image

        self.settings = GameSettings()
        self.service = PlayerKarteaConfigService()
        self.default_config = self.service.get_kartea_ini_config()
        self.image = Image.load(
            self.default_config["visual_resources"]["vehicle_image_default"],
            size=(self.settings.CAR_SIZE, self.settings.CAR_SIZE),
        )
        self.rect = pygame.Rect(
            self.settings.SCREEN_WIDTH // 2,
            self.settings.SCREEN_HEIGHT // 2,
            self.settings.CAR_HITBOX_SIZE[0],
            self.settings.CAR_HITBOX_SIZE[1],
        )

    def draw(self, surface: pygame.Surface):
        from udescjoinvilletteagames.kartea.gamemodel import Image

        Image.draw(
            surface, self.image, self.rect.center, pos_mode=Car.POS_MODE
        )

        if self.settings.DRAW_HITBOX:
            pygame.draw.rect(surface, (200, 60, 0), self.rect, 2)

    def on_target(self, targets: list["Target"]):
        """Retorna lista de alvos que colidem com o carro."""
        return [t for t in targets if self.rect.colliderect(t.rect)]

    def kill_targets(
        self,
        surface: pygame.Surface,
        targets: list["Target"],
        score: int,
        sounds: dict,
    ) -> int:
        """Processa colisões quando o jogador acerta os alvos."""
        for target in self.on_target(targets):
            score += target.kill(surface, targets, sounds, player_hit=True)
        return score
