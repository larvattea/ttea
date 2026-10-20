"""Hercules, the player character of Herpules 2."""

import pygame


class Hercules(pygame.sprite.Sprite):
    """Player character: running, jumping, crouching and animation.

    Parameters
    ----------
    pos : tuple[int, int]
        Initial ``(x, y)`` of the bottom center of the sprite.

    Attributes
    ----------
    image : pygame.Surface
        Current frame.
    rect : pygame.Rect
        Position and size of the current frame.
    mask : pygame.mask.Mask
        Collision mask of the current frame (set by ``animar``).
    imagens_run : list[pygame.Surface]
        Running frames.
    imagem_pulo : pygame.Surface
        Jumping frame.
    imagem_abaixa : list[pygame.Surface]
        Crouching frames.
    imagem_morto : pygame.Surface
        Frame shown when the character dies.
    imagem_parado : pygame.Surface
        Standing frame.
    vel_x, vel_y : float
        Horizontal and vertical speed, in pixels per frame.
    gravidade : float
        Added to ``vel_y`` every frame (0.6).
    forca_pulo : int
        Initial vertical speed of a jump (-18).
    no_chao : bool
        Whether the character is on the ground.
    anim_index : float
        Position in the current animation.
    anim_speed : float
        Animation frames advanced per game frame (0.15).
    esta_correndo : bool
        Whether the character is running.
    esta_abaixado : bool
        Whether the character is crouching.

    Notes
    -----
    The frames are scaled 3 times from the standing image, but the size
    is passed as ``(height, width)`` to ``pygame.transform.scale``, so
    width and height are swapped unless the image is square. The ground
    level is fixed at y = 400 px.
    """

    def __init__(self, pos) -> None:
        super().__init__()

        self.image = pygame.image.load("Imagens/hercules-parado.png")
        altura = self.image.get_height() * 3
        largura = self.image.get_width() * 3

        self.imagens_run = [
            pygame.transform.scale(
                pygame.image.load("Imagens/hercules-correndo1.png").convert_alpha(), 
                (altura, largura)),
            pygame.transform.scale(
                pygame.image.load("Imagens/hercules-correndo2.png").convert_alpha(), 
                (altura, largura))
        ]
        self.imagem_pulo = pygame.transform.scale(
            pygame.image.load("Imagens/hercules-pulando.png").convert_alpha(), 
            (altura, largura))
        self.imagem_abaixa = [
            pygame.transform.scale(
                pygame.image.load("Imagens/hercules-abaixa1.png").convert_alpha(), (altura, largura)),
            pygame.transform.scale(
                pygame.image.load("Imagens/hercules-abaixa2.png").convert_alpha(), (altura, largura))
        ]
        self.imagem_morto = pygame.transform.scale(
            pygame.image.load("Imagens/hercules-mortinho.png").convert_alpha(), (altura, largura))
        self.imagem_parado = pygame.transform.scale(
            pygame.image.load("Imagens/hercules-parado.png").convert_alpha(), (altura, largura))

        self.image = pygame.transform.scale(self.image.convert_alpha(), (altura, largura))
        self.rect = self.image.get_rect(midbottom=pos)

        self.vel_x = 0
        self.vel_y = 0
        self.gravidade = 0.6
        self.forca_pulo = -18
        self.no_chao = True

        self.anim_index = 0
        self.anim_speed = 0.15
        self.esta_correndo = False
        self.esta_abaixado = False

    def esta_em_movimento(self):
        """Check whether the character is running, crouching or jumping.

        Returns
        -------
        bool
            True if any movement state is active.
        """
        return self.esta_correndo or self.esta_abaixado or not self.no_chao

    def aplicar_gravidade(self):
        """Apply gravity and stop the fall at y = 400 px."""
        self.vel_y += self.gravidade
        self.rect.y += self.vel_y

        if self.rect.bottom >= 400:
            self.rect.bottom = 400
            self.vel_y = 0
            self.no_chao = True

    def animar(self):
        """Pick the frame of the current state and update the mask.

        Jumping shows the jump frame; crouching and running cycle their
        frames; otherwise the standing frame is shown. The rect keeps
        its bottom and horizontal center.
        """
        if not self.no_chao:
            self.image = self.imagem_pulo
        elif self.esta_abaixado:
            self.anim_index += self.anim_speed
            if self.anim_index >= len(self.imagem_abaixa):
                self.anim_index = 0
            self.image = self.imagem_abaixa[int(self.anim_index)]
        elif self.esta_correndo:
            self.anim_index += self.anim_speed
            if self.anim_index >= len(self.imagens_run):
                self.anim_index = 0
            self.image = self.imagens_run[int(self.anim_index)]
        else:
            self.image = self.imagem_parado
        
        self.mask = pygame.mask.from_surface(self.image)
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.centerx = old_centerx

    def pular(self):
        """Start a jump if the character is on the ground."""
        if self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False

    def abaixar(self, ativo):
        """Turn crouching on or off.

        Parameters
        ----------
        ativo : bool
            True to crouch. Running is turned off while crouching and
            back on when standing up on the ground.
        """
        self.esta_abaixado = ativo
        self.esta_correndo = not ativo and self.no_chao

    def update(self):
        """Update the physics and the animation for one frame.

        The character runs automatically while on the ground and not
        crouching.
        """
        if self.no_chao and not self.esta_abaixado:
            self.esta_correndo = True

        self.aplicar_gravidade()
        self.animar()
