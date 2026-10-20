"""Clickable button drawn with pygame."""

import pygame


class Botao:
    """Clickable button with text drawn on a pygame surface.

    Parameters
    ----------
    x, y : int
        Center of the button, in pixels.
    texto : str
        Button text.
    fonte : pygame.font.Font
        Font used to render the text.
    cor_texto : str, optional
        Text color. Default is ``"white"``.
    cor_fundo : str, optional
        Button color. Default is ``"#4169E1"``.
    cor_hover : str, optional
        Button color under the mouse. Default is ``"#6495ED"``.

    Attributes
    ----------
    fonte : pygame.font.Font
        Font of the text.
    cor_texto : str
        Text color.
    texto_surf : pygame.Surface
        Rendered text.
    cor_fundo : str
        Button color.
    cor_hover : str
        Button color under the mouse.
    rect : pygame.Rect
        Button area: the text rect enlarged by 20 px.
    texto_rect : pygame.Rect
        Text position, centered in the button.
    clicado : bool
        Whether the left mouse button is held after a click, so one
        press counts as one click.
    """

    def __init__(self, x, y, texto, fonte, cor_texto='white', 
                 cor_fundo='#4169E1', cor_hover='#6495ED'):
        self.fonte = fonte
        self.cor_texto = cor_texto
        self.texto_surf = self.fonte.render(texto, True, self.cor_texto)

        self.cor_fundo = cor_fundo
        self.cor_hover = cor_hover
        self.rect = self.texto_surf.get_rect(center=(x, y)).inflate(20, 20) 
        self.texto_rect = self.texto_surf.get_rect(center=self.rect.center)

        self.clicado = False

    def draw(self, superficie):
        """Draw the button, with the hover color under the mouse.

        Parameters
        ----------
        superficie : pygame.Surface
            Target surface.
        """
        cor_atual = self.cor_fundo
        pos_mouse = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos_mouse):
            cor_atual = self.cor_hover

        pygame.draw.rect(superficie, cor_atual, self.rect, border_radius=12)
        superficie.blit(self.texto_surf, self.texto_rect)

    def check_click(self):
        """Check whether the button was just clicked.

        Returns
        -------
        bool
            True only on the frame the left mouse button is pressed over
            the button; holding the button does not repeat the click.
        """
        pos_mouse = pygame.mouse.get_pos()
        acao = False

        if self.rect.collidepoint(pos_mouse):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicado:
                self.clicado = True
                acao = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicado = False
        return acao
