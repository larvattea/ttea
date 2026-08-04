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


_cache_alpha = {}

def carregar_alpha(caminho, tamanho=None, copia=False):
    # load + convert_alpha + scale com cache. O VesTEA reconstroi a Tela a
    # cada frame e relia essas imagens do disco toda vez (so o space.jpg
    # custava ~65 ms/frame). Usa transform.scale (nao smoothscale) pra
    # manter exatamente o mesmo resultado visual de antes.
    # copia=True para imagens que o jogo DESENHA por cima depois (as roupas
    # recebem um retangulo de destaque via pygame.draw.rect) - sem a copia o
    # destaque ficaria gravado no cache e apareceria pra sempre.
    chave = (caminho, tamanho)
    img = _cache_alpha.get(chave)
    if img is None:
        img = pygame.image.load(caminho).convert_alpha()
        if tamanho is not None:
            img = pygame.transform.scale(img, tamanho)
        _cache_alpha[chave] = img
    return img.copy() if copia else img


def scale(img, size):
    return pygame.transform.smoothscale(img, size)


def draw(surface, img, pos, pos_mode="top_left"):
    if pos_mode == "center":
        pos = list(pos)
        pos[0] -= img.get_width()//2
        pos[1] -= img.get_height()//2

    surface.blit(img, pos)
