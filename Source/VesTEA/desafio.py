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
        self.tilesize = 25
        self.fase = fase
        self.nivel = nivel
        #print (111)
        self.labirinto = self.getLabirinto()
        #print (222)
        self.roupa_certa = self.getRoupaCerta()
        #print (333)
        self.corpo = int(self.getCorpo())
        #print (444)
        self.clima = int(self.getClima())
        #print (555)
        self.local = int(self.getLocal())
        #print (665)
        self.roupa_errada = self.getRoupaErrada()
        self.DefineImagensDesafio()
        
    def getLabirinto(self):
        rand = random.randint(1,3)
        #rand = 1
        if rand == 1:
            return np.array([
                [4,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,33,33,33],
                [44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33,33,33,33],
                [44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33,33,33,33],
                [44,44,44,44,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,33,33,33,33],
                [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,22,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            ])
        elif rand == 2:
            return np.array([
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,3,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,33,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,33,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,33,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,4,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,2,22,0,0,1,1,44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,22,22,0,0,1,1,44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            ])
        elif rand == 3:
            return np.array([
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,3,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,33,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,33,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,33,33,33,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,4,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,1,44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,2,22,0,0,1,1,44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,22,22,0,0,1,1,44,44,44,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            ])
        elif rand == 4:
            return np.array([
                [3,33,0,0,0,0,0,0,0,0,0,0,0,0,4,44],
                [33,33,1,0,0,0,0,0,0,0,0,0,0,1,44,44],
                [0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,0],
                [0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0],
                [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1],
                [0,0,0,0,0,0,0,2,22,0,0,0,0,0,0,0],
            ])
        elif rand == 5:
            return np.array([
                [0,0,0,0,0,0,0,4,44,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,44,44,0,0,0,0,0,0,0],
                [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0],
                [0,0,0,0,0,0,0,3,33,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,33,33,0,0,0,0,0,0,0],
                [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,2,22,0,0,0,0,0,0,0],
            ])
        elif rand == 6:
            return np.array([
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,3,33,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,33,33,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,1,0,0,0,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,0,0,0,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,4,44,0,0,0,0,0,0,0,0],
                [0,2,22,0,1,1,44,44,0,0,0,0,0,0,0,0],
            ])

    def getRoupaCerta(self):
        with open('VesTEA/config/roupas.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile, dialect='mydialect')
            cabecalho = next(csvreader)
            dados = list(csvreader)
        for linha in dados:
            print(', '.join(linha))
        #print(len(dados))
        rouparand = random.randint(1,len(dados))-1
        print('Roupa certa:',dados[rouparand])
        #print(dados[rouparand][0])
        return Roupa(dados[rouparand], rouparand)

    #1=torso; 2=pernas; 3= pés; 4=roupa de baixo
    def getCorpo(self):
        print('Desafio corpo:',self.roupa_certa.corpo)
        return self.roupa_certa.corpo

    #1=calor; 2=frio
    def getClima(self):
        if self.roupa_certa.clima == '0':
            self.roupa_certa.clima = random.randint(1,2)
        print('Desafio clima:',self.roupa_certa.clima)
        return self.roupa_certa.clima

    #1=parque; 2=restaurante; 3=praia
    def getLocal(self):
        while (True):
            localrand = random.randint(1,len(self.roupa_certa.local))-1
            print('tentou local ',localrand+1)
            #print(self.roupa_certa.local)
            #print(self.roupa_certa.local[localrand])
            #print(self.roupa_certa.local[localrand]=='1')
            if self.roupa_certa.local[localrand] =='1' :
                print('Desafio local:',localrand+1)
                return localrand+1

    def getRoupaErrada(self):
        with open('VesTEA/config/roupas.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile, dialect='mydialect')
            cabecalho = next(csvreader)
            dados = list(csvreader)
        #print ('roupa errada') 
        #dados.pop(self.roupa_certa.posicao)
        #print(dados)
        rouparand = ""
        while True:
            #gera roupa errada aleatoria
            rouparand = random.randint(1,len(dados))-1
            #print(rouparand)
            print(dados)
            print('Roupa certa:', dados[self.roupa_certa.posicao])
            print('Roupa errada:', dados[rouparand])
            roupaSelecionada = Roupa(dados[rouparand], rouparand)
            print(roupaSelecionada.local)
            print('self.local: ',self.local)
            print(roupaSelecionada.local[self.local-1])
            #verifica as diferencas
            diferencas = [0,0,0]
            diferencas[0] += 1 if roupaSelecionada.corpo!=self.roupa_certa.corpo else 0
            diferencas[1] += 1 if (roupaSelecionada.clima!=self.roupa_certa.clima and self.roupa_certa.clima != '0' and roupaSelecionada.clima != '0') else 0
            diferencas[2] += 1 if roupaSelecionada.local[self.local-1]!='1' else 0 
            print('diferenças:', diferencas)
            #se tiver ao menos uma diferença, usa essa roupa
            if (diferencas[0] != diferencas[1] or diferencas[1] != diferencas[2]):
                print ('Roupa é diferente...')
                return roupaSelecionada
            #remove da lista    
            else:
                print ('Roupa é igual, buscar de novo...')
                #dados.pop(rouparand)    
                #if len(dados)<1: 
                    #print ('Nenhuma roupa é diferente...')
                    #return

    def DefineImagensDesafio(self):
        print('define desafio')
        #se fase for 1
        if self.fase == 1:
            while True:
            #repete
                #gera valor
                randNum = random.randint(1,3)
                #se certo for dif de errado, zera os outros 2
                if randNum == 1:
                    if (self.roupa_certa.corpo != self.roupa_errada.corpo):
                        print('Desafio = corpo:',self.roupa_certa.corpo,self.roupa_errada.corpo)
                        self.clima = 0
                        self.local = 0
                        return
                elif randNum == 2:
                    if (self.roupa_certa.clima != '0' and self.roupa_errada.clima != '0' and self.roupa_certa.clima != self.roupa_errada.clima):
                        print('Desafio = clima:',self.roupa_certa.clima,self.roupa_errada.clima)
                        self.corpo = 0
                        self.local = 0
                        return
                elif randNum == 3:
                    if (self.roupa_certa.local[self.local-1] != self.roupa_errada.local[self.local-1]):
                        print('Desafio = local:',self.roupa_certa.local[self.local-1],self.roupa_errada.local[self.local-1])
                        self.corpo = 0
                        self.clima = 0
                        return
        #se fase for 2
        elif self.fase == 2:
            while True:
            #repete
                #gera valor
                randNum = random.randint(1,3)
                #se certo for igual errado, zera ele
                if randNum == 1:
                    #print('Desafio = testa corpo:',self.roupa_certa.corpo,self.roupa_errada.corpo)
                    if (self.roupa_certa.corpo == self.roupa_errada.corpo):
                        print('Desafio = remove corpo:',self.roupa_certa.corpo,self.roupa_errada.corpo)
                        self.corpo = 0
                        return
                elif randNum == 2:
                    #print('Desafio = testa clima:',self.roupa_certa.clima,self.roupa_errada.clima)
                    if (int(self.roupa_certa.clima) + int(self.roupa_errada.clima) > 0 and self.roupa_certa.clima == self.roupa_errada.clima):
                        print('Desafio = remove clima:',self.roupa_certa.clima,self.roupa_errada.clima)
                        self.clima = 0
                        return
                elif randNum == 3:
                    #print('Desafio = testa local:',self.roupa_certa.local[self.local-1],self.roupa_errada.local[self.local-1])
                    if (self.roupa_certa.local[self.local-1] == self.roupa_errada.local[self.local-1]):
                        print('Desafio = remove local:',self.roupa_certa.local[self.local-1],self.roupa_errada.local[self.local-1])
                        self.local = 0
                        return
                

        


    #captura código do local onde o jogador está no labirinto
    def detectaColisao(self, x, y):
        y = y-125    
        col = int(np.floor(x / 25))
        lin = int(np.floor(y / 25))
        #print(lin,col)
        if (0 <= lin <= 17) and (0 <= col <= 31):
            #retorna simbolo onde o jogador está
            return(self.labirinto[lin,col])
        else:
            #retorna -1 pois está fora do labirinto
            #print('fora do labirinto')
            return -1

    #muda cor do local da parede onde o jogador colidiu
    def mudaParedeAtingida(self, x, y, labirinto):
        y = y-125    
        col = int(np.floor(x / 25))
        #lin = 3 #teste
        lin = int(np.floor(y / 25))
        #col = 4 #teste
        print(lin,col)
        if (0 <= lin <= 17) and (0 <= col <= 31):
            #altera labirinto para 11, que identifica que bateu nessa parede
            labirinto[lin,col] = 11
            return labirinto
        else:
            #retorna -1 pois está fora do labirinto
            #print('fora do labirinto')
            return -1

    
        
        