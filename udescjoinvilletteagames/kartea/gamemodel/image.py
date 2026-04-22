import pygame


class Image:
    """Classe utilitária para carregamento, escalonamento e desenho de imagens no Pygame."""

    @staticmethod
    def load(
        img_path: str,
        size: tuple = "default",
        convert: str = "alpha",
        flip: bool = False,
    ):
        """
        Carrega uma imagem do disco.

        Args:
            img_path (str): Caminho da imagem
            size (tuple or str): Tamanho desejado (ex: (800, 600)) ou "default"
            convert (str): "alpha" para convert_alpha() ou qualquer outro valor para convert()
            flip (bool): Se True, espelha a imagem horizontalmente

        Returns:
            pygame.Surface: Imagem carregada e processada
        """
        if convert == "alpha":
            img = pygame.image.load(img_path).convert_alpha()
        else:
            img = pygame.image.load(img_path).convert()

        if flip:
            img = pygame.transform.flip(img, True, False)

        if size != "default":
            img = Image.scale(img, size)

        return img

    @staticmethod
    def scale(img: pygame.Surface, size: tuple) -> pygame.Surface:
        """
        Escala uma imagem usando smoothscale (melhor qualidade).

        Args:
            img (pygame.Surface): Imagem original
            size (tuple): Novo tamanho (largura, altura)

        Returns:
            pygame.Surface: Imagem escalada
        """
        return pygame.transform.smoothscale(img, size)

    @staticmethod
    def draw(
        surface: pygame.Surface,
        img: pygame.Surface,
        pos: tuple,
        pos_mode: str = "top_left",
    ):
        """
        Desenha uma imagem na superfície.

        Args:
            surface (pygame.Surface): Superfície onde desenhar (geralmente a tela)
            img (pygame.Surface): Imagem a ser desenhada
            pos (tuple): Posição (x, y)
            pos_mode (str): "top_left" ou "center"
        """
        if pos_mode == "center":
            # Calcula o centro da imagem
            x = pos[0] - img.get_width() // 2
            y = pos[1] - img.get_height() // 2
            draw_pos = (x, y)
        else:
            draw_pos = pos

        surface.blit(img, draw_pos)
