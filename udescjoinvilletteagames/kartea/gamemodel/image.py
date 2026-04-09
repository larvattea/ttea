import io
from typing import Tuple, Union

import pygame
from PySide6.QtCore import QFile, QIODevice

from udescjoinvilletteagames.kartea.util import KarteaPathConfig


class Image:
    """
    Classe utilitária para carregamento, escala e desenho de imagens.
    """

    IMAGE_SIZE_DEFAULT_NAME = "default"
    IMAGE_CONVERT_ALPHA = "alpha"

    IMAGE_POS_TOP_LEFT = "top_left"
    IMAGE_POS_CENTER = "center"
    IMAGE_POS_BOTTOM_CENTER = "bottom_center"

    @staticmethod
    def load(
        img_name: str,
        size: Union[str, Tuple[int, int]] = IMAGE_SIZE_DEFAULT_NAME,
        convert: str = IMAGE_CONVERT_ALPHA,
        flip: bool = False,
    ) -> pygame.Surface:
        """Carrega imagem usando o sistema de paths do projeto."""
        full_path = KarteaPathConfig.kartea_image(img_name)

        if not full_path:
            # Retorna uma superfície vazia para evitar crash se a imagem sumir
            return pygame.Surface((1, 1))

        # Verificação: Se o caminho for um recurso do Qt
        if full_path.startswith(":/"):
            file = QFile(full_path)
            if file.open(QIODevice.ReadOnly):
                img_data = file.readAll().data()
                file.close()
                # Transforma os bytes em algo que o Pygame entende
                img = pygame.image.load(io.BytesIO(img_data))
            else:
                raise FileNotFoundError(
                    f"Não foi possível abrir o recurso Qt: {full_path}"
                )
        else:
            # Caminho físico normal
            img = pygame.image.load(full_path)

        if convert == Image.IMAGE_CONVERT_ALPHA:
            img = img.convert_alpha()
        else:
            img = img.convert()

        if flip:
            img = pygame.transform.flip(img, True, False)

        if size != Image.IMAGE_SIZE_DEFAULT_NAME:
            img = Image.scale(img, size)

        return img

    @staticmethod
    def scale(img: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
        """Redimensiona com smoothscale e tamanho mínimo seguro."""
        width = max(1, int(size[0]))
        height = max(1, int(size[1]))
        return pygame.transform.smoothscale(img, (width, height))

    @staticmethod
    def draw(
        surface: pygame.Surface,
        img: pygame.Surface,
        pos: Tuple[int, int],
        pos_mode: str = IMAGE_POS_TOP_LEFT,
    ):
        """Desenha a imagem com diferentes modos de ancoragem."""
        render_pos = list(pos)

        # TODO verificar se precisa manter o IMAGE_POS_BOTTOM_CENTER
        # no código original não tinha
        if pos_mode == Image.IMAGE_POS_CENTER:
            render_pos[0] -= img.get_width() // 2
            render_pos[1] -= img.get_height() // 2
        elif pos_mode == Image.IMAGE_POS_BOTTOM_CENTER:  # new position mode
            render_pos[0] -= img.get_width() // 2
            render_pos[1] -= img.get_height()

        surface.blit(img, render_pos)

    @staticmethod
    def load_image_resource(img_name: str) -> pygame.Surface:
        resource_path = KarteaPathConfig.kartea_image(img_name)

        if resource_path.startswith(":/"):
            # É recurso Qt: carrega via memória (Alta performance)
            file = QFile(resource_path)
            if file.open(QIODevice.ReadOnly):
                img_data = file.readAll().data()
                file.close()
                byte_stream = io.BytesIO(img_data)
                # O Pygame lê os bytes e transforma em imagem
                surface = pygame.image.load(byte_stream).convert_alpha()
                return surface
        return pygame.Surface((1, 1))
