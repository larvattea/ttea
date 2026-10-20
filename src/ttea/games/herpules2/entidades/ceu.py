"""Sky background of Herpules 2 with moving clouds."""

import random
import pygame


class Ceu:
    """Sky background with clouds that scroll to the left.

    Creates seven clouds of random size, spacing and height and moves
    them left; a cloud that leaves the screen is placed again after the
    rightmost one, with a new size and height.

    Parameters
    ----------
    vel : int
        Scroll speed in pixels per frame.
    largura_tela : int
        Screen width in pixels.

    Attributes
    ----------
    nuvens_data : list[dict]
        Clouds, each with ``"image"`` (scaled surface), ``"rect"`` and
        ``"alpha"``.
    vel : int
        Scroll speed in pixels per frame.
    largura_tela : int
        Screen width in pixels.

    Notes
    -----
    Clouds are scaled 3 to 6 times, placed at y 0-90 and spaced 150 to
    400 px apart. Bigger clouds are more transparent: the alpha is ``255
    - 23 * scale`` when created and ``255 - 15 * scale`` when a cloud is
    recycled. The image is read from ``Imagens/nuvem.png``, relative to
    the current directory, and reloaded on every recycle.
    """

    def __init__(self, vel, largura_tela):
        original_nuvem_image = pygame.image.load("Imagens/nuvem.png").convert_alpha()
        self.nuvens_data = []
        num_nuvens = 7
        current_x = 0

        for _ in range(num_nuvens):
            scale_factor = random.uniform(3, 6)
            scaled_width = int(original_nuvem_image.get_width() * scale_factor)
            scaled_height = int(original_nuvem_image.get_height() * scale_factor)
            scaled_image = pygame.transform.scale(original_nuvem_image,
                                                  (scaled_width, scaled_height))

            alpha_value = max(0, 255 - (scale_factor * 23))
            scaled_image.set_alpha(alpha_value)

            pos_x = current_x
            pos_y = random.randint(0, 90)
            rect = scaled_image.get_rect(topleft=(pos_x, pos_y))

            self.nuvens_data.append({'image': scaled_image, 'rect': rect, 'alpha': alpha_value})

            spacing = random.randint(150, 400)
            current_x = rect.right + spacing

        self.vel = vel
        self.largura_tela = largura_tela

    def update(self):
        """Move the clouds left and recycle those off screen."""
        for nuvem in self.nuvens_data:
            nuvem['rect'].x -= self.vel

        for nuvem in self.nuvens_data:
            if nuvem['rect'].right <= 0:
                max_right = max(n['rect'].right for n in self.nuvens_data)
                spacing = random.randint(150, 400)
                nuvem['rect'].x = max_right + spacing

                scale_factor = random.uniform(3, 6)
                original_nuvem_image = pygame.image.load("Imagens/nuvem.png").convert_alpha()
                scaled_width = int(original_nuvem_image.get_width() * scale_factor)
                scaled_height = int(original_nuvem_image.get_height() * scale_factor)
                nuvem['image'] = pygame.transform.scale(original_nuvem_image,
                                                        (scaled_width, scaled_height))
 
                alpha_value = max(0, 255 - (scale_factor * 15))
                nuvem['image'].set_alpha(alpha_value)
                nuvem['rect'].y = random.randint(0, 90)

    def draw(self, tela):
        """Draw all clouds.

        Parameters
        ----------
        tela : pygame.Surface
            Target surface.
        """
        for nuvem in self.nuvens_data:
            tela.blit(nuvem['image'], nuvem['rect'])
