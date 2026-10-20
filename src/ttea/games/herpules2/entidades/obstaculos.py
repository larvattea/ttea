"""Obstacles of Herpules 2."""

import random
import pygame


class Obstaculo(pygame.sprite.Sprite):
    """Obstacle that moves toward the player.

    Each obstacle picks a random image and scale and starts 200 to 300
    px beyond the right edge of the screen.

    Parameters
    ----------
    vel : int
        Speed in pixels per frame.
    largura_tela : int
        Screen width in pixels.
    altura_chao : int
        Ground level used as the bottom of the obstacle, in pixels.

    Attributes
    ----------
    image : pygame.Surface
        Scaled obstacle image.
    rect : pygame.Rect
        Obstacle position.
    mask : pygame.mask.Mask
        Collision mask.
    vel : int
        Speed in pixels per frame.
    ja_pontuou : bool
        Whether the player already scored for passing this obstacle.

    Notes
    -----
    Three images are scaled 1.5-2.2 times, the broken column 2-2.7 times
    and the others 2-2.5 times. ``hades1.png``, ``fogo1.png`` and
    ``fogão.png`` may float 85 to 95 px above the ground (to be passed
    by crouching); the others stand on the ground. The list of images
    has ``fogo1.gif``, not ``fogo1.png``, so the fire never floats.
    TODO(doc): should the check use ``fogo1.gif``?
    """

    def __init__(self, vel, largura_tela, altura_chao):
        super().__init__()

        tipos_de_obstaculos = [
            'Imagens/PeA-juntos.png',
            'Imagens/agonia.png',
            'Imagens/panico.png',
            'Imagens/Sprite-coluna-inteira.png',
            'Imagens/Sprite-coluna-quebrada.png',
            'Imagens/colunas-juntas.png',
            'Imagens/Sprite-vaso.png',
            'Imagens/hades1.png',
            'Imagens/fogo1.gif',
            'Imagens/fogão.png'
        ]

        imagem_escolhida = random.choice(tipos_de_obstaculos)
        if imagem_escolhida in ['Imagens/PeA-juntos.png',
                                'Imagens/agonia.png',
                                'Imagens/panico.png']:
            scale_factor = random.uniform(1.5, 2.2)
        elif imagem_escolhida == 'Imagens/Sprite-coluna-quebrada.png':
            scale_factor = random.uniform(2, 2.7)
        else:
            scale_factor = random.uniform(2, 2.5)

        original_image = pygame.image.load(imagem_escolhida).convert_alpha()

        new_width = int(original_image.get_width() * scale_factor)
        new_height = int(original_image.get_height() * scale_factor)
        self.image = pygame.transform.scale(original_image, (new_width, new_height))

        alturas_possiveis = [altura_chao, altura_chao - 85,
                              altura_chao - 90, altura_chao - 95]
        altura_escolhida = random.choice(alturas_possiveis)

        if imagem_escolhida in ['Imagens/hades1.png',
                                'Imagens/fogo1.png',
                                'Imagens/fogão.png']:
            self.rect = self.image.get_rect(
                bottomleft=(largura_tela + random.randint(200, 300), altura_escolhida))
        else:
            self.rect = self.image.get_rect(
                bottomleft=(largura_tela + random.randint(200, 300), altura_chao))

        self.mask = pygame.mask.from_surface(self.image)
       
        self.vel = vel

        self.ja_pontuou = False

    def update(self):
        """Move the obstacle left; remove it once off screen."""
        self.rect.x -= self.vel

        if self.rect.right < 0:
            self.kill()
