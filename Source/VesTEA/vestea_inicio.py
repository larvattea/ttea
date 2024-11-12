import pygame
from pygame import font
from pygame import display
from pygame.image import load
from pygame.transform import scale
from pygame import event
from pygame.locals import QUIT, KEYUP, K_SPACE, K_UP, K_DOWN, K_RIGHT, K_LEFT, K_s, K_h, K_f
from pygame.time import Clock

#from VesTEA.pose_tracking import PoseTracking
from VesTEA import arquivo as arq
from VesTEA import botao
from VesTEA.jogo import Jogo
from VesTEA.tutorial import Tutorial
from VesTEA.config_desafio import ConfigDesafio


#se for executar de outra pasta, precisa de:
#import os
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Vestea():
    def __init__(self, jogador):
        pygame.init()
        arq.set_Player(jogador)
        self.esta_rodando = True
        self.estado = 0
        self.tamanho = 800, 600
        self.configdesafio = ConfigDesafio()
        self.clock = Clock()
        self.fonte_destaque = font.SysFont('opensans', 80)
        self.fonte = font.SysFont('opensans', 40)
        self.fonte_legenda = font.SysFont('opensans', 25)
        self.superficie = display.set_mode(
            size=self.tamanho,
            display=0
        )
        display.set_caption(
            'VesTEA'
        )

        self.fundo = scale(
            load('VesTEA/images/space.jpg'),
            self.tamanho
        )

        self.jogo = Jogo(self.superficie, arq.get_V_FASE(), arq.get_V_NIVEL())
        self.tutorial = Tutorial(self.superficie)
        #self.fundo_inicio = scale(
        #    load('images/title_background.jpg'),
        #    self.tamanho
        #)

    def novo_jogo(self):
        #self.grupo_inimigos = Group()
        #self.grupo_tiros = Group()
        #self.jogador = Jogador(self)
        #self.grupo_jogador = GroupSingle(self.jogador) #permite draw
        #self.grupo_inimigos.add(Inimigo(self))

        self.mortes = 0
        #self.round = 0
    
    def rodar(self):
        #loop do jogo
        while self.esta_rodando:
            #print(evento)
            for evento in event.get():  # Events
                if evento.type == QUIT:
                    #print("clicou em fechar")
                    arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', 'Botao X Fechar')
                    arq.grava_Sessao(self.jogo.sessaoInicio, self.jogo.fase, self.jogo.nivel, self.jogo.sessaoAcertos, 
                                     self.jogo.sessaoAcertosAjuda, self.jogo.sessaoAjudas, 
                                     self.jogo.sessaoErros, self.jogo.sessaoOmissoes, self.jogo.totalColisoes)
                    self.esta_rodando = False
                if self.estado==1 or self.estado==2:
                    if evento.type == KEYUP:
                        if evento.key == K_SPACE:
                            arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', 'Botao ESPACO')
                            if self.jogo.jogando == True:
                                arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', 'Pausa')
                            else:
                                arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', 'Saiu da Pausa')
                            self.jogo.jogando = not self.jogo.jogando
                            self.tutorial.jogando = not self.tutorial.jogando
                        #ATIVA/DESATIVA SOM    
                        elif evento.key == K_s:
                            arq.set_R_SOM(not(bool(arq.get_V_SOM())))
                            arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', f'Som {arq.get_V_SOM()}')
                            #print('som: ', bool(arq.get_V_SOM()))
                        #ATIVA/DESATIVA HUD    
                        elif evento.key == K_h:
                            arq.set_R_HUD(not(bool(arq.get_V_HUD())))
                            arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', f'HUD {arq.get_V_HUD()}')
                            #print('HUD: ', bool(arq.get_V_HUD()))
                        #ALTERA COR DE FUNDO   
                        elif evento.key == K_f:
                            fundoSelecionado = arq.get_V_FUNDO()
                            if f'{fundoSelecionado}' == '(238, 236, 225)':
                                arq.set_K_FUNDO('(217, 217, 217)')
                            elif f'{fundoSelecionado}' == '(217, 217, 217)':
                                arq.set_K_FUNDO('(199, 199, 199)')
                            elif f'{fundoSelecionado}' == '(199, 199, 199)':
                                arq.set_K_FUNDO('(238, 236, 225)') 
                            arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Acao profissional', f'Cor de Fundo {arq.get_V_FUNDO()}')
                            #print('HUD: ', bool(arq.get_V_HUD()))
                        #################################
                        #  PARA TESTES MANUAIS          # 
                        #################################
                        elif evento.key == K_UP:#passou de fase
                            print('UP')
                            self.jogo.posicaoJogador = '3'
                            self.jogo.estado += 1
                            self.tutorial.posicaoJogador = '3'
                            self.tutorial.estado += 1
                        elif evento.key == K_DOWN:#retroagiu a fase
                            print('down')
                            self.jogo.posicaoJogador = '4'
                            self.jogo.estado += 1
                            self.tutorial.posicaoJogador = '4'
                            self.tutorial.estado += 1
                        elif evento.key == K_RIGHT:#se posicionou no inicio
                            print('side')
                            self.jogo.posicaoJogador = '2'
                            if self.jogo.estado < 7:
                                self.jogo.estado += 1
                            self.tutorial.posicaoJogador = '2'
                            if self.tutorial.estado < 7:
                                self.tutorial.estado += 1
                        elif evento.key == K_LEFT:#bateu na parede
                            #self.jogo.posicaoJogador = 1
                            arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Colidiu na parede', '')
                            self.jogo.acoesColisao(225,245)
                            #self.tutorial.acoesColisao(225,245)

            # Loop de eventos
            #################################
            #         TELA INICIAL          # 
            #################################     
            if self.estado==0:    
                self.superficie.fill((238, 236, 225))
                #CRIA TÍTULO
                titulo = self.fonte_destaque.render(
                    'VesTEA',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(titulo, (300, 60))
                
                #CRIA BOTÕES
                self.imagem_jogar = pygame.image.load('VesTEA/images/button_jogar.png').convert_alpha()
                self.botao_jogar = botao.Botao(322, 160, self.imagem_jogar, 1)
                self.imagem_tutorial = pygame.image.load('VesTEA/images/button_tutorial.png').convert_alpha()
                self.botao_tutorial = botao.Botao(298, 250, self.imagem_tutorial, 1)
                self.imagem_opcoes = pygame.image.load('VesTEA/images/button_opcoes.png').convert_alpha()
                self.botao_opcoes = botao.Botao(407, 340, self.imagem_opcoes, 1)
                self.imagem_personalizar = pygame.image.load('VesTEA/images/button_personalizar.png').convert_alpha()
                self.botao_personalizar = botao.Botao(407, 430, self.imagem_personalizar, 1)
                self.imagem_sair = pygame.image.load('VesTEA/images/button_sair.png').convert_alpha()
                self.botao_sair = botao.Botao(339, 520, self.imagem_sair, 1)
        
                #TEXTOS
                texto_opcoes = self.fonte.render(
                    'Jogo configurado',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_opcoes, (50, 365))
                texto_personalizar = self.fonte.render(
                    f'Jogador: {arq.get_Player()}',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 445))
                
                
                if self.botao_jogar.criar(self.superficie):
                    #print('START')
                    #self.novo_jogo()
                    self.jogo.configDesafio = self.configdesafio
                    self.jogo.jogando = True
                    self.jogo.estado = 1
                    self.estado=1
                if self.botao_tutorial.criar(self.superficie):
                    #print('NÃO IMPLEMENTADO')
                    arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Inicio Tutorial', '')
                    self.tutorial.jogando = True
                    self.tutorial.estado = 1
                    self.estado=2
                if self.botao_opcoes.criar(self.superficie):
                    pygame.time.delay(1000)
                    self.estado = 3
                if self.botao_personalizar.criar(self.superficie):
                    pygame.time.delay(1000)
                    self.estado = 4
                if self.botao_sair.criar(self.superficie):
                    #print('EXIT')
                    self.esta_rodando = False

            #################################
            #             JOGO              # 
            #################################     
            elif self.estado==1:
                #self.jogo.jogando = True
                self.jogo.update()
                #se sair do jogo, volta pro menu
                if self.jogo.estado == 99:
                    arq.grava_Sessao(self.jogo.sessaoInicio, self.jogo.fase, self.jogo.nivel, self.jogo.sessaoAcertos, 
                                     self.jogo.sessaoAcertosAjuda, self.jogo.sessaoAjudas, 
                                     self.jogo.sessaoErros, self.jogo.sessaoOmissoes, self.jogo.totalColisoes)    
                    self.jogo = Jogo(self.superficie, arq.get_V_FASE(), arq.get_V_NIVEL())
                    self.estado = 0
                #print(self.estado,' e ',self.jogo.estado)
            #################################
            #           TUTORIAL            # 
            #################################     
            elif self.estado==2:
                #self.jogo.jogando = True
                self.tutorial.update()
                #se terminar tutorial, volta pro menu
                if self.tutorial.estado == 99:
                    arq.grava_Detalhado(self.jogo.fase, self.jogo.nivel, 0, 'Fim tutorial', '')
                    self.tutorial = Tutorial(self.superficie)
                    self.estado = 0
                #print(self.estado,' e ',self.jogo.estado)
            #################################
            #         CONFIG GERAL          # 
            #################################     
            elif self.estado==3:
                self.superficie.fill((238, 236, 225))
                #CRIA TÍTULO
                titulo = self.fonte_destaque.render(
                    'Configurações gerais',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(titulo, (150, 60))
                #TEXTOS
                texto_opcoes = self.fonte.render(
                    'Imagem da parede',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_opcoes, (50, 165))
                texto_personalizar = self.fonte.render(
                    'Cor do fundo',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 345))
                #botoes opções de tijolo
                self.imagem_tijolo1 = pygame.image.load('Assets/vestea/imgs/tijolo1.jpg').convert_alpha()
                self.botao_tijolo1 = botao.Botao(320, 150, self.imagem_tijolo1, 1)
                self.imagem_tijolo2 = pygame.image.load('Assets/vestea/imgs/tijolo2.jpg').convert_alpha()
                self.botao_tijolo2 = botao.Botao(470, 150, self.imagem_tijolo2, 1)
                self.imagem_tijolo3 = pygame.image.load('Assets/vestea/imgs/tijolo3.jpg').convert_alpha()
                self.botao_tijolo3 = botao.Botao(620, 150, self.imagem_tijolo3, 1)
                if self.botao_tijolo1.criar(self.superficie):
                    arq.set_K_TIJOLO(1)
                elif self.botao_tijolo2.criar(self.superficie):
                    arq.set_K_TIJOLO(2)
                elif self.botao_tijolo3.criar(self.superficie):
                    arq.set_K_TIJOLO(3)
                #destaca imagem do tijolo selecionado
                tijoloSelecionado = arq.get_V_TIJOLO()
                if tijoloSelecionado == 1:
                    tijoloSelecionado = self.imagem_tijolo1
                    posicaotijolo = self.botao_tijolo1.rect.topleft
                elif tijoloSelecionado == 2:
                    tijoloSelecionado = self.imagem_tijolo2
                    posicaotijolo = self.botao_tijolo2.rect.topleft
                elif tijoloSelecionado == 3:
                    tijoloSelecionado = self.imagem_tijolo3
                    posicaotijolo = self.botao_tijolo3.rect.topleft
                pygame.draw.rect(tijoloSelecionado, (0,255,0), (0, 0, 119, 121),10)
                self.superficie.blit(tijoloSelecionado, tijoloSelecionado.get_rect(topleft = posicaotijolo))
                #botoes cores de fundo
                self.imagem_cor1 = pygame.image.load('Assets/vestea/imgs/fundo1.jpg').convert_alpha()
                self.botao_cor1 = botao.Botao(320, 330, self.imagem_cor1, 1)
                self.imagem_cor2 = pygame.image.load('Assets/vestea/imgs/fundo2.jpg').convert_alpha()
                self.botao_cor2 = botao.Botao(470, 330, self.imagem_cor2, 1)
                self.imagem_cor3 = pygame.image.load('Assets/vestea/imgs/fundo3.jpg').convert_alpha()
                self.botao_cor3 = botao.Botao(620, 330, self.imagem_cor3, 1)
                if self.botao_cor1.criar(self.superficie):
                    arq.set_K_FUNDO('(238, 236, 225)')
                elif self.botao_cor2.criar(self.superficie):
                    arq.set_K_FUNDO('(217, 217, 217)')
                elif self.botao_cor3.criar(self.superficie):
                    arq.set_K_FUNDO('(199, 199, 199)')
                #destaca imagem do fundo selecionado
                fundoSelecionado = arq.get_V_FUNDO()
                if f'{fundoSelecionado}' == '(238, 236, 225)':
                    fundoSelecionado = self.imagem_cor1
                    posicaofundo = self.botao_cor1.rect.topleft
                elif f'{fundoSelecionado}' == '(217, 217, 217)':
                    fundoSelecionado = self.imagem_cor2
                    posicaofundo = self.botao_cor2.rect.topleft
                elif f'{fundoSelecionado}' == '(199, 199, 199)':
                    fundoSelecionado = self.imagem_cor3
                    posicaofundo = self.botao_cor3.rect.topleft
                pygame.draw.rect(fundoSelecionado, (0,255,0), (0, 0, 119, 121),10)
                self.superficie.blit(fundoSelecionado, fundoSelecionado.get_rect(topleft = posicaofundo))
                #botao sair    
                self.imagem_sair = pygame.image.load('VesTEA/images/button_sair.png').convert_alpha()
                self.botao_sair = botao.Botao(339, 520, self.imagem_sair, 1)
                if self.botao_sair.criar(self.superficie):
                    pygame.time.delay(1000)
                    self.estado = 0
            #################################
            #        CONFIG JOGADOR         # 
            #################################     
            elif self.estado==4:
                self.superficie.fill((238, 236, 225))
                #CRIA TÍTULO
                titulo = self.fonte_destaque.render(
                    f'Configurações por jogador:',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(titulo, (50, 20))
                texto_nome = self.fonte.render(
                    f'{arq.get_Player()}',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_nome, (350, 100))
                #TEXTOS
                texto_opcoes = self.fonte.render(
                    'Cor do ponto',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_opcoes, (50, 180))
                texto_personalizar = self.fonte.render(
                    'Som',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 300))
                texto_personalizar = self.fonte.render(
                    'Hud (texto)',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 420))
                #botoes opções de cor do ponto
                self.imagem_ponto1 = pygame.image.load('Assets/vestea/imgs/corponto1.jpg').convert_alpha()
                self.botao_ponto1 = botao.Botao(320, 170, self.imagem_ponto1, 1)
                self.imagem_ponto2 = pygame.image.load('Assets/vestea/imgs/corponto2.jpg').convert_alpha()
                self.botao_ponto2 = botao.Botao(400, 170, self.imagem_ponto2, 1)
                self.imagem_ponto3 = pygame.image.load('Assets/vestea/imgs/corponto3.jpg').convert_alpha()
                self.botao_ponto3 = botao.Botao(480, 170, self.imagem_ponto3, 1)
                self.imagem_ponto4 = pygame.image.load('Assets/vestea/imgs/corponto4.jpg').convert_alpha()
                self.botao_ponto4 = botao.Botao(560, 170, self.imagem_ponto4, 1)
                if self.botao_ponto1.criar(self.superficie):
                    arq.set_R_COR_PONTO('(255, 255, 0)')
                elif self.botao_ponto2.criar(self.superficie):
                    arq.set_R_COR_PONTO('(255, 127, 39)')
                elif self.botao_ponto3.criar(self.superficie):
                    arq.set_R_COR_PONTO('(37, 34, 255)')
                elif self.botao_ponto4.criar(self.superficie):
                    arq.set_R_COR_PONTO('(234, 68, 188)')
                #destaca imagem do ponto selecionado
                pontoSelecionado = arq.get_V_COR_PONTO()
                if f'{pontoSelecionado}' == '(255, 255, 0)':
                    pontoSelecionado = self.imagem_ponto1
                    posicaoponto = self.botao_ponto1.rect.topleft
                elif f'{pontoSelecionado}' == '(255, 127, 39)':
                    pontoSelecionado = self.imagem_ponto2
                    posicaoponto = self.botao_ponto2.rect.topleft
                elif f'{pontoSelecionado}' == '(37, 34, 255)':
                    pontoSelecionado = self.imagem_ponto3
                    posicaoponto = self.botao_ponto3.rect.topleft
                elif f'{pontoSelecionado}' == '(234, 68, 188)':
                    pontoSelecionado = self.imagem_ponto4
                    posicaoponto = self.botao_ponto4.rect.topleft
                pygame.draw.rect(pontoSelecionado, (0,255,0), (0, 0, 60, 60),10)
                self.superficie.blit(pontoSelecionado, pontoSelecionado.get_rect(topleft = posicaoponto))
                #botão som
                if arq.get_V_SOM():
                    self.imagem_som = pygame.image.load('Assets/vestea/imgs/on.png').convert_alpha()
                else:
                    self.imagem_som = pygame.image.load('Assets/vestea/imgs/off.png').convert_alpha()
                self.botao_som = botao.Botao(320, 300, self.imagem_som, 0.2)
                if self.botao_som.criar(self.superficie):
                    pygame.time.delay(300)
                    arq.set_R_SOM(not arq.get_V_SOM())
                #botoes hud
                if arq.get_V_HUD():
                    self.imagem_hud = pygame.image.load('Assets/vestea/imgs/on.png').convert_alpha()
                else:
                    self.imagem_hud = pygame.image.load('Assets/vestea/imgs/off.png').convert_alpha()
                self.botao_hud = botao.Botao(320, 420, self.imagem_hud, 0.2)
                if self.botao_hud.criar(self.superficie):
                    pygame.time.delay(300)
                    arq.set_R_HUD(not arq.get_V_HUD())
                
                #botao sair    
                self.imagem_sair = pygame.image.load('VesTEA/images/button_sair.png').convert_alpha()
                self.botao_sair = botao.Botao(339, 520, self.imagem_sair, 1)
                if self.botao_sair.criar(self.superficie):
                    pygame.time.delay(1000)
                    self.estado = 0

            #################################
            #         CONFIG GERAL          # 
            #################################     
            elif self.estado==9:
                self.superficie.fill((238, 236, 225))
                #CRIA TÍTULO
                titulo = self.fonte_destaque.render(
                    'Configurações dos desafios',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(titulo, (20, 10))
                ######  TEXTOS
                texto_opcoes = self.fonte.render(
                    'Corpo',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_opcoes, (50, 110))
                texto_personalizar = self.fonte.render(
                    'Clima',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 225))
                texto_personalizar = self.fonte.render(
                    'Ocasião',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 335))
        ######  CORPO ######
                #botoes opções de corpo
                if self.configdesafio.corpo["nenhum"]:
                    imagem_corponenhum = pygame.image.load('Assets/vestea/imgs/ativo.png').convert_alpha()
                else:
                    imagem_corponenhum = pygame.image.load('Assets/vestea/imgs/inativo.png').convert_alpha()    
                botao_corponenhum = botao.Botao(200, 80, imagem_corponenhum, 1)
                legenda_corpo_nenhum = self.fonte_legenda.render(
                    'Nenhum',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_corpo_nenhum, (200, 150))
                if self.configdesafio.corpo["todos"]:
                    imagem_corpotodos = pygame.image.load('Assets/vestea/imgs/ativo.png').convert_alpha()
                else:
                    imagem_corpotodos = pygame.image.load('Assets/vestea/imgs/inativo.png').convert_alpha()
                botao_corpotodos = botao.Botao(300, 80, imagem_corpotodos, 1)
                legenda_corpo_todos = self.fonte_legenda.render(
                    'Todos',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_corpo_todos, (310, 150))
                imagem_corpo1 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Corpo1.png').convert_alpha()
                botao_corpo1 = botao.Botao(420, 80, imagem_corpo1, 1)
                legenda_corpo_1 = self.fonte_legenda.render(
                    'Superior',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_corpo_1, (405, 175))
                imagem_corpo2 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Corpo2.png').convert_alpha()
                botao_corpo2 = botao.Botao(515, 80, imagem_corpo2, 1)
                legenda_corpo_2 = self.fonte_legenda.render(
                    'Inferior',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_corpo_2, (505, 175))
                imagem_corpo3 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Corpo3.png').convert_alpha()
                botao_corpo3 = botao.Botao(610, 80, imagem_corpo3, 1)
                legenda_corpo_3 = self.fonte_legenda.render(
                    'Pés',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_corpo_3, (615, 175))
                imagem_corpo4 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Corpo4.png').convert_alpha()
                botao_corpo4 = botao.Botao(700, 80, imagem_corpo4, 1)
                legenda_corpo_4 = self.fonte_legenda.render(
                    'Íntima',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_corpo_4, (690, 173))
                #ações dos botões do corpo
                if botao_corponenhum.criar(self.superficie):
                    #print('botao nenhum')
                    pygame.time.delay(300)
                    self.configdesafio.corpo["nenhum"] = True
                    self.configdesafio.corpo["todos"] = False
                    self.configdesafio.corpo["1"] = False
                    self.configdesafio.corpo["2"] = False
                    self.configdesafio.corpo["3"] = False
                    self.configdesafio.corpo["4"] = False
                if botao_corpotodos.criar(self.superficie):
                    #print('botao todos')
                    pygame.time.delay(300)
                    self.configdesafio.corpo["nenhum"] = False
                    self.configdesafio.corpo["todos"] = True
                    self.configdesafio.corpo["1"] = True
                    self.configdesafio.corpo["2"] = True
                    self.configdesafio.corpo["3"] = True
                    self.configdesafio.corpo["4"] = True
                if botao_corpo1.criar(self.superficie):
                    #print('botao 1')
                    pygame.time.delay(300)
                    self.configdesafio.corpo["1"] = not self.configdesafio.corpo["1"]
                    if self.configdesafio.corpo["1"] and self.configdesafio.corpo["2"] and self.configdesafio.corpo["3"] and self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["todos"] = True
                    else:
                        self.configdesafio.corpo["todos"] = False
                    if not self.configdesafio.corpo["1"] and not self.configdesafio.corpo["2"] and not self.configdesafio.corpo["3"] and not self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["nenhum"] = True
                    else:
                        self.configdesafio.corpo["nenhum"] = False
                if botao_corpo2.criar(self.superficie):
                    #print('botao 2')
                    pygame.time.delay(300)
                    self.configdesafio.corpo["2"] = not self.configdesafio.corpo["2"]
                    if self.configdesafio.corpo["1"] and self.configdesafio.corpo["2"] and self.configdesafio.corpo["3"] and self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["todos"] = True
                    else:
                        self.configdesafio.corpo["todos"] = False
                    if not self.configdesafio.corpo["1"] and not self.configdesafio.corpo["2"] and not self.configdesafio.corpo["3"] and not self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["nenhum"] = True
                    else:
                        self.configdesafio.corpo["nenhum"] = False                
                if botao_corpo3.criar(self.superficie):
                    #print('botao 3')
                    pygame.time.delay(300)
                    self.configdesafio.corpo["3"] = not self.configdesafio.corpo["3"]
                    if self.configdesafio.corpo["1"] and self.configdesafio.corpo["2"] and self.configdesafio.corpo["3"] and self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["todos"] = True
                    else:
                        self.configdesafio.corpo["todos"] = False
                    if not self.configdesafio.corpo["1"] and not self.configdesafio.corpo["2"] and not self.configdesafio.corpo["3"] and not self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["nenhum"] = True
                    else:
                        self.configdesafio.corpo["nenhum"] = False                
                if botao_corpo4.criar(self.superficie):
                    #print('botao 4')
                    pygame.time.delay(300)
                    self.configdesafio.corpo["4"] = not self.configdesafio.corpo["4"]
                    if self.configdesafio.corpo["1"] and self.configdesafio.corpo["2"] and self.configdesafio.corpo["3"] and self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["todos"] = True
                    else:
                        self.configdesafio.corpo["todos"] = False
                    if not self.configdesafio.corpo["1"] and not self.configdesafio.corpo["2"] and not self.configdesafio.corpo["3"] and not self.configdesafio.corpo["4"]:
                        self.configdesafio.corpo["nenhum"] = True
                    else:
                        self.configdesafio.corpo["nenhum"] = False                
                #destaca imagens das partes do corpo selecionadas
                if self.configdesafio.corpo["1"]:
                    pygame.draw.rect(imagem_corpo1, (0,255,0), (0, 0, 40, 90),4)
                    self.superficie.blit(imagem_corpo1, imagem_corpo1.get_rect(topleft = botao_corpo1.rect.topleft))
                if self.configdesafio.corpo["2"]:
                    pygame.draw.rect(imagem_corpo2, (0,255,0), (0, 0, 40, 90),4)
                    self.superficie.blit(imagem_corpo2, imagem_corpo2.get_rect(topleft = botao_corpo2.rect.topleft))
                if self.configdesafio.corpo["3"]:
                    pygame.draw.rect(imagem_corpo3, (0,255,0), (0, 0, 40, 90),4)
                    self.superficie.blit(imagem_corpo3, imagem_corpo3.get_rect(topleft = botao_corpo3.rect.topleft))
                if self.configdesafio.corpo["4"]:
                    pygame.draw.rect(imagem_corpo4, (0,255,0), (0, 0, 40, 90),4)
                    self.superficie.blit(imagem_corpo4, imagem_corpo4.get_rect(topleft = botao_corpo4.rect.topleft))
    ######  CLIMA  ######
                #botoes opções de clima
                if self.configdesafio.clima["nenhum"]:
                    imagem_climanenhum = pygame.image.load('Assets/vestea/imgs/ativo.png').convert_alpha()
                else:
                    imagem_climanenhum = pygame.image.load('Assets/vestea/imgs/inativo.png').convert_alpha()    
                botao_climanenhum = botao.Botao(200, 205, imagem_climanenhum, 1)
                legenda_clima_nenhum = self.fonte_legenda.render(
                    'Nenhum',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_clima_nenhum, (200, 275))
                if self.configdesafio.clima["todos"]:
                    imagem_climatodos = pygame.image.load('Assets/vestea/imgs/ativo.png').convert_alpha()
                else:
                    imagem_climatodos = pygame.image.load('Assets/vestea/imgs/inativo.png').convert_alpha()
                botao_climatodos = botao.Botao(300, 205, imagem_climatodos, 1)
                legenda_clima_todos = self.fonte_legenda.render(
                    'Todos',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_clima_todos, (310, 275))
                imagem_clima1 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Clima1.png').convert_alpha()
                botao_clima1 = botao.Botao(420, 205, imagem_clima1, 1)
                legenda_clima_1 = self.fonte_legenda.render(
                    'Calor',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_clima_1, (437, 285))
                imagem_clima2 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Clima2.png').convert_alpha()
                botao_clima2 = botao.Botao(530, 205, imagem_clima2, 1)
                legenda_clima_2 = self.fonte_legenda.render(
                    'Frio',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_clima_2, (550, 285))
                #ações dos botões do clima
                if botao_climanenhum.criar(self.superficie):
                    #print('botao nenhum')
                    pygame.time.delay(300)
                    self.configdesafio.clima["nenhum"] = True
                    self.configdesafio.clima["todos"] = False
                    self.configdesafio.clima["1"] = False
                    self.configdesafio.clima["2"] = False
                if botao_climatodos.criar(self.superficie):
                    #print('botao todos')
                    pygame.time.delay(300)
                    self.configdesafio.clima["nenhum"] = False
                    self.configdesafio.clima["todos"] = True
                    self.configdesafio.clima["1"] = True
                    self.configdesafio.clima["2"] = True
                if botao_clima1.criar(self.superficie):
                    #print('botao 1')
                    pygame.time.delay(300)
                    self.configdesafio.clima["1"] = not self.configdesafio.clima["1"]
                    if self.configdesafio.clima["1"] and self.configdesafio.clima["2"]:
                        self.configdesafio.clima["todos"] = True
                    else:
                        self.configdesafio.clima["todos"] = False
                    if not self.configdesafio.clima["1"] and not self.configdesafio.clima["2"]:
                        self.configdesafio.clima["nenhum"] = True
                    else:
                        self.configdesafio.clima["nenhum"] = False
                if botao_clima2.criar(self.superficie):
                    #print('botao 2')
                    pygame.time.delay(300)
                    self.configdesafio.clima["2"] = not self.configdesafio.clima["2"]
                    if self.configdesafio.clima["1"] and self.configdesafio.clima["2"]:
                        self.configdesafio.clima["todos"] = True
                    else:
                        self.configdesafio.clima["todos"] = False
                    if not self.configdesafio.clima["1"] and not self.configdesafio.clima["2"]:
                        self.configdesafio.clima["nenhum"] = True
                    else:
                        self.configdesafio.clima["nenhum"] = False              
                #destaca imagens das partes do clima selecionadas
                if self.configdesafio.clima["1"]:
                    pygame.draw.rect(imagem_clima1, (0,255,0), (0, 0, 80, 80),6)
                    self.superficie.blit(imagem_clima1, imagem_clima1.get_rect(topleft = botao_clima1.rect.topleft))
                if self.configdesafio.clima["2"]:
                    pygame.draw.rect(imagem_clima2, (0,255,0), (0, 0, 80, 80),6)
                    self.superficie.blit(imagem_clima2, imagem_clima2.get_rect(topleft = botao_clima2.rect.topleft))
 
        ######  OCASIAO  ######
                #botoes opções de ocasiao
                if self.configdesafio.ocasiao["nenhum"]:
                    imagem_ocasiaonenhum = pygame.image.load('Assets/vestea/imgs/ativo.png').convert_alpha()
                else:
                    imagem_ocasiaonenhum = pygame.image.load('Assets/vestea/imgs/inativo.png').convert_alpha()    
                botao_ocasiaonenhum = botao.Botao(200, 310, imagem_ocasiaonenhum, 1)
                legenda_ocasiao_nenhum = self.fonte_legenda.render(
                    'Nenhum',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_nenhum, (200, 380))
                if self.configdesafio.ocasiao["todos"]:
                    imagem_ocasiaotodos = pygame.image.load('Assets/vestea/imgs/ativo.png').convert_alpha()
                else:
                    imagem_ocasiaotodos = pygame.image.load('Assets/vestea/imgs/inativo.png').convert_alpha()
                botao_ocasiaotodos = botao.Botao(300, 310, imagem_ocasiaotodos, 1)
                legenda_ocasiao_todos = self.fonte_legenda.render(
                    'Todos',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_todos, (310, 380))
                imagem_ocasiao1 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local1.jpg').convert_alpha()
                botao_ocasiao1 = botao.Botao(420, 322, imagem_ocasiao1, 1)
                legenda_ocasiao_1 = self.fonte_legenda.render(
                    'Parque',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_1, (428, 390))
                imagem_ocasiao2 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local2.jpg').convert_alpha()
                botao_ocasiao2 = botao.Botao(520, 310, imagem_ocasiao2, 1)
                legenda_ocasiao_2 = self.fonte_legenda.render(
                    'Restaurante',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_2, (505, 390))
                imagem_ocasiao3 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local3.jpg').convert_alpha()
                botao_ocasiao3 = botao.Botao(610, 310, imagem_ocasiao3, 1)
                legenda_ocasiao_3 = self.fonte_legenda.render(
                    'Praia',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_3, (630, 390))
                imagem_ocasiao4 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local4.jpg').convert_alpha()
                botao_ocasiao4 = botao.Botao(700, 310, imagem_ocasiao4, 1)
                legenda_ocasiao_4 = self.fonte_legenda.render(
                    'Mercado',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_4, (704, 390))
                imagem_ocasiao5 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local5.jpg').convert_alpha()
                botao_ocasiao5 = botao.Botao(420, 428, imagem_ocasiao5, 1)
                legenda_ocasiao_5 = self.fonte_legenda.render(
                    'Piscina',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_5, (428, 500))
                imagem_ocasiao6 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local6.jpg').convert_alpha()
                botao_ocasiao6 = botao.Botao(515, 424, imagem_ocasiao6, 1)
                legenda_ocasiao_6 = self.fonte_legenda.render(
                    'Esporte',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_6, (523, 500))
                imagem_ocasiao7 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local7.jpg').convert_alpha()
                botao_ocasiao7 = botao.Botao(610, 420, imagem_ocasiao7, 1)
                legenda_ocasiao_7 = self.fonte_legenda.render(
                    'Escola',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_7, (622, 500))
                imagem_ocasiao8 = pygame.image.load('Assets/vestea/imgs/desafios/mini/Local8.jpg').convert_alpha()
                botao_ocasiao8 = botao.Botao(700, 420, imagem_ocasiao8, 1)
                legenda_ocasiao_8 = self.fonte_legenda.render(
                    'Festa',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(legenda_ocasiao_8, (719, 500))
                #ações dos botões do ocasiao
                if botao_ocasiaonenhum.criar(self.superficie):
                    #print('botao nenhum')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["nenhum"] = True
                    self.configdesafio.ocasiao["todos"] = False
                    self.configdesafio.ocasiao["1"] = False
                    self.configdesafio.ocasiao["2"] = False
                    self.configdesafio.ocasiao["3"] = False
                    self.configdesafio.ocasiao["4"] = False
                    self.configdesafio.ocasiao["5"] = False
                    self.configdesafio.ocasiao["6"] = False
                    self.configdesafio.ocasiao["7"] = False
                    self.configdesafio.ocasiao["8"] = False
                if botao_ocasiaotodos.criar(self.superficie):
                    #print('botao todos')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["nenhum"] = False
                    self.configdesafio.ocasiao["todos"] = True
                    self.configdesafio.ocasiao["1"] = True
                    self.configdesafio.ocasiao["2"] = True
                    self.configdesafio.ocasiao["3"] = True
                    self.configdesafio.ocasiao["4"] = True
                    self.configdesafio.ocasiao["5"] = False
                    self.configdesafio.ocasiao["6"] = False
                    self.configdesafio.ocasiao["7"] = False
                    self.configdesafio.ocasiao["8"] = False
                if botao_ocasiao1.criar(self.superficie):
                    #print('botao 1')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["1"] = not self.configdesafio.ocasiao["1"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao2.criar(self.superficie):
                    #print('botao 2')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["2"] = not self.configdesafio.ocasiao["2"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao3.criar(self.superficie):
                    #print('botao 3')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["3"] = not self.configdesafio.ocasiao["3"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao4.criar(self.superficie):
                    #print('botao 4')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["4"] = not self.configdesafio.ocasiao["4"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao5.criar(self.superficie):
                    #print('botao 5')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["5"] = not self.configdesafio.ocasiao["5"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao6.criar(self.superficie):
                    #print('botao 6')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["6"] = not self.configdesafio.ocasiao["6"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao7.criar(self.superficie):
                    #print('botao 7')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["7"] = not self.configdesafio.ocasiao["7"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                if botao_ocasiao8.criar(self.superficie):
                    #print('botao 8')
                    pygame.time.delay(300)
                    self.configdesafio.ocasiao["8"] = not self.configdesafio.ocasiao["8"]
                    if self.configdesafio.ocasiao["1"] and self.configdesafio.ocasiao["2"] and self.configdesafio.ocasiao["3"] and self.configdesafio.ocasiao["4"] and self.configdesafio.ocasiao["5"] and self.configdesafio.ocasiao["6"] and self.configdesafio.ocasiao["7"] and self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["todos"] = True
                    else:
                        self.configdesafio.ocasiao["todos"] = False
                    if not self.configdesafio.ocasiao["1"] and not self.configdesafio.ocasiao["2"] and not self.configdesafio.ocasiao["3"] and not self.configdesafio.ocasiao["4"] and not self.configdesafio.ocasiao["5"] and not self.configdesafio.ocasiao["6"] and not self.configdesafio.ocasiao["7"] and not self.configdesafio.ocasiao["8"]:
                        self.configdesafio.ocasiao["nenhum"] = True
                    else:
                        self.configdesafio.ocasiao["nenhum"] = False
                #destaca imagens das partes do ocasiao selecionadas
                if self.configdesafio.ocasiao["1"]:
                    pygame.draw.rect(imagem_ocasiao1, (0,255,0), (0, 0, 80, 55),4)
                    self.superficie.blit(imagem_ocasiao1, imagem_ocasiao1.get_rect(topleft = botao_ocasiao1.rect.topleft))
                if self.configdesafio.ocasiao["2"]:
                    pygame.draw.rect(imagem_ocasiao2, (0,255,0), (0, 0, 71, 80),4)
                    self.superficie.blit(imagem_ocasiao2, imagem_ocasiao2.get_rect(topleft = botao_ocasiao2.rect.topleft))
                if self.configdesafio.ocasiao["3"]:
                    pygame.draw.rect(imagem_ocasiao3, (0,255,0), (0, 0, 80, 80),4)
                    self.superficie.blit(imagem_ocasiao3, imagem_ocasiao3.get_rect(topleft = botao_ocasiao3.rect.topleft))
                if self.configdesafio.ocasiao["4"]:
                    pygame.draw.rect(imagem_ocasiao4, (0,255,0), (0, 0, 79, 80),4)
                    self.superficie.blit(imagem_ocasiao4, imagem_ocasiao4.get_rect(topleft = botao_ocasiao4.rect.topleft))
                if self.configdesafio.ocasiao["5"]:
                    pygame.draw.rect(imagem_ocasiao5, (0,255,0), (0, 0, 80, 64),4)
                    self.superficie.blit(imagem_ocasiao5, imagem_ocasiao5.get_rect(topleft = botao_ocasiao5.rect.topleft))
                if self.configdesafio.ocasiao["6"]:
                    pygame.draw.rect(imagem_ocasiao6, (0,255,0), (0, 0, 80, 72),4)
                    self.superficie.blit(imagem_ocasiao6, imagem_ocasiao6.get_rect(topleft = botao_ocasiao6.rect.topleft))
                if self.configdesafio.ocasiao["7"]:
                    pygame.draw.rect(imagem_ocasiao7, (0,255,0), (0, 0, 80, 80),4)
                    self.superficie.blit(imagem_ocasiao7, imagem_ocasiao7.get_rect(topleft = botao_ocasiao7.rect.topleft))
                if self.configdesafio.ocasiao["8"]:
                    pygame.draw.rect(imagem_ocasiao8, (0,255,0), (0, 0, 80, 80),4)
                    self.superficie.blit(imagem_ocasiao8, imagem_ocasiao8.get_rect(topleft = botao_ocasiao8.rect.topleft))
                #botao voltar    
                self.imagem_voltar = pygame.image.load('VesTEA/images/button_voltar.png').convert_alpha()
                self.botao_voltar = botao.Botao(30, 500, self.imagem_voltar, 0.15)
                if self.botao_voltar.criar(self.superficie):
                    pygame.time.delay(500)
                    self.estado = 0  
                #botao jogar    
                self.imagem_jogar = pygame.image.load('VesTEA/images/button_jogar.png').convert_alpha()
                self.botao_jogar = botao.Botao(600, 530, self.imagem_jogar, 1)
                if self.botao_jogar.criar(self.superficie):
                    pygame.time.delay(500)
                    self.estado = 1  
            #atualiza a tela         
            display.update()

def main(jogador):
    g = Vestea(jogador)
    
    #g.novo_jogo()
    g.rodar()

    #print("saiu")
    pygame.quit()
    exit()


