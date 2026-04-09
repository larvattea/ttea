import pygame

from udescjoinvilletteagames.kartea.gamemodel import Image
from udescjoinvilletteagames.kartea.gamemodel.target import Target
from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.service import PlayerKarteaConfigService


class Obstacle(Target):

    def __init__(self, road_index: int):
        super().__init__(road_index)
        self.settings = GameSettings()
        self.service = PlayerKarteaConfigService()
        self.default_config = self.service.get_kartea_ini_config()
        self.size = self.settings.OBSTACLE_SIZES
        self.images = [
            Image.load(
                self.default_config["visual_resources"][
                    "obstacle_image_default"
                ],
                size=self.size,
            )
        ]
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.current_pos = [0, 0]

    # TODO fazer a parte de gravação de informações da sessão
    # TODO reve a questão de som e imagens
    def kill(self, surface, objects_list, sounds, player_hit: bool = False):
        """Obstáculo: colidir = perde pontos, desviar = ganha pontos."""
        if player_hit:
            # Colidiu com obstáculo → ruim
            if sounds and "screaming" in sounds:
                sounds["screaming"].play()
            # settings.Obst_c += 1
            # arquivo.grava_Detalhado(...) 'Colidiu com Obstaculo'
            self.settings.obstacle_c += 1
            points = 0
        else:
            # Desviou do obstáculo → bom
            if sounds and "slap" in sounds:
                sounds["slap"].play()
            # settings.Obst_d += 1
            # arquivo.grava_Detalhado(...) 'Desviou de Obstaculo'
            self.settings.obstacle_d += 1
            points = 10

        if self in objects_list:
            objects_list.remove(self)
        return points
