"""Ground of Herpules 2, made of tiles that scroll in a loop."""

import pygame


class Chao(pygame.sprite.Sprite):
    """Ground made of repeated tiles that scroll to the left.

    Parameters
    ----------
    y_pos : int
        Top of the ground on the screen, in pixels.
    vel : int
        Scroll speed in pixels per frame.

    Attributes
    ----------
    image : pygame.Surface
        Ground tile (``Imagens/chao.png`` scaled to 64x64 px).
    rect : pygame.Rect
        Rect of the first tile.
    copias : list[pygame.Rect]
        Rects of the 14 tiles drawn side by side.
    vel : int
        Scroll speed in pixels per frame.
    """

    def __init__(self, y_pos, vel):
        super().__init__()

        self.image = pygame.transform.scale(
            pygame.image.load("Imagens/chao.png").convert_alpha(),(16*4,16*4))
        self.rect = self.image.get_rect(topleft=(0, y_pos))

        self.copias = []
        quant_copias = 14
        largura_img = self.image.get_width()
        for i in range(quant_copias):
            rect = self.image.get_rect(topleft=(i * largura_img, y_pos))
            self.copias.append(rect)

        self.vel = vel

    def update(self):
        """Move the tiles left, recycling those off screen."""
        for rect in self.copias:
            rect.x -= self.vel

        for rect in self.copias:
            if rect.right <= 0:
                max_right = max(r.right for r in self.copias)
                rect.x = max_right

    def draw(self, tela):
        """Draw all ground tiles.

        Parameters
        ----------
        tela : pygame.Surface
            Target surface.
        """
        for rect in self.copias:
            tela.blit(self.image, rect)
