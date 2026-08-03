
# O logging precisa ser a primeira coisa: captura erros ate dos imports.
import ttea_log
ttea_log.init()

# Precisa rodar ANTES de qualquer janela ser criada (Tk ou pygame/SDL).
# O SDL2 (usado pelo pygame) marca o processo como "DPI aware" na hora que
# abre a primeira janela em tela cheia (calibrar/jogar). Se o Tk ja tiver
# criado o menu antes disso, o Windows reescala essa janela retroativamente
# para compensar - e o menu "encolhe" sozinho. Marcando o processo como DPI
# aware aqui, antes do Tk existir, os dois ficam consistentes o tempo todo.
if __import__('sys').platform == 'win32':
    try:
        import ctypes
        try:
            # PER_MONITOR_AWARE_V2 - mesmo nivel que o SDL2 pede sozinho.
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except Exception:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
    except Exception as _e:
        ttea_log.debug(f'Falha ao marcar processo como DPI aware: {_e!r}')

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys
import threading
import arquivo
from settings import *
import cv2
import numpy as np
import settings
import pygame
import subprocess
import calibracaov2
#para inserir arquivos de outras pastas 
from sys import path
path.insert(1, '/VesTEA')

from tkinter import messagebox


def center_window_on_screen(width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cord = int((screen_width/2) - (width/2))
    y_cord = int((screen_height/2) - (height/2))
    root.geometry("{}x{}+{}+{}".format(width, height, x_cord, y_cord))

def show_menu():
    root.title('Menu TTEA')
    arr_Jogadores = ler_nome_jogadores()
    # set combo values
    jogador_cb['values'] = arr_Jogadores

    width, height = 520, 760
    center_window_on_screen(width, height)
    menu_frame.pack()
    cad_frame.forget()
    game_cb['state'] = 'readonly'
    game_cb.set('')
    jogador_cb['state'] = 'disabled'
    jogador_cb.set('')
    fase_cb['state'] = 'disabled'
    fase_cb.set('')
    nivel_cb['state'] = 'disabled'
    nivel_cb.set('')


def show_cad():
    root.title('Cadastro TTEA')
    width, height = 300, 150
    center_window_on_screen(width, height)
    cad_frame.pack()
    menu_frame.forget()

root = tk.Tk()
# Erros dentro de callbacks do tkinter vao para o debug.txt
root.report_callback_exception = ttea_log.hook_tk

# config the root window
root.resizable(False, False)
root.title('Menu TTEA')
width, height = 520, 760
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_window_on_screen(width, height)

# frames
menu_frame = tk.Frame(root)
cad_frame = tk.Frame(root)

# Menu

# Logo
image = Image.open("Assets/TTEA Logo.png")
photo = ImageTk.PhotoImage(image)
imagem = tk.Label(menu_frame, text = "TTEA Logo", image = photo)
imagem.image = photo
imagem.pack()


# Calibrar Buttons (manual + automática, lado a lado)
def CalibrarCallback():
    #import calibracao
    calibracaov2.calibrar_ttea()

def CalibrarAutomaticaCallback():
    abrir_calibracao_automatica()

calibrar_frame = tk.Frame(menu_frame)
calibrar_frame.pack(pady=(5, 10))

botao_calibrar_manual = tk.Button(calibrar_frame, text="Calibrar Manualmente", command=CalibrarCallback)
botao_calibrar_manual.pack(side=tk.LEFT, padx=8, ipadx=4, ipady=2)

botao_calibrar_auto = tk.Button(calibrar_frame, text="Calibrar Automaticamente", command=CalibrarAutomaticaCallback)
botao_calibrar_auto.pack(side=tk.LEFT, padx=8, ipadx=4, ipady=2)

# label
label = ttk.Label(menu_frame, text="Jogos:")
label.pack(fill=tk.X, padx=100, pady=5)

# create a combobox
selected_game = tk.StringVar()
game_cb = ttk.Combobox(menu_frame, textvariable=selected_game)
game = ''

# set combo values
game_cb['values'] = ['KARTEA', 'REPETEA', 'VESTEA'
]

# prevent typing a value
game_cb['state'] = 'readonly'

# place the widget
game_cb.pack(fill=tk.X, padx=100, pady=5)


# bind the selected value changes
def game_changed(event):
    global game
    game = selected_game.get()
    jogador_cb['state'] = 'readonly'

    if game == 'KARTEA':
        fase_cb['values'] = ['1', '2', '3']
        nivel_cb['values'] = ['1', '2', '3', '4', '5', '6']
    elif game == 'REPETEA':
        fase_cb['values'] = ['1', '2', '3','4','5','6','7','8','9','10']
        nivel_cb['values'] = ['1', '2', '3', '4', '5']
    elif game == 'VESTEA':
        fase_cb['values'] = ['1', '2', '3']
        nivel_cb['values'] = ['1', '2', '3', '4', '5','6','7','8','9','10', '11', '12', '13','14','15']

    if jogador_cb['values']:
        # Seleciona o primeiro jogador automaticamente, poupando um clique,
        # e ja popula fase/nivel dele (jogador_changed cuida disso).
        jogador_cb.current(0)
        jogador_changed(None)
    else:
        jogador_cb.set('')
        fase_cb['state'] = 'disabled'
        fase_cb.set('')
        nivel_cb['state'] = 'disabled'
        nivel_cb.set('')

game_cb.bind('<<ComboboxSelected>>', game_changed)


# label
label = ttk.Label(menu_frame, text="Jogador:")
label.pack(fill=tk.X, padx=100, pady=5)

# create a combobox
selected_jogador = tk.StringVar()
jogador_cb = ttk.Combobox(menu_frame, textvariable=selected_jogador)

arr_Jogadores = []

def ler_nome_jogadores():
    # Reading registered players
    path = os.getcwd() + "\Jogadores"
    Jogadores = os.listdir(path)
    #print(Jogadores)

    arr = []
    b = ''

    for a in Jogadores:
        a = a.replace('_KarTEA_sessao.csv','')
        a = a.replace('_KarTEA_config.csv','')
        a = a.replace('_KarTEA_detalhado.csv','')
        a = a.replace('_RepeTEA.csv','')
        a = a.replace('_RepeTEA_config.csv','')
        a = a.replace('_RepeTEA_detalhado.csv','')
        a = a.replace('_VesTEA_sessao.csv','')
        a = a.replace('_VesTEA_config.csv','')
        a = a.replace('_VesTEA_detalhado.csv','')
        if a != b:
            arr.append(a)
        b = a
    return arr

#print(arr_Jogadores)
arr_Jogadores = ler_nome_jogadores()
# set combo values
jogador_cb['values'] = arr_Jogadores

# prevent typing a value
jogador_cb['state'] = 'disabled'

# place the widget
jogador_cb.pack(fill=tk.X, padx=100, pady=5)


# bind the selected value changes
jogador = ''
FASE = 0
NIVEL = 0
PLAYER_ARQ_CONFIG = ''

def jogador_changed(event):
    global jogador
    jogador = selected_jogador.get()
    global PLAYER_ARQ_CONFIG
    PLAYER = "Jogadores/" + jogador
    if game == 'KARTEA':
        PLAYER_ARQ = PLAYER + "_KarTEA_sessao.csv"
        PLAYER_ARQ_CONFIG = PLAYER + "_KarTEA_config.csv"
        PLAYER_ARQ_DET = PLAYER + "_KarTEA_detalhado.csv"
    elif game == 'REPETEA':
        PLAYER_ARQ = PLAYER + "_RepeTEA_sessao.csv"
        PLAYER_ARQ_CONFIG = PLAYER + "_RepeTEA_config.csv"
        PLAYER_ARQ_DET = PLAYER + "_RepeTEA_detalhado.csv"
    elif game == 'VESTEA':
        PLAYER_ARQ = PLAYER + "_VesTEA_sessao.csv"
        PLAYER_ARQ_CONFIG = PLAYER + "_VesTEA_config.csv"
        PLAYER_ARQ_DET = PLAYER + "_VesTEA_detalhado.csv"

    global FASE, NIVEL
    FASE = arquivo.get_K_FASE(PLAYER_ARQ_CONFIG)
    NIVEL = arquivo.get_K_NIVEL(PLAYER_ARQ_CONFIG)
    fase_cb['state'] = 'readonly'
    fase_cb.current(FASE-1)
    nivel_cb['state'] = 'readonly'
    nivel_cb.current(NIVEL-1)


jogador_cb.bind('<<ComboboxSelected>>', jogador_changed)



def cadastrarCallback():
    show_cad()


botao_cadastro = tk.Button(menu_frame, text ="Cadastrar Novo Jogador", command = cadastrarCallback)
B = botao_cadastro

B.pack(fill=tk.X, padx=100, pady=10)

# label
label = ttk.Label(menu_frame, text="Fase:")
label.pack(fill=tk.X, padx=100, pady=5)

# create a combobox
selected_fase = tk.StringVar()
fase_cb = ttk.Combobox(menu_frame, textvariable=selected_fase)

# set combo values
#fase_cb['values'] = ['1', '2', '3']

# prevent typing a value
fase_cb['state'] = 'disabled'

# place the widget
fase_cb.pack(fill=tk.X, padx=100, pady=5)

# bind the selected value changes
def fase_changed(event):
    arquivo.set_K_FASE(PLAYER_ARQ_CONFIG, int(selected_fase.get()))

fase_cb.bind('<<ComboboxSelected>>', fase_changed)


# label
label = ttk.Label(menu_frame, text="Nível:")
label.pack(fill=tk.X, padx=100, pady=5)

# create a combobox
selected_nivel = tk.StringVar()
nivel_cb = ttk.Combobox(menu_frame, textvariable=selected_nivel)

# set combo values
nivel_cb['values'] = ['1', '2', '3', '4', '5', '6']

# prevent typing a value
nivel_cb['state'] = 'disabled'

# place the widget
nivel_cb.pack(fill=tk.X, padx=100, pady=5)

nivel = ''
# bind the selected value changes
def nivel_changed(event):
    arquivo.set_K_NIVEL(PLAYER_ARQ_CONFIG, int(selected_nivel.get()))

nivel_cb.bind('<<ComboboxSelected>>', nivel_changed)


jogo_thread = None

def _rodar_jogo(jogo_selecionado, jogador_selecionado):
    # Roda numa thread separada (nao a do Tk) para que o menu continue
    # respondendo - e o botao "Parar de Jogar" consiga aparecer/funcionar.
    try:
        if jogo_selecionado == 'KARTEA':
            import KarTEA
            KarTEA.main()
        elif jogo_selecionado == 'REPETEA':
            import RepeTEA
            # RepeTEA().main
        elif jogo_selecionado == 'VESTEA':
            from VesTEA import vestea_inicio
            vestea_inicio.main(jogador_selecionado)
    except SystemExit:
        # Jogo encerrado pelo usuário (tecla Q, Parar de Jogar etc.).
        pass
    except Exception as e:
        ttea_log.debug(f'Erro no jogo {jogo_selecionado}: {e!r}')
    finally:
        # O RepeTEA roda ao ser importado; tira do cache para poder jogar
        # de novo na mesma sessão (e usar a câmera escolhida na hora).
        sys.modules.pop('RepeTEA', None)
        ttea_log.debug(f'Jogo {jogo_selecionado} encerrado, de volta ao menu')

def _definir_estado_jogo_rodando(rodando):
    estado_ocioso = 'disabled' if rodando else 'normal'
    botao_jogar['state'] = estado_ocioso
    botao_cadastro['state'] = estado_ocioso
    botao_calibrar_manual['state'] = estado_ocioso
    botao_calibrar_auto['state'] = estado_ocioso
    botao_config['state'] = estado_ocioso
    game_cb['state'] = 'disabled' if rodando else 'readonly'
    jogador_cb['state'] = 'disabled' if rodando else 'readonly'
    fase_cb['state'] = 'disabled' if rodando else 'readonly'
    nivel_cb['state'] = 'disabled' if rodando else 'readonly'
    if rodando:
        botao_parar.pack(side=tk.LEFT, padx=8)
    else:
        botao_parar.pack_forget()

def _checar_fim_jogo():
    global jogo_thread
    if jogo_thread is not None and jogo_thread.is_alive():
        root.after(300, _checar_fim_jogo)
        return
    jogo_thread = None
    settings.PARAR_JOGO.clear()
    _definir_estado_jogo_rodando(False)

def JogarCallback():
    global jogo_thread
    if jogo_thread is not None and jogo_thread.is_alive():
        return  # ja tem um jogo rodando

    arquivo.set_Player(jogador)
    arquivo.set_Fase(arquivo.get_K_FASE(PLAYER_ARQ_CONFIG))
    arquivo.set_Nivel(arquivo.get_K_NIVEL(PLAYER_ARQ_CONFIG))
    print("Jogador: ", arquivo.get_Player(), " Fase: ", arquivo.get_Fase(), " Nivel: ", arquivo.get_Nivel())
    settings.pontos_calibracao = arquivo.lerCalibracao()
    x1 = settings.pontos_calibracao[2][0]
    x2 = settings.pontos_calibracao[3][0]
    print("x1= ", x1, "x2= ", x2)
    settings.div0_pista = 0
    settings.div1_pista = (SCREEN_WIDTH // 3)
    settings.div2_pista = (2*(SCREEN_WIDTH//3))
    settings.div3_pista = SCREEN_WIDTH
    print("Pontos de Calibracao: ", settings.pontos_calibracao)
    print("Div0: ", settings.div0_pista, " Div1: ", settings.div1_pista,"Div2: ", settings.div2_pista, " Div3: ", settings.div3_pista)

    TARGETS_MOVE_SPEED = arquivo.get_Nivel()

    settings.PARAR_JOGO.clear()
    _definir_estado_jogo_rodando(True)
    jogo_thread = threading.Thread(target=_rodar_jogo, args=(game, jogador), daemon=True)
    jogo_thread.start()
    root.after(300, _checar_fim_jogo)

def PararJogarCallback():
    settings.PARAR_JOGO.set()


jogar_frame = tk.Frame(menu_frame)
jogar_frame.pack(pady=(10, 5))

botao_jogar = tk.Button(jogar_frame, text="Jogar", command=JogarCallback)
botao_jogar.pack(side=tk.LEFT, padx=8, ipadx=4, ipady=2)

botao_parar = tk.Button(jogar_frame, text="Parar de Jogar", command=PararJogarCallback, fg='red')
# So aparece (via pack) enquanto um jogo estiver rodando - ver _definir_estado_jogo_rodando.

# Teste-Logo UDESC
imageUdesc = Image.open("Assets/Logos UDESC Larva.png")
photoUdesc = ImageTk.PhotoImage(imageUdesc)
imagemUdesc = tk.Label(menu_frame, text = "Logo Udesc", image = photoUdesc)
imagemUdesc.imageUdesc = photoUdesc
imagemUdesc.pack(pady=10)

menu_frame.pack()

# Configurações (engrenagem no canto superior direito) -------------------------
def detectar_cameras():
    # Testa os indices de camera e devolve [(indice, largura, altura), ...]
    ttea_log.debug('Config: procurando cameras...')
    encontradas = []
    falhas_seguidas = 0
    for i in range(10):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            largura = altura = 0
            ret, frame = cap.read()
            if ret and frame is not None:
                altura, largura = frame.shape[:2]
            encontradas.append((i, largura, altura))
            falhas_seguidas = 0
            ttea_log.debug(f'Config: camera {i} disponivel ({largura}x{altura})')
        else:
            falhas_seguidas += 1
            ttea_log.debug(f'Config: camera {i} indisponivel')
        cap.release()
        if falhas_seguidas >= 2:
            break
    return encontradas

def detectar_monitores():
    # Devolve [(largura, altura), ...] na ordem usada por settings.MONITOR /
    # pygame display=<indice>.
    try:
        pygame.display.init()
        return pygame.display.get_desktop_sizes()
    except Exception as e:
        ttea_log.debug(f'Config: falha ao listar monitores: {e!r}')
        return [(SCREEN_WIDTH, SCREEN_HEIGHT)]

def abrir_calibracao_automatica():
    # auto_calibracao_espelho.py fica na raiz do projeto (um nível acima de
    # Source/); em execução a partir do código-fonte, garante que ela esteja
    # no sys.path. No build compilado, T-TEA.spec já a inclui no pacote.
    raiz_projeto = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    if raiz_projeto not in sys.path:
        sys.path.insert(0, raiz_projeto)
    try:
        import auto_calibracao_espelho
        auto_calibracao_espelho.executar()
    except Exception as e:
        ttea_log.debug(f'Config: falha ao rodar calibracao automatica: {e!r}')
        messagebox.showerror('Calibração automática', f'Não foi possível rodar a ferramenta: {e}')

def abrir_configuracoes():
    win = tk.Toplevel(root)
    win.title('Configurações')
    win.resizable(False, False)
    win.grab_set()
    win.geometry('+{}+{}'.format(root.winfo_x() + 40, root.winfo_y() + 40))

    frame = tk.Frame(win, padx=15, pady=15)
    frame.pack()

    ttk.Label(frame, text='Câmera:').grid(column=0, row=0, sticky=tk.W)
    cam_cb = ttk.Combobox(frame, state='readonly', width=24)
    cam_cb.grid(column=1, row=0, padx=10)
    aviso = ttk.Label(frame, text='Procurando câmeras...')
    aviso.grid(column=0, row=1, columnspan=2, pady=5)

    # Preview ao vivo da câmera selecionada, com o esqueleto do mediapipe
    # desenhado por cima (mesmo desenho usado dentro dos jogos).
    # Um Label sem imagem mede width/height em "unidades de texto" (~px por
    # caractere da fonte), nao em pixels - por isso o placeholder ficava
    # enorme antes do primeiro frame chegar. Da um PhotoImage preto de
    # verdade logo de cara para o tamanho ficar certo (640x480) desde o
    # início.
    PREVIEW_W, PREVIEW_H = 640, 480
    _preview_placeholder = ImageTk.PhotoImage(Image.new('RGB', (PREVIEW_W, PREVIEW_H), 'black'))
    preview_label = tk.Label(frame, image=_preview_placeholder, bg='black')
    preview_label.image = _preview_placeholder
    preview_label.grid(column=0, row=2, columnspan=2, pady=5)

    ttk.Label(frame, text='Tela (monitor):').grid(column=0, row=3, sticky=tk.W, pady=(10, 0))
    tela_cb = ttk.Combobox(frame, state='readonly', width=24)
    tela_cb.grid(column=1, row=3, padx=10, pady=(10, 0))

    win.update()

    cameras = detectar_cameras()
    if cameras:
        cam_cb['values'] = [
            'Câmera {} ({}x{})'.format(i, w, h) if w else 'Câmera {}'.format(i)
            for i, w, h in cameras
        ]
        indices = [i for i, w, h in cameras]
        cam_cb.current(indices.index(settings.CAMERA) if settings.CAMERA in indices else 0)
        aviso['text'] = '{} câmera(s) encontrada(s). Em uso: câmera {}'.format(len(cameras), settings.CAMERA)
    else:
        aviso['text'] = 'Nenhuma câmera encontrada!'

    monitores = detectar_monitores()
    tela_cb['values'] = [
        'Monitor {} ({}x{})'.format(i + 1, w, h) for i, (w, h) in enumerate(monitores)
    ]
    tela_cb.current(settings.MONITOR if 0 <= settings.MONITOR < len(monitores) else 0)

    # --- Preview da câmera (mediapipe pose) ---------------------------------
    import mediapipe as mp
    _preview_pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0)
    estado_preview = {'cap': None, 'indice': None, 'foto': None, 'agendado': None, 'ativo': True}

    def _preview_trocar_camera():
        if not cameras:
            return
        indice = cameras[cam_cb.current()][0]
        if indice == estado_preview['indice']:
            return
        if estado_preview['cap'] is not None:
            estado_preview['cap'].release()
        estado_preview['indice'] = indice
        estado_preview['cap'] = settings.abrir_camera(indice)

    def _preview_tick():
        if not estado_preview['ativo']:
            return
        _preview_trocar_camera()
        cap = estado_preview['cap']
        if cap is not None and cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resultados = _preview_pose.process(rgb)
                if resultados.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        rgb, resultados.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style())
                img = Image.fromarray(rgb).resize((PREVIEW_W, PREVIEW_H))
                estado_preview['foto'] = ImageTk.PhotoImage(img)
                preview_label.configure(image=estado_preview['foto'])
        estado_preview['agendado'] = win.after(100, _preview_tick)

    cam_cb.bind('<<ComboboxSelected>>', lambda e: _preview_trocar_camera())
    if cameras:
        _preview_tick()

    def _fechar_preview():
        estado_preview['ativo'] = False
        if estado_preview['agendado'] is not None:
            win.after_cancel(estado_preview['agendado'])
        if estado_preview['cap'] is not None:
            estado_preview['cap'].release()
        try:
            _preview_pose.close()
        except Exception:
            pass

    def salvar():
        _fechar_preview()
        if cameras:
            settings.salvar_camera(cameras[cam_cb.current()][0])
        settings.salvar_monitor(tela_cb.current())
        win.destroy()

    def cancelar():
        _fechar_preview()
        win.destroy()

    tk.Button(frame, text='Salvar', width=10, command=salvar).grid(column=0, row=4, pady=10)
    tk.Button(frame, text='Cancelar', width=10, command=cancelar).grid(column=1, row=4, pady=10)

    win.protocol('WM_DELETE_WINDOW', cancelar)

botao_config = tk.Button(root, text='⚙', font=('Segoe UI Symbol', 13),
                         relief='flat', cursor='hand2', command=abrir_configuracoes)
botao_config.place(relx=1.0, x=-4, y=4, anchor='ne')

#Frame Cadastro
arr_Jogadores = ler_nome_jogadores()

NomeString = tk.StringVar(cad_frame)
DataString = tk.StringVar(cad_frame)
ObsString = tk.StringVar(cad_frame)

LNome = tk.Label(cad_frame, text="Nome: ")
LNome.grid(column=0, row=0, sticky=tk.W)
Nome = tk.Entry(cad_frame, width=20, textvariable=NomeString)
Nome.grid(column=1, row=0, padx=10)

LData = tk.Label(cad_frame, text="Data de Nasc.: ")
LData.grid(column=0, row=1, sticky=tk.W)
Data = tk.Entry(cad_frame, width=20, textvariable=DataString)
Data.grid(column=1, row=1, padx=10)

LObs = tk.Label(cad_frame, text="Observação: ")
LObs.grid(column=0, row=2, sticky=tk.W)
Obs = tk.Entry(cad_frame, width=20, textvariable=ObsString)
Obs.grid(column=1, row=2, padx=10)

def cadastrarcallback():
    SNome = NomeString.get()
    SData = DataString.get()
    SObs = ObsString.get()
    #print(SNome, SData, SObs)


    if SNome not in arr_Jogadores:
        arquivo.CadastrarJogador(SNome, SData, SObs)
        arr_Jogadores.append(SNome)
        res = tk.messagebox.askquestion (title='Jogador cadastrado!', message='Jogador cadastrado com sucesso!\nDeseja cadastrar outro jogador?')
        if res == 'no':
            show_menu()
    else:
        tk.messagebox.showerror(title='Erro!', message='Jogador com esse nome já esta cadastrado!')

B = tk.Button(cad_frame, text="Cadastrar Novo Jogador", command=cadastrarcallback)

B.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

def cancelarcallback():
    show_menu()

B = tk.Button(cad_frame, text="Cancelar", command=cancelarcallback)

B.grid(column=1, row=3, padx=10, pady=10, sticky=tk.W)

root.mainloop()