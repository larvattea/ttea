import pygame

# Varios lugares chamam image.load() dentro do loop do jogo (ex: Menu.draw()
# recarregava um fundo do disco + redimensionava a cada frame). Cache evita
# reler/redecodificar/reescalar a mesma imagem 60x por segundo.
_cache = {}

def load(img_path, size="default", convert="alpha", flip=False):
    chave = (img_path, size, convert, flip)
    if chave in _cache:
        return _cache[chave]

    if convert == "alpha":
        img = pygame.image.load(img_path).convert_alpha()
    else:
        img = pygame.image.load(img_path).convert()

    if flip:
        img = pygame.transform.flip(img, True, False)

    if size != "default":
        img = scale(img, size)

    _cache[chave] = img
    return img


def scale(img, size):
    return pygame.transform.smoothscale(img, size)


def draw(surface, img, pos, pos_mode="top_left"):
    if pos_mode == "center":
        pos = list(pos)
        pos[0] -= img.get_width()//2
        pos[1] -= img.get_height()//2

    surface.blit(img, pos)
