import csv
import random

import numpy as np
import pygame
from pygame.image import load
from VesTEA.roupa import Roupa

csv.register_dialect(
    "mydialect",
    delimiter=";",
    quotechar='"',
    doublequote=True,
    skipinitialspace=True,
    lineterminator="\n",
    quoting=csv.QUOTE_MINIMAL,
)


class DesafioTutorial:
    def __init__(self, nivel):
        super().__init__()
        self.tilesize = 25
        self.nivel = nivel
        # print (111)
        self.labirinto = self.getLabirintoCsv()
        print("labirinto:", self.labirinto)
        # print (222)
        self.roupa_certa = self.getRoupaCerta()
        # print (333)
        self.corpo = int(self.getCorpo())
        # print (444)
        self.clima = int(self.getClima())
        # print (555)
        self.local = int(self.getLocal())
        # print (665)
        self.DefineImagensDesafio()
        self.roupa_errada = self.getRoupaErrada()
        if nivel >= 6:
            self.roupa_coringa = self.getRoupaCoringa()
        else:
            self.roupa_coringa = ""

    def getLabirintoCsv(self):
        print(f"Labirinto: tutorial{self.nivel}.csv")
        with open(
            f"VesTEA/labirintos/tutorial{self.nivel}.csv", "r"
        ) as csvfile:
            csvreader = csv.reader(csvfile, dialect="mydialect")
            mapa = np.array(list(csvreader))
        return mapa

    def getRoupaCerta(self):
        with open("VesTEA/config/roupas.csv", "r") as csvfile:
            csvreader = csv.reader(csvfile, dialect="mydialect")
            cabecalho = next(csvreader)
            dados = list(csvreader)
        for linha in dados:
            print(", ".join(linha))
        # print(len(dados))
        rouparand = random.randint(1, len(dados)) - 1
        print("Roupa certa:", dados[rouparand])
        # print(dados[rouparand][0])
        return Roupa(dados[rouparand], rouparand)

    # 1=torso; 2=pernas; 3= pés; 4=roupa de baixo
    def getCorpo(self):
        print("Desafio corpo:", self.roupa_certa.corpo)
        return self.roupa_certa.corpo

    # 1=calor; 2=frio; 3=ambos
    def getClima(self):
        if self.roupa_certa.clima == "3":
            return random.randint(1, 2)
        print("Desafio clima:", self.roupa_certa.clima)
        return self.roupa_certa.clima

    # 1=parque; 2=restaurante; 3=praia
    def getLocal(self):
        while True:
            localrand = random.randint(1, len(self.roupa_certa.local)) - 1
            print("tentou local ", localrand + 1)
            # print(self.roupa_certa.local)
            # print(self.roupa_certa.local[localrand])
            # print(self.roupa_certa.local[localrand]=='1')
            if self.roupa_certa.local[localrand] == "1":
                print("Desafio local:", localrand + 1)
                return localrand + 1

    def DefineImagensDesafio(self):
        print("define desafio")
        print("Desafio = corpo:", self.roupa_certa.corpo)
        self.clima = 0
        self.local = 0
        return

    def getRoupaErrada(self):
        with open("VesTEA/config/roupas.csv", "r") as csvfile:
            csvreader = csv.reader(csvfile, dialect="mydialect")
            cabecalho = next(csvreader)
            dados = list(csvreader)
        print("buscando roupa errada")
        # dados.pop(self.roupa_certa.posicao)
        # print(dados)
        rouparand = ""
        while True:
            # gera roupa errada aleatoria
            rouparand = random.randint(1, len(dados)) - 1
            # print(rouparand)
            print(dados)
            print("Roupa certa:", dados[self.roupa_certa.posicao])
            print("Roupa errada:", dados[rouparand])
            roupaSelecionada = Roupa(dados[rouparand], rouparand)
            # verifica as diferencas
            # se tiver ao menos uma diferença, usa essa roupa
            if roupaSelecionada.corpo != self.roupa_certa.corpo:
                print("Roupa é diferente da certa...")
                return roupaSelecionada
            else:
                print("Roupa é igual, buscar de novo...")

    # captura código do local onde o jogador está no labirinto
    def detectaColisao(self, x, y):
        y = y - 195
        col = int(np.floor(x / 25))
        lin = int(np.floor(y / 25))
        # print(lin,col)
        if (0 <= lin <= 17) and (0 <= col <= 31):
            # retorna simbolo onde o jogador está
            return self.labirinto[lin, col]
        else:
            # retorna -1 pois está fora do labirinto
            # print('fora do labirinto')
            return -1

    # muda cor do local da parede onde o jogador colidiu
    def mudaParedeAtingida(self, x, y, labirinto):
        y = y - 195
        col = int(np.floor(x / 25))
        # lin = 3 #teste
        lin = int(np.floor(y / 25))
        # col = 4 #teste
        print(lin, col)
        if (0 <= lin <= 17) and (0 <= col <= 31):
            # altera labirinto para 11, que identifica que bateu nessa parede
            labirinto[lin, col] = 11
            return labirinto
        else:
            # retorna -1 pois está fora do labirinto
            # print('fora do labirinto')
            return -1
