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

class Janela:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.width = 400
        self.height = 600
        self.screen_width = None
        self.logo = None
        self.arr_jogadores = None

    #centraliza uma janela de acordo com a resolução da tela 
    def centraliza_tela(self):
        self.screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cord = int((self.screen_width/2) - (self.width/2))
        y_cord = int((screen_height/2) - (self.height/2))
        self.root.geometry("{}x{}+{}+{}".format(self.width, self.height, x_cord, y_cord))

    def troca_tela(self, nova): #trabalhar nesse metodo
        self.frame.forget()
        nova.exibir()

    # Calibrar Button
    def calibrar_callback(self):
        import calibracao

    # busca nomes dos jogadores na lista de arquivos da pasta jogadores
    def ler_nome_jogadores(self):
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

class JanelaMenuPrincipal(Janela):
    def __init__(self, root):
        Janela.__init__(self, root)
        self.janela_cadastro = JanelaCadastro(self)
        self.nomeJogador = None
        self.fase = 0
        self.nivel = 0
        self.arq_config = ''
        self.jogador_cb = None
        self.game_cb = None
        self.fase_cb = None
        self.nivel_cb = None
        self.selected_jogador = None
        self.selected_game = None
        self.selected_fase = None
        self.selected_nivel = None
    #exibe menu do TTEA
    def exibir(self):
        
        self.root.title('Menu TTEA')
        self.centraliza_tela()

        #Se for a primeira vez, carrega os itens na tela
        if (self.logo == None):
            # Coloca a Logo no frame do menu principal (!)
            image = Image.open("Assets/TTEA Logo.png")
            photo = ImageTk.PhotoImage(image)
            self.logo = tk.Label(self.frame, text = "TTEA Logo", image = photo)
            self.logo.image = photo
            self.logo.pack()

            #Coloca botão de calibração no frame do menu principal (!)
            B = tk.Button(self.frame, text ="Calibrar", command = self.calibrar_callback)
            B.pack()

            # label de texto para menu principal (!)
            label = ttk.Label(self.frame, text="Jogos:")
            label.pack(fill=tk.X, padx=100, pady=5)

            # cria a combobox de jogos para o menu principal (!)
            self.selected_game = tk.StringVar()
            self.game_cb = ttk.Combobox(self.frame, textvariable=self.selected_game)
            # define opções de jogos e coloca no modo leitura para o menu principal (!)
            self.game_cb['values'] = ['KARTEA', 'REPETEA']
            self.game_cb['state'] = 'readonly'
            self.game_cb.pack(fill=tk.X, padx=100, pady=5)

            #vincula o evento de alterar da combobox de jogo com a função game_changed (!)
            self.game_cb.bind('<<ComboboxSelected>>', self.game_changed)

            # label de texto para o menu principal (!)
            label = ttk.Label(self.frame, text="Jogador:")
            label.pack(fill=tk.X, padx=100, pady=5)

            # cria botão para acessar janela de cadastro de jogador no frame do menu principal (!)
            B = tk.Button(self.frame, text ="Cadastrar Novo Jogador", command = self.cadastrar_callback)
            B.pack(fill=tk.X, padx=100, pady=10)

            # cria combobox para escolha do jogador para o menu principal (!)
            self.selected_jogador = tk.StringVar()
            self.jogador_cb = ttk.Combobox(self.frame, textvariable=self.selected_jogador)
            
            #Busca nomes dos jogadores e cria combobox para o menu principal (!)
            self.jogador_cb['state'] = 'disabled'
            self.jogador_cb.pack(fill=tk.X, padx=100, pady=5)

            #vincula o evento de alterar da combobox de jogador com a função jogador_changed (!)
            self.jogador_cb.bind('<<ComboboxSelected>>', self.jogador_changed)

            # label de texto para o menu principal (!)
            label = ttk.Label(self.frame, text="Fase:")
            label.pack(fill=tk.X, padx=100, pady=5)

            # cria combobox para escolha da fase para o menu principal (!)
            self.selected_fase = tk.StringVar()
            self.fase_cb = ttk.Combobox(self.frame, textvariable=self.selected_fase)
            self.fase_cb['state'] = 'disabled'
            self.fase_cb.pack(fill=tk.X, padx=100, pady=5)

            #vincula o evento de alterar da combobox de fase com a função fase_changed (!)
            self.fase_cb.bind('<<ComboboxSelected>>', self.fase_changed)

            # label de texto para o menu principal (!)
            label = ttk.Label(self.frame, text="Nível:")
            label.pack(fill=tk.X, padx=100, pady=5)

            # cria combobox para escolha de nivel para o menu principal (!)
            self.selected_nivel = tk.StringVar()
            self.nivel_cb = ttk.Combobox(self.frame, textvariable=self.selected_nivel)
            self.nivel_cb['state'] = 'disabled'
            self.nivel_cb.pack(fill=tk.X, padx=100, pady=5)

            #vincula o evento de alterar da combobox de nivel com a função nivel_changed (!)
            self.nivel_cb.bind('<<ComboboxSelected>>', self.nivel_changed)

            ############teste
            # label de texto para o menu principal (!)
            label = ttk.Label(self.frame, text="Tempo da fase:")
            label.pack(fill=tk.X, padx=100, pady=5)

            # cria combobox para escolha de tempo para o menu principal (!)
            self.selected_tempo = tk.StringVar()
            self.tempo_cb = ttk.Combobox(self.frame, textvariable=self.selected_tempo)
            self.tempo_cb['values'] = ['30', '60', '90']
            self.tempo_cb['state'] = 'readonly'
            self.tempo_cb.pack(fill=tk.X, padx=100, pady=5)

            #vincula o evento de alterar da combobox de nivel com a função nivel_changed (!)
            self.tempo_cb.bind('<<ComboboxSelected>>', self.tempo_changed)
            ############teste

            # cria botão para abrir jogo no frame do menu principal (!)
            B = tk.Button(self.frame, text ="Jogar", command = self.jogar)
            B.pack()

        self.arr_jogadores = self.ler_nome_jogadores()
        self.jogador_cb['values'] = self.arr_jogadores

        self.frame.pack()
        self.game_cb['state'] = 'readonly'
        self.game_cb.set('')
        self.jogador_cb['state'] = 'disabled'
        self.jogador_cb.set('')
        self.fase_cb['state'] = 'disabled'
        self.fase_cb.set('')
        self.nivel_cb['state'] = 'disabled'
        self.nivel_cb.set('')

    # redefine demais combobox caso usuário mude de jogo
    def game_changed(self, event):
        game = self.selected_game.get()
        self.jogador_cb['state'] = 'readonly'
        self.jogador_cb.set('')
        if game == 'KARTEA':
            self.fase_cb['values'] = ['1', '2', '3']
            self.nivel_cb['values'] = ['1', '2', '3', '4', '5', '6']
        else:
            self.fase_cb['values'] = ['1', '2', '3','4','5','6','7','8','9','10']
            self.nivel_cb['values'] = ['1', '2', '3', '4', '5']

        self.fase_cb['state'] = 'disabled'
        self.fase_cb.set('')
        self.nivel_cb['state'] = 'disabled'
        self.nivel_cb.set('')

    #função que altera valores das variáveis do jogador
    def jogador_changed(self, event):
        game = self.selected_game.get()
        self.nomeJogador = self.selected_jogador.get()
        player = "Jogadores/" + self.nomeJogador
        if game == 'KARTEA':
            self.arq_config = player + "_KarTEA_config.csv"
        elif game == 'REPETEA':
            self.arq_config = player + "_RepeTEA_config.csv"
            
        self.fase = arquivo.get_K_FASE(self.arq_config)
        self.nivel = arquivo.get_K_NIVEL(self.arq_config)
        self.fase_cb['state'] = 'readonly'
        self.fase_cb.current(self.fase-1)
        self.nivel_cb['state'] = 'readonly'
        self.nivel_cb.current(self.nivel-1)

    # salva nova escolha de fase no arquivo (! - ERRO - se só por mudar já salva no arquivo, terapeuta pode perder fase atual real)
    def fase_changed(self, event):
        #arquivo.set_K_FASE(self.arq_config, int(self.selected_fase.get()))
        self.fase = int(self.selected_fase.get())

    # salva nova escolha de nivel no arquivo (! - ERRO - se só por mudar já salva no arquivo, terapeuta pode perder fase atual real)
    def nivel_changed(self, event):
        #arquivo.set_K_NIVEL(self.arq_config, int(self.selected_nivel.get()))
        self.nivel = int(self.selected_nivel.get())

    # salva nova escolha de tempo no arquivo (! - ERRO - se só por mudar já salva no arquivo, terapeuta pode perder fase atual real)
    def tempo_changed(self, event):
        #arquivo.set_K_NIVEL(self.arq_config, int(self.selected_nivel.get()))
        self.tempo = int(self.selected_tempo.get())

    #função que seta os parâmetros e inicia o jogo selecionado
    def jogar(self):
        game = self.selected_game.get()
        arquivo.set_Player(self.nomeJogador)
        arquivo.set_Fase(self.fase)
        arquivo.set_K_FASE(self.arq_config, self.fase)
        arquivo.set_Nivel(self.nivel)
        arquivo.set_K_NIVEL(self.arq_config, self.nivel)
        arquivo.set_K_TEMPO_NIVEL(self.arq_config, self.tempo)
        print("Jogador: ", arquivo.get_Player(), " Fase: ", arquivo.get_Fase(), " Nivel: ", arquivo.get_Nivel(), " Tempo: ", arquivo.get_K_TEMPO_NIVEL(self.arq_config))
        settings.pontos_calibracao = arquivo.lerCalibracao()
        x1 = settings.pontos_calibracao[2][0]
        x2 = settings.pontos_calibracao[3][0]
        print("x1= ", x1, "x2= ", x2)
        settings.div0_pista = 0
        settings.div1_pista = (self.screen_width // 3)
        settings.div2_pista = (2*(self.screen_width//3))
        settings.div3_pista = self.screen_width
        print("Pontos de Calibracao: ", settings.pontos_calibracao)
        print("Div0: ", settings.div0_pista, " Div1: ", settings.div1_pista,"Div2: ", settings.div2_pista, " Div3: ", settings.div3_pista)

        if game == 'KARTEA':
            import KarTEA
            KarTEA.main()
        else:
            import RepeTEA
    
    #cria funcao que mostra janela de cadastro (!)
    def cadastrar_callback(self):
        self.frame.forget()
        self.janela_cadastro.exibir()

class JanelaCadastro(Janela):
    def __init__(self, parent):
        Janela.__init__(self, parent.root)
        self.width = 300
        self.height = 120
        self.parent = parent
        self.NomeString = None
        self.DataString = None
        self.ObsString = None

    #exibe janela de cadastro
    def exibir(self):
        self.root.title('Cadastro TTEA')
        self.centraliza_tela()
                
        #cria label e campo de nome no frame de cadastro (!)
        self.NomeString = tk.StringVar(self.frame)
        LNome = tk.Label(self.frame, text="Nome: ")
        LNome.grid(column=0, row=0, sticky=tk.W)
        Nome = tk.Entry(self.frame, width=20, textvariable=self.NomeString)
        Nome.grid(column=1, row=0, padx=10)
        #cria label e campo de nascimento no frame de cadastro (!)
        self.DataString = tk.StringVar(self.frame)
        LData = tk.Label(self.frame, text="Data de Nasc.: ")
        LData.grid(column=0, row=1, sticky=tk.W)
        Data = tk.Entry(self.frame, width=20, textvariable=self.DataString)
        Data.grid(column=1, row=1, padx=10)
        #cria label e campo de observações no frame de cadastro (!)
        self.ObsString = tk.StringVar(self.frame)
        LObs = tk.Label(self.frame, text="Observação: ")
        LObs.grid(column=0, row=2, sticky=tk.W)
        Obs = tk.Entry(self.frame, width=20, textvariable=self.ObsString)
        Obs.grid(column=1, row=2, padx=10)

        # cria botão para cadastrar novo jogador no frame do cadastro (!)
        B = tk.Button(self.frame, text="Cadastrar Novo Jogador", command=self.cadastrar)
        B.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

        # cria botão para cancelar no frame do cadastro (!)
        B = tk.Button(self.frame, text="Cancelar", command=self.menu_callback)
        B.grid(column=1, row=3, padx=10, pady=10, sticky=tk.W)
        self.frame.pack()

    #função que cadastra jogador e cria seus respectivos arquivos (! - ERRO - mesmo nome da função que abre a janela de cadastro)
    def cadastrar(self):
        SNome = self.NomeString.get()
        SData = self.DataString.get()
        SObs = self.ObsString.get()

        self.arr_jogadores = self.ler_nome_jogadores()
        if SNome not in self.arr_jogadores:
            arquivo.CadastrarJogador(SNome, SData, SObs)
            self.arr_jogadores.append(SNome)
            res = tk.messagebox.askquestion (title='Jogador cadastrado!', message='Jogador cadastrado com sucesso!\nDeseja cadastrar outro jogador?')
            if res == 'no':
                self.menu_callback()
        else:
            tk.messagebox.showerror(title='Erro!', message='Jogador com esse nome já esta cadastrado!')

    # função que reabre menu principal ao clicar em cancelar
    def menu_callback(self):
        self.frame.forget()
        self.parent.exibir()

#cria raiz do Tkinter que criará a janela
root = tk.Tk()
# configura a janela do menu principal (!)
root.resizable(False, False)
#cria objetos das janelas
janela_menu = JanelaMenuPrincipal(root)
janela_menu.exibir()

#cria loop para identificar os eventos
root.mainloop()