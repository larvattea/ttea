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
        self.clock = Clock()
        self.fonte = font.SysFont('opensans', 40)
        self.fonte_destaque = font.SysFont('opensans', 80)
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
                    print("clicou em fechar")
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
                    'Jogador: Vestea',
                    True,
                    (50, 50, 50)
                )
                self.superficie.blit(texto_personalizar, (50, 445))
                
                
                if self.botao_jogar.criar(self.superficie):
                    #print('START')
                    #self.novo_jogo()
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
                    print('NÃO IMPLEMENTADO')
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
            display.update()

def main(jogador):
    g = Vestea(jogador)
    
    #g.novo_jogo()
    g.rodar()

    #print("saiu")
    pygame.quit()
    exit()


