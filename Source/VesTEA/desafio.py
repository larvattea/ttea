import pygame
from pygame.image import load
import numpy as np
import random
from VesTEA.roupa import Roupa
import csv
csv.register_dialect(
    'mydialect',
    delimiter = ';',
    quotechar = '"',
    doublequote = True,
    skipinitialspace = True,
    lineterminator = '\n',
    quoting = csv.QUOTE_MINIMAL)

class Desafio():
    def __init__(self, fase, nivel):
        super().__init__()
        self.tilesize = 50
        self.fase = fase
        self.nivel = nivel
        print (111)
        self.labirinto = self.getLabirinto()
        print (222)
        self.roupa_certa = self.getRoupaCerta()
        print (333)
        self.corpo = self.getCorpo()
        print (444)
        self.clima = self.getClima()
        print (555)
        self.local = self.getLocal()
        print (665)
        self.roupa_errada = self.getRoupaErrada()
        
    def getLabirinto(self):
        rand = random.randint(1,3)
        if rand == 1:
            return np.array([
                [4,44,0,0,0,0,0,0,0,0,0,0,0,0,3,33],
                [44,44,1,0,0,0,0,0,0,0,0,0,0,1,33,33],
                [0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,0],
                [0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0],
                [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1],
                [0,0,0,0,0,0,0,2,22,0,0,0,0,0,0,0],
            ])
        elif rand == 2:
            return np.array([
                [0,0,0,0,0,0,0,3,33,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,33,33,0,0,0,0,0,0,0],
                [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,0,0,4,44,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,44,44,0,0,0,0,0,0,0],
                [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,2,22,0,0,0,0,0,0,0],
            ])
        elif rand == 3:
            return np.array([
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,4,44,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,44,44,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,0,0,0,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,0,0,0,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,3,33,0,0,0,0,0,0,0,0],
                [0,2,22,0,1,1,33,33,0,0,0,0,0,0,0,0],
            ])

    def getRoupaCerta(self):
        with open('VesTEA/config/roupas.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile, dialect='mydialect')
            cabecalho = next(csvreader)
            dados = list(csvreader)
        for linha in dados:
            print(', '.join(linha))
        print(len(dados))
        rouparand = random.randint(1,len(dados))-1
        print(dados[rouparand])
        print(dados[rouparand][0])
        return Roupa(dados[rouparand], rouparand)

    #1=torso; 2=pernas; 3= pés; 4=roupa de baixo
    def getCorpo(self):
        print('corpo:',self.roupa_certa.corpo)
        return self.roupa_certa.corpo

    #1=calor; 2=frio
    def getClima(self):
        print('clima:',self.roupa_certa.clima)
        return self.roupa_certa.clima

    #1=parque; 2=restaurante; 3=praia
    def getLocal(self):
        while (True):
            localrand = random.randint(1,len(self.roupa_certa.local))-1
            print('tentou local ',localrand)
            print(self.roupa_certa.local)
            print(self.roupa_certa.local[localrand])
            print(self.roupa_certa.local[localrand]=='1')
            if self.roupa_certa.local[localrand] =='1' :
                print('local:',localrand)
                return localrand

    def getRoupaErrada(self):
        with open('VesTEA/config/roupas.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile, dialect='mydialect')
            cabecalho = next(csvreader)
            dados = list(csvreader)
        print ('roupa errada2') 
        dados.pop(self.roupa_certa.posicao)
        rouparand = ""
        while rouparand == "":
            #gera roupa errada aleatoria
            rouparand = random.randint(1,len(dados))-1
            #verifica as diferencas
            diferencas = 0
            diferencas += 1 if dados[rouparand][1]!=self.roupa_certa.corpo else 0
            diferencas += 1 if dados[rouparand][2]!=self.roupa_certa.clima else 0
            print(dados[rouparand])
            print('self.local: ',self.local)
            print(dados[rouparand][3+self.local])
            diferencas += 1 if dados[rouparand][3+self.local]!=1 else 0 #o +3 considera apenas as posicoes de locais
            #se tiver ao menos uma diferença, usa essa roupa
            if diferencas >= 1:
                print ('Roupa é diferente...')
                return Roupa(dados[rouparand], rouparand)
            #remove da lista    
            else:
                print ('Roupa é igual, removendo...')
                dados.pop(rouparand)    
                if len(dados)<1: 
                    print ('Nenhuma roupa é diferente...')
                    return

    #captura onde o jogador está no labirinto
    def detectaColisao(self, x, y):
        y = y-150    
        lin = int(np.floor(x / 50))
        col = int(np.floor(y / 50))
        print(lin,col)
        if (0 <= lin <= 8) and (0 <= col <= 15):
            #retorna simbolo onde o jogador está
            return(self.labirinto[lin,col])
        else:
            #retorna -1 pois está fora do labirinto
            print('fora do labirinto')
            return -1

    
        
        