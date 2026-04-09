import pygame

from udescjoinvilletteagames.kartea.gamemodel import Image
from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.service import PlayerKarteaConfigService


class Target:
    def __init__(self, road_index: int):
        """
        Inicializa um alvo em uma das três faixas da pista.
        road_index: 0 (esquerda), 1 (centro), 2 (direita)
        """
        # Propriedades de Tamanho e Identificação
        self.settings = GameSettings()
        self.service = PlayerKarteaConfigService()

        self.default_config = self.service.get_kartea_ini_config()
        self.size = self.settings.TARGETS_SIZES
        self.current_road = road_index

        # Estado de Animação
        self.images = [
            Image.load(
                self.default_config["visual_resources"][
                    "target_image_default"
                ],
                size=self.size,
            )
        ]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Ajuste conforme necessário

        # Posição Lógica (Coordenadas de Tela calculadas pela Line)
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.current_pos = [0, 0]  # [x, y] na tela

    def animate(self):
        """Usa o animation_speed para alternar entre os frames da lista."""
        if len(self.images) > 1:
            # Incrementa o timer com base na velocidade definida
            self.animation_timer += self.animation_speed

            # Quando o timer atinge 1 (ou o limite desejado), troca o frame
            if self.animation_timer >= 1:
                self.current_frame = (self.current_frame + 1) % len(
                    self.images
                )
                self.animation_timer = 0

    def define_pos(self, x: float, y: float):
        """
        Sincroniza a posição calculada pela projeção da Line com o Rect
        de colisão. Chamado por Line.drawTarget().
        """
        self.current_pos = [int(x), int(y)]
        self.rect.topleft = (int(x), int(y))

    def att_current_pos(self, x: float, y: float):
        """Atualiza a posição lógica (usado pelo BackGround)."""
        self.current_pos = [int(x), int(y)]

    def check_collision(self, player_rect: pygame.Rect) -> bool:
        """Centraliza a lógica de colisão."""
        return self.rect.colliderect(player_rect)

    def draw_debug_hitbox(self, surface: pygame.Surface):
        """Desenha apenas o contorno da colisão para debug."""
        if self.settings.DRAW_HITBOX:  # Constante do gamesettings.py
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)

    # TODO fazer a parte de gravação de informações da sessão
    # TODO reve a questão de som e imagens
    def kill(self, surface, objects_list, sounds, player_hit: bool = False):
        """Alvo normal: colidir = ganha pontos, desviar = perde."""
        if player_hit:
            if sounds and "slap" in sounds:
                sounds["slap"].play()
            # settings.Alvo_c += 1
            # arquivo.grava_Detalhado(...) 'Colidiu com Alvo'
            self.settings.target_c += 1
            points = 10
        else:
            if sounds and "screaming" in sounds:
                sounds["screaming"].play()
            # settings.Alvo_d += 1
            # arquivo.grava_Detalhado(...) 'Desviou de Alvo'
            self.settings.target_d += 1
            points = 0

        if self in objects_list:
            objects_list.remove(self)
        return points

    # def save_session_detail
