import time
import pygame
from settings import *

def draw_text(surface, text, pos, color, font=FONTS["medium"], pos_mode="top_left",
                shadow=False, shadow_color=(0,0,0), shadow_offset=2):
    label = font.render(text, 1, color)
    label_rect = label.get_rect()
    if pos_mode == "top_left":
        label_rect.x, label_rect.y = pos
    elif pos_mode == "center":
        label_rect.center = pos

    if shadow: # make the shadow
        label_shadow = font.render(text, 1, shadow_color)
        surface.blit(label_shadow, (label_rect.x - shadow_offset, label_rect.y + shadow_offset))

    surface.blit(label, label_rect) # draw the text



# Tempo que o jogador precisa ficar parado em cima do botao pra selecionar
# com os pes/corpo. Sem isso, so encostar no botao ja clicava - passar por
# cima do "Sair" indo pra outro botao fechava o jogo sem querer.
TEMPO_SELECAO_PES = 1.2
_selecao_pes = {'chave': None, 'inicio': 0.0}


def desenhar_bolinha_jogador(surface, pos, raio=15):
    # Bolinha amarela mostrando onde o jogador esta na tela. Sem ela o
    # jogador nao tem como saber pra onde esta "apontando" no menu.
    if pos is None or tuple(pos) == (0, 0):
        return
    x = max(raio, min(SCREEN_WIDTH - raio, int(pos[0])))
    y = max(raio, min(SCREEN_HEIGHT - raio, int(pos[1])))
    pygame.draw.circle(surface, (255, 255, 0), (x, y), raio)


def button(surface, pos_x,  pos_y, text=None, click_sound=None, extra_pos=None):
    # extra_pos: posicao alternativa (ex: pes do jogador rastreados por
    # mediapipe) que tambem seleciona o botao, alem do mouse.
    if pos_x == 1 : #esqueda
        rect = pygame.Rect((SCREEN_WIDTH//4 - BUTTONS_SIZES[0]//2, pos_y), BUTTONS_SIZES)
    elif pos_x == 2: #direita
        rect = pygame.Rect((3*SCREEN_WIDTH//4 - BUTTONS_SIZES[0] // 2, pos_y), BUTTONS_SIZES)
    else: #meio
        rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTONS_SIZES[0] // 2, pos_y), BUTTONS_SIZES)

    feet_on_button = extra_pos is not None and rect.collidepoint(extra_pos)
    mouse_on_button = rect.collidepoint(pygame.mouse.get_pos())
    on_button = feet_on_button or mouse_on_button
    color = COLORS["buttons"]["second"] if on_button else COLORS["buttons"]["default"]

    # Selecao pelos pes: precisa PERMANECER em cima do botao. Enquanto conta,
    # o botao vai enchendo, pra o jogador ver que esta selecionando e poder
    # sair de cima antes de confirmar.
    chave = (pos_x, pos_y, text)
    progresso = 0.0
    pes_confirmou = False
    if feet_on_button:
        agora = time.time()
        if _selecao_pes['chave'] != chave:
            _selecao_pes['chave'] = chave
            _selecao_pes['inicio'] = agora
        progresso = min((agora - _selecao_pes['inicio']) / TEMPO_SELECAO_PES, 1.0)
        if progresso >= 1.0:
            pes_confirmou = True
            _selecao_pes['chave'] = None
    elif _selecao_pes['chave'] == chave:
        _selecao_pes['chave'] = None

    pygame.draw.rect(surface, COLORS["buttons"]["shadow"], (rect.x - 6, rect.y - 6, rect.w, rect.h)) # draw the shadow rectangle
    pygame.draw.rect(surface, color, rect) # draw the rectangle
    if progresso > 0:  # barra de preenchimento da selecao pelos pes
        pygame.draw.rect(surface, COLORS["buttons"]["shadow"],
                         (rect.x, rect.y, int(rect.w * progresso), rect.h))
    # draw the text
    if text is not None:
        draw_text(surface, text, rect.center, COLORS["buttons"]["text"], pos_mode="center",
                    shadow=True, shadow_color=COLORS["buttons"]["shadow"])

    if (mouse_on_button and pygame.mouse.get_pressed()[0]) or pes_confirmou:
        if click_sound is not None: # play the sound if needed
            click_sound.play()
        return True
