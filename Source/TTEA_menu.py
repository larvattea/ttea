import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import arquivo
from settings import *
import cv2
import numpy as np
import settings
import pygame
import subprocess

from tkinter import messagebox

#centraliza uma janela de acordo com a resolução da tela 
def center_window_on_screen(width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cord = int((screen_width/2) - (width/2))
    y_cord = int((screen_height/2) - (height/2))
    root.geometry("{}x{}+{}+{}".format(width, height, x_cord, y_cord))

#exibe menu do TTEA
def show_menu():
    root.title('Menu TTEA')
    arr_Jogadores = ler_nome_jogadores()
    jogador_cb['values'] = arr_Jogadores

    width, height = 400, 600
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

#exibe janela de cadastro
def show_cad():
    root.title('Cadastro TTEA')
    width, height = 300, 150
    center_window_on_screen(width, height)
    cad_frame.pack()
    menu_frame.forget()

# Calibrar Button
def CalibrarCallback():
    import calibracao
    
# redefine demais combobox caso usuário mude de jogo
def game_changed(event):
    global game
    game = selected_game.get()
    jogador_cb['state'] = 'readonly'
    jogador_cb.set('')
    if game == 'KARTEA':
        fase_cb['values'] = ['1', '2', '3']
        nivel_cb['values'] = ['1', '2', '3', '4', '5', '6']
    else:
        fase_cb['values'] = ['1', '2', '3','4','5','6','7','8','9','10']
        nivel_cb['values'] = ['1', '2', '3', '4', '5']

    fase_cb['state'] = 'disabled'
    fase_cb.set('')
    nivel_cb['state'] = 'disabled'
    nivel_cb.set('')
    

# busca nomes dos jogadores na lista de arquivos da pasta jogadores
def ler_nome_jogadores():
    # Reading registered players
    path = os.getcwd() + "\Jogadores"
    Jogadores = os.listdir(path)

    arr = []
    b = ''

    for a in Jogadores:
        a = a.replace('_KarTEA_sessao.csv','')
        a = a.replace('_KarTEA_config.csv','')
        a = a.replace('_KarTEA_detalhado.csv','')
        a = a.replace('_RepeTEA.csv','')
        a = a.replace('_RepeTEA_config.csv','')
        a = a.replace('_RepeTEA_detalhado.csv','')
        if a != b:
            arr.append(a)
        b = a
    return arr

#função que altera valores das variáveis do jogador
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

    global FASE, NIVEL
    FASE = arquivo.get_K_FASE(PLAYER_ARQ_CONFIG)
    NIVEL = arquivo.get_K_NIVEL(PLAYER_ARQ_CONFIG)
    fase_cb['state'] = 'readonly'
    fase_cb.current(FASE-1)
    nivel_cb['state'] = 'readonly'
    nivel_cb.current(NIVEL-1)

#cria funcao que mostra janela de cadastro (!)
def cadastrarCallback():
    show_cad()

# salva nova escolha de fase no arquivo (! - ERRO - se só por mudar já salva no arquivo, terapeuta pode perder fase atual real)
def fase_changed(event):
    arquivo.set_K_FASE(PLAYER_ARQ_CONFIG, int(selected_fase.get()))

# salva nova escolha de nivel no arquivo (! - ERRO - se só por mudar já salva no arquivo, terapeuta pode perder fase atual real)
def nivel_changed(event):
    arquivo.set_K_NIVEL(PLAYER_ARQ_CONFIG, int(selected_nivel.get()))

#função que seta os parâmetros e inicia o jogo selecionado
def JogarCallback():
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

    if game == 'KARTEA':
        import KarTEA
        KarTEA.main()
    else:
        import RepeTEA
        # RepeTEA().main

#função que cadastra jogador e cria seus respectivos arquivos (! - ERRO - mesmo nome da função que abre a janela de cadastro)
def cadastrarcallback():
    SNome = NomeString.get()
    SData = DataString.get()
    SObs = ObsString.get()

    if SNome not in arr_Jogadores:
        arquivo.CadastrarJogador(SNome, SData, SObs)
        arr_Jogadores.append(SNome)
        res = tk.messagebox.askquestion (title='Jogador cadastrado!', message='Jogador cadastrado com sucesso!\nDeseja cadastrar outro jogador?')
        if res == 'no':
            show_menu()
    else:
        tk.messagebox.showerror(title='Erro!', message='Jogador com esse nome já esta cadastrado!')

# função que reabre menu principal ao clicar em cancelar
def cancelarcallback():
    show_menu()

#cria raiz do Tkinter que criará a janela
root = tk.Tk()

# configura a janela do menu principal (!)
root.resizable(False, False)

root.title('Menu TTEA')
width, height = 400, 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_window_on_screen(width, height)

# frames para colocar conteúdos das janelas
menu_frame = tk.Frame(root)
cad_frame = tk.Frame(root)

# Menu

# Coloca a Logo no frame do menu principal (!)
image = Image.open("Assets/TTEA Logo.png")
photo = ImageTk.PhotoImage(image)
imagem = tk.Label(menu_frame, text = "TTEA Logo", image = photo)
imagem.image = photo
imagem.pack()




#Coloca botão de calibração no frame do menu principal (!)
B = tk.Button(menu_frame, text ="Calibrar", command = CalibrarCallback)
B.pack()

# label de texto para menu principal (!)
label = ttk.Label(menu_frame, text="Jogos:")
label.pack(fill=tk.X, padx=100, pady=5)

# cria a combobox de jogos para o menu principal (!)
selected_game = tk.StringVar()
game_cb = ttk.Combobox(menu_frame, textvariable=selected_game)
game = ''
# define opções de jogos e coloca no modo leitura para o menu principal (!)
game_cb['values'] = ['KARTEA', 'REPETEA']
game_cb['state'] = 'readonly'
game_cb.pack(fill=tk.X, padx=100, pady=5)


#vincula o evento de alterar da combobox de jogo com a função game_changed (!)
game_cb.bind('<<ComboboxSelected>>', game_changed)

# label de texto para o menu principal (!)
label = ttk.Label(menu_frame, text="Jogador:")
label.pack(fill=tk.X, padx=100, pady=5)

# cria combobox para escolha do jogador para o menu principal (!)
selected_jogador = tk.StringVar()
jogador_cb = ttk.Combobox(menu_frame, textvariable=selected_jogador)
arr_Jogadores = []

#Busca nomes dos jogadores e cria combobox para o menu principal (!)
arr_Jogadores = ler_nome_jogadores()
jogador_cb['values'] = arr_Jogadores
jogador_cb['state'] = 'disabled'
jogador_cb.pack(fill=tk.X, padx=100, pady=5)

# Variáveis do jogador
jogador = ''
FASE = 0
NIVEL = 0
PLAYER_ARQ_CONFIG = ''


#vincula o evento de alterar da combobox de jogador com a função jogador_changed (!)
jogador_cb.bind('<<ComboboxSelected>>', jogador_changed)

# cria botão para acessar janela de cadastro de jogador no frame do menu principal (!)
B = tk.Button(menu_frame, text ="Cadastrar Novo Jogador", command = cadastrarCallback)
B.pack(fill=tk.X, padx=100, pady=10)

# label de texto para o menu principal (!)
label = ttk.Label(menu_frame, text="Fase:")
label.pack(fill=tk.X, padx=100, pady=5)

# cria combobox para escolha da fase para o menu principal (!)
selected_fase = tk.StringVar()
fase_cb = ttk.Combobox(menu_frame, textvariable=selected_fase)
fase_cb['state'] = 'disabled'
fase_cb.pack(fill=tk.X, padx=100, pady=5)

#vincula o evento de alterar da combobox de fase com a função fase_changed (!)
fase_cb.bind('<<ComboboxSelected>>', fase_changed)

# label de texto para o menu principal (!)
label = ttk.Label(menu_frame, text="Nível:")
label.pack(fill=tk.X, padx=100, pady=5)

# cria combobox para escolha de nivel para o menu principal (!)
selected_nivel = tk.StringVar()
nivel_cb = ttk.Combobox(menu_frame, textvariable=selected_nivel)
nivel_cb['state'] = 'disabled'
nivel_cb.pack(fill=tk.X, padx=100, pady=5)

#vincula o evento de alterar da combobox de nivel com a função nivel_changed (!)
nivel_cb.bind('<<ComboboxSelected>>', nivel_changed)

# cria botão para abrir jogo no frame do menu principal (!)
B = tk.Button(menu_frame, text ="Jogar", command = JogarCallback)
B.pack()

#prepara frame do menu principal
menu_frame.pack()

#Frame Cadastro
# lê jogadores (!)
arr_Jogadores = ler_nome_jogadores()
#cria label e campo de nome no frame de cadastro (!)
NomeString = tk.StringVar(cad_frame)
LNome = tk.Label(cad_frame, text="Nome: ")
LNome.grid(column=0, row=0, sticky=tk.W)
Nome = tk.Entry(cad_frame, width=20, textvariable=NomeString)
Nome.grid(column=1, row=0, padx=10)
#cria label e campo de nascimento no frame de cadastro (!)
DataString = tk.StringVar(cad_frame)
LData = tk.Label(cad_frame, text="Data de Nasc.: ")
LData.grid(column=0, row=1, sticky=tk.W)
Data = tk.Entry(cad_frame, width=20, textvariable=DataString)
Data.grid(column=1, row=1, padx=10)
#cria label e campo de observações no frame de cadastro (!)
ObsString = tk.StringVar(cad_frame)
LObs = tk.Label(cad_frame, text="Observação: ")
LObs.grid(column=0, row=2, sticky=tk.W)
Obs = tk.Entry(cad_frame, width=20, textvariable=ObsString)
Obs.grid(column=1, row=2, padx=10)

# cria botão para cadastrar novo jogador no frame do cadastro (!)
B = tk.Button(cad_frame, text="Cadastrar Novo Jogador", command=cadastrarcallback)
B.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

# cria botão para cancelar no frame do cadastro (!)
B = tk.Button(cad_frame, text="Cancelar", command=cancelarcallback)
B.grid(column=1, row=3, padx=10, pady=10, sticky=tk.W)

#cria loop para identificar os eventos
root.mainloop()