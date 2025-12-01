import datetime

import image
import numpy as np
import pygame
import ui
from camera import Camera
from pygame import display, event, font
from pygame.locals import K_SPACE, KEYUP, QUIT
from VesTEA import arquivo as arq
from VesTEA.botao import Botao
from VesTEA.config import Config
from VesTEA.config_desafio import ConfigDesafio
from VesTEA.desafio import Desafio
from VesTEA.jogador import Jogador
from VesTEA.tela import Tela


class Jogo:
    def __init__(self, superficie, fase, nivel, configdesafio):
        self.jogando = True
        self.fase = fase
        self.nivel = nivel
        self.configDesafio = configdesafio
        # mensuram nível
        self.jogada = 1
        self.pontos = 0
        self.colisoes = 0
        # controlam ajuda
        self.ultimaPosicao = [-9999, -9999]
        self.tempoSemMovimento = datetime.datetime.now()
        self.ajuda = False
        # para o fluxo do jogo
        self.estado = 1
        # captura do jogador
        self.cap = Camera()
        self.jogador = Jogador()
        self.superficie = superficie
        # total de um nivel
        self.totalAcertos = 0
        self.totalAcertosAjuda = 0
        self.totalOmissoes = 0
        self.totalColisoes = 0
        self.totalTempo = 0
        self.totalAjudas = 0
        self.trofeu = 2
        # total da sessão
        self.sessaoInicio = datetime.datetime.now().strftime("%X")
        self.sessaoAcertos = 0
        self.sessaoAcertosAjuda = 0
        self.sessaoOmissoes = 0
        self.sessaoAjudas = 0
        self.sessaoErros = 0
        self.sessaoColisoes = 0
        # imagens
        self.emoji = ""
        self.erro = pygame.image.load(
            f"Assets/vestea/imgs/erro.png"
        ).convert_alpha()
        self.erro = pygame.transform.scale(self.erro, (100, 100))

    def carregaDados(self):
        # mensuram nível
        if arq.get_V_SOM():
            Config.som_inicio.play()
        if self.jogada == 1:
            arq.grava_Detalhado(self.fase, self.nivel, 0, "Inicio Nivel", "")
            self.pontos = 0
            self.totalAcertos = 0
            self.totalAcertosAjuda = 0
            self.totalOmissoes = 0
            self.totalColisoes = 0
            self.totalTempo = datetime.datetime.now()
            self.totalAjudas = 0
            self.trofeu = 2
        self.tempoSemMovimento = 0
        self.colisoes = 0
        self.ajuda = False
        self.desafio = Desafio(
            self.fase, self.nivel, self.jogada, self.configDesafio
        )
        arq.grava_Detalhado(
            self.fase, self.nivel, 0, "Inicio da jogada", self.jogada
        )
        arq.grava_Detalhado(
            self.fase,
            self.nivel,
            0,
            "Roupa certa",
            self.desafio.roupa_certa.nome,
        )
        arq.grava_Detalhado(
            self.fase,
            self.nivel,
            0,
            "Roupa errada",
            self.desafio.roupa_errada.nome,
        )
        if self.nivel >= 6:
            tipoCoringa = "certa"
            if self.nivel < 11:
                tipoCoringa = "errada"
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                0,
                f"Roupa {tipoCoringa} 2",
                self.desafio.roupa_coringa.nome,
            )
        if self.desafio.corpo > 0:
            if self.desafio.corpo == 1:
                txtCorpo = "Torso"
            elif self.desafio.corpo == 2:
                txtCorpo = "Pernas"
            elif self.desafio.corpo == 3:
                txtCorpo = "Pes"
            elif self.desafio.corpo == 4:
                txtCorpo = "Roupa de baixo"
            arq.grava_Detalhado(
                self.fase, self.nivel, 0, "Desafio: corpo", txtCorpo
            )
        if self.desafio.clima > 0:
            if self.desafio.clima == 1:
                txtClima = "Calor"
            elif self.desafio.clima == 2:
                txtClima = "Frio"
            elif self.desafio.clima == 3:
                txtClima = "Ambos"
            arq.grava_Detalhado(
                self.fase, self.nivel, 0, "Desafio: clima", txtClima
            )
        # 1=parque; 2=restaurante; 3=praia; 4=compras; 5=piscina; 6=esporte; 7=escola; 8=festa
        if self.desafio.local > 0:
            if self.desafio.local == 1:
                txtLocal = "Parque"
            elif self.desafio.local == 2:
                txtLocal = "Restaurante"
            elif self.desafio.local == 3:
                txtLocal = "Praia"
            elif self.desafio.local == 4:
                txtLocal = "Compras"
            elif self.desafio.local == 5:
                txtLocal = "Piscina"
            elif self.desafio.local == 6:
                txtLocal = "Esporte"
            elif self.desafio.local == 7:
                txtLocal = "Escola"
            elif self.desafio.local == 8:
                txtLocal = "Festa"
            arq.grava_Detalhado(
                self.fase, self.nivel, 0, "Desafio: local", txtLocal
            )
        self.estado += 1
        self.ultimaPosicao = [-9999, -9999]

    def carregaTelaJogo(self):
        self.tela = Tela(self.desafio, 1)
        # inserindo captura do jogador
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x, y = self.jogador.get_feet_center()
        # print("Jogador em: ",x," - ",y)
        pygame.draw.circle(
            self.superficie, arq.get_V_COR_PONTO(), [x, y - 90], 15
        )
        self.posicaoJogador = self.desafio.detectaColisao(x, y)
        print("Jogador em: ", self.posicaoJogador)
        # print(self.posicaoJogador == '2' or self.posicaoJogador == '22')
        if self.posicaoJogador == "2" or self.posicaoJogador == "22":
            # self.posicaoJogador = '99'
            # print("Jogador em: ",self.posicaoJogador)
            # mostrar só desafio
            self.tela = Tela(self.desafio, 2)
            display.update()
            self.tempoSemMovimento = datetime.datetime.now()
            # print(f"Tempo parado 1:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            pygame.time.delay(3000)
            # mostrar labirinto e roupas
            # print(f"Tempo parado 2:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            self.tela = Tela(self.desafio, 3)
            display.update()
            pygame.time.delay(2000)
            self.cap.load_camera()
            self.estado += 1

    def carregaPartida(self):
        # self.posicaoJogador = '99'
        self.tela = Tela(self.desafio, 3)
        # print("Jogador 2 em: ",self.posicaoJogador)
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x, y = self.jogador.get_feet_center()
        # print("Jogador em: ",x," - ",y)
        pygame.draw.circle(
            self.superficie, arq.get_V_COR_PONTO(), [x, y - 90], 15
        )
        self.posicaoJogador = self.desafio.detectaColisao(x, y)
        # print("Jogador 2.5 em: ",self.posicaoJogador)
        display.update()
        # se o jogador ainda estiver na posição inicial, começa a partida
        if self.posicaoJogador == "2" or self.posicaoJogador == "22":
            # print("Jogador 3 em: ",self.posicaoJogador)
            # print(f"Tempo parado 3:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Inicio da movimentacao",
                "",
            )
            if arq.get_V_SOM():
                Config.som_vez_do_jogador_1.play()
                pygame.time.delay(500)
                Config.som_vez_do_jogador_2.play()
            self.jogador = Jogador()
            self.estado += 1

    def gerenciaJogo(self):
        self.tela = Tela(self.desafio, 3)
        # inserindo captura do jogador
        self.cap.load_camera()
        self.cap.frame = self.jogador.scan_feets(self.cap.frame)
        x, y = self.jogador.get_feet_center()
        # verifica se precisa de ajuda
        # print(f"Tempo parado:{(datetime.datetime.now() - self.tempoSemMovimento).seconds} segundos")
        # se ainda não atualizou ultima posição ou se jogador se moveu mais que 25px para qualquer direção, atualiza última posição
        if self.ultimaPosicao == [-9999, -9999] or (
            x > self.ultimaPosicao[0] + 25
            or x < self.ultimaPosicao[0] - 25
            or y > self.ultimaPosicao[1] + 25
            or y < self.ultimaPosicao[1] - 25
        ):
            print("inicio contador movimento")
            self.ultimaPosicao = [x, y]
            self.tempoSemMovimento = datetime.datetime.now()
        # senão, se passou mais do que 5 segundos e ainda não teve ajuda, dá ajuda
        elif (
            datetime.datetime.now() - self.tempoSemMovimento
        ).seconds > 5 and (
            datetime.datetime.now() - self.tempoSemMovimento
        ).seconds < 10:
            print("contador ajuda")
            # se ainda está false, toca som e muda ajuda pra true (pra tocar som uma vez apenas)
            if self.ajuda == False:
                arq.grava_Detalhado(
                    self.fase, self.nivel, self.posicaoJogador, "Ajuda", ""
                )
                if arq.get_V_SOM():
                    Config.som_ajuda.play()
                self.ajuda = True
                self.totalAjudas += 1
            # destaca imagem roupa certa
            pygame.draw.rect(
                self.tela.roupacerta_img, (0, 255, 0), (0, 0, 100, 100), 10
            )
            certo_rect = self.tela.roupacerta_img.get_rect(
                topleft=self.tela.roupacerta_pos
            )
            self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        # senão, entra em pausa por omissao
        elif (datetime.datetime.now() - self.tempoSemMovimento).seconds > 10:
            print("contador omissao")
            arq.grava_Detalhado(
                self.fase, self.nivel, self.posicaoJogador, "Omissao", ""
            )
            self.totalOmissoes += 1
            self.jogando = False

        # print("Jogador em: ",x,"-",y)
        pygame.draw.circle(
            self.superficie, arq.get_V_COR_PONTO(), [x, y - 90], 15
        )
        self.posicaoJogador = self.desafio.detectaColisao(x, y)
        if (
            self.posicaoJogador == "3"
            or self.posicaoJogador == "33"
            or self.posicaoJogador == "4"
            or self.posicaoJogador == "44"
        ):
            self.estado += 1
        if self.desafio.nivel >= 6:
            if self.posicaoJogador == "5" or self.posicaoJogador == "55":
                self.estado += 1
        if self.posicaoJogador == "1":
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Colidiu com parede",
                "",
            )
            self.acoesColisao(x, y)

    def verificaResultado(self):
        # some o labirinto
        self.tela = Tela(self.desafio, 4)
        # desenha retangulo na roupa certa
        pygame.draw.rect(
            self.tela.roupacerta_img, (0, 255, 0), (0, 0, 100, 100), 10
        )
        certo_rect = self.tela.roupacerta_img.get_rect(
            topleft=self.tela.roupacerta_pos
        )
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        # desenha retangulo na roupa errada
        pygame.draw.rect(
            self.tela.roupaerrada_img, (255, 0, 0), (0, 0, 100, 100), 10
        )
        erro_rect = self.tela.roupaerrada_img.get_rect(
            topleft=self.tela.roupaerrada_pos
        )
        self.superficie.blit(self.tela.roupaerrada_img, erro_rect)
        # desenha retangulo na roupa coringa
        if self.desafio.roupa_coringa != "":
            if self.desafio.nivel >= 11:
                pygame.draw.rect(
                    self.tela.roupacoringa_img,
                    (0, 255, 0),
                    (0, 0, 100, 100),
                    10,
                )
            else:
                pygame.draw.rect(
                    self.tela.roupacoringa_img,
                    (255, 0, 0),
                    (0, 0, 100, 100),
                    10,
                )
            coringa_rect = self.tela.roupacoringa_img.get_rect(
                topleft=self.tela.roupacoringa_pos
            )
            self.superficie.blit(self.tela.roupacoringa_img, coringa_rect)

        ######logica antiga de verificação de avanço/volta
        # if self.posicaoJogador == 3 or self.posicaoJogador == 33:
        #    self.acoesAvancaNivel()
        # elif self.posicaoJogador == 4 or self.posicaoJogador == 44:
        #    self.acoesVoltaNivel()
        ######logica nova de verificacao de avanço/volta
        ##calcula pontuação
        # se acertou sem ajuda, 10 ptos, se acertou om ajuda 5 pts
        if (self.posicaoJogador == "3" or self.posicaoJogador == "33") or (
            self.desafio.nivel >= 11
            and (self.posicaoJogador == "5" or self.posicaoJogador == "55")
        ):
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Escolheu Roupa Certa",
                "",
            )
            self.emoji = pygame.image.load(
                f"Assets/vestea/imgs/feliz.webp"
            ).convert_alpha()
            self.emoji = pygame.transform.scale(
                self.emoji, (self.tela.tilesize * 4, self.tela.tilesize * 4)
            )
            if arq.get_V_SOM():
                Config.som_acerto.play()
            self.totalAcertos += 1
            if self.ajuda == False:
                self.pontos += 10
            else:
                self.totalAcertosAjuda += 1
                self.pontos += 5
        elif (self.posicaoJogador == "4" or self.posicaoJogador == "44") or (
            self.desafio.nivel >= 6
            and (self.posicaoJogador == "5" or self.posicaoJogador == "55")
        ):
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Escolheu Roupa Errada",
                "",
            )
            self.emoji = pygame.image.load(
                f"Assets/vestea/imgs/triste.webp"
            ).convert_alpha()
            self.emoji = pygame.transform.scale(
                self.emoji, (self.tela.tilesize * 4, self.tela.tilesize * 4)
            )
            self.superficie.blit(self.erro, self.tela.roupaerrada_pos)
            if arq.get_V_SOM():
                Config.som_erro.play()
        # display.update()
        # soma pontos por não colidir
        self.pontos += 10 - self.colisoes
        display.update()
        pygame.time.delay(2500)
        self.estado += 1

    def exibeRoupasCertas(self):
        # some roupa errada
        self.tela = Tela(self.desafio, 5)
        # desenha emoji na tela
        self.superficie.blit(self.emoji, (275, 10))
        # desenha retangulo na roupa certa
        pygame.draw.rect(
            self.tela.roupacerta_img, (0, 255, 0), (0, 0, 100, 100), 10
        )
        certo_rect = self.tela.roupacerta_img.get_rect(
            topleft=self.tela.roupacerta_pos
        )
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        # desenha retangulo na roupa coringa se for certa
        if self.desafio.roupa_coringa != "":
            if self.desafio.nivel >= 11:
                pygame.draw.rect(
                    self.tela.roupacoringa_img,
                    (0, 255, 0),
                    (0, 0, 100, 100),
                    10,
                )
                coringa_rect = self.tela.roupacoringa_img.get_rect(
                    topleft=self.tela.roupacoringa_pos
                )
                self.superficie.blit(self.tela.roupacoringa_img, coringa_rect)
        display.update()
        pygame.time.delay(3000)
        self.cap.load_camera()
        self.estado += 1

    def finalizaJogada(self):
        # some roupa errada
        self.tela = Tela(self.desafio, 6)
        # desenha emoji na tela
        self.superficie.blit(self.emoji, (275, 10))
        # desenha retangulo na roupa certa
        pygame.draw.rect(
            self.tela.roupacerta_img, (0, 255, 0), (0, 0, 100, 100), 10
        )
        certo_rect = self.tela.roupacerta_img.get_rect(
            topleft=self.tela.roupacerta_pos
        )
        self.superficie.blit(self.tela.roupacerta_img, certo_rect)
        # desenha retangulo na roupa coringa se for certa
        if self.desafio.roupa_coringa != "":
            if self.desafio.nivel >= 11:
                pygame.draw.rect(
                    self.tela.roupacoringa_img,
                    (0, 255, 0),
                    (0, 0, 100, 100),
                    10,
                )
                coringa_rect = self.tela.roupacoringa_img.get_rect(
                    topleft=self.tela.roupacoringa_pos
                )
                self.superficie.blit(self.tela.roupacoringa_img, coringa_rect)
        # se for terceira jogada, exibe tela de resultado
        if self.jogada == 3:
            if arq.get_V_SOM():
                Config.som_trofeu.play()
            print("Pontos jogada 3 = ", self.pontos)
            # atualiza dados da sessão
            self.sessaoAcertos += self.totalAcertos
            self.sessaoAcertosAjuda += self.totalAcertosAjuda
            self.sessaoOmissoes += self.totalOmissoes
            self.sessaoAjudas += self.totalAjudas
            self.sessaoErros += 3 - self.totalAcertos
            self.sessaoColisoes += self.totalColisoes
            self.totalTempo = datetime.datetime.now() - self.totalTempo
            self.posicaoJogador = 0
            if self.pontos <= 20:
                self.trofeu = 1
            elif self.pontos >= 40:
                self.trofeu = 3
            # grava no detalhado
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Concluiu Nivel",
                "",
            )
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Pontuacao",
                self.pontos,
            )
            if self.trofeu == 1:
                textoResultado = "Retrocede nivel"
            elif self.trofeu == 2:
                textoResultado = "Permanece nivel"
            elif self.trofeu == 3:
                textoResultado = "Avanca nivel"
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Resultado",
                textoResultado,
            )
            # muda pra false pra mostrar tela de fim de nível
            self.jogando = False
        # senão, se jogador não estiver no ponto inicial, verifica sua posição
        elif self.posicaoJogador != "2" and self.posicaoJogador != "22":
            # inserindo captura do jogador
            self.cap.load_camera()
            self.cap.frame = self.jogador.scan_feets(self.cap.frame)
            x, y = self.jogador.get_feet_center()
            # print("Jogador em: ",x," - ",y)
            pygame.draw.circle(
                self.superficie, arq.get_V_COR_PONTO(), [x, y - 90], 15
            )
            self.posicaoJogador = self.desafio.detectaColisao(x, y)
        # se jogador voltar pro ponto inicial
        else:
            # se for jogada 1 ou 2, troca pra seguinte
            print("Pontos jogada ", self.jogada, " = ", self.pontos)
            self.jogada += 1
            self.posicaoJogador = "0"
            pygame.time.delay(1000)
            self.estado = 1
        display.update()

    def acoesAvancaNivel(self):

        print("avança")
        if self.nivel < 15:
            self.nivel += 1
        elif self.nivel == 15 and self.fase < 3:
            if (
                self.nivel == 15
                and self.verificaDesafiosDisponiveis(self.fase + 1) == False
            ):
                ui.draw_text(
                    self.superficie,
                    "Não há desafios suficientes para a próxima fase.",
                    (130, 575),
                    (38, 61, 39),
                    font=pygame.font.Font(None, 25),
                    shadow=False,
                )
            else:
                self.fase += 1
                self.nivel = 1

    def acoesVoltaNivel(self):
        print("Volta")

        if self.nivel == 1 and self.fase > 1:
            self.fase -= 1
            self.nivel = 15
        elif self.nivel > 1:
            self.nivel -= 1

    def acoesColisao(self, x, y):
        if arq.get_V_SOM():
            Config.som_erro.play()
        print("Bateu na parede")
        # pintar o quadrado
        self.desafio.labirinto = self.desafio.mudaParedeAtingida(
            x, y, self.desafio.labirinto
        )
        # se ainda não tem 10 colisoes, soma mais uma
        if self.colisoes < 10:
            self.colisoes += 1
            self.totalColisoes += 1

    ################################
    ##       TELA  PAUSA          ##
    ################################
    def carregaTelaPausa(self):
        self.superficie.fill((238, 236, 225))

        titulo = font.SysFont("opensans", 80).render(
            "Pausa", True, (50, 50, 50)
        )
        self.superficie.blit(titulo, (110, 50))

        # mostra as pecs
        self.tela.mostraDesafio()
        # mostra os atalhos
        ui.draw_text(
            self.superficie,
            "Atalhos:",
            (450, 200),
            (38, 61, 39),
            font=pygame.font.Font(None, 50),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            "Som: Tecla 'S'",
            (450, 280),
            (38, 61, 39),
            font=pygame.font.Font(None, 35),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            "Hud: Tecla 'H'",
            (450, 330),
            (38, 61, 39),
            font=pygame.font.Font(None, 35),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            "Cor de fundo: Tecla 'F'",
            (450, 380),
            (38, 61, 39),
            font=pygame.font.Font(None, 35),
            shadow=False,
        )
        # botao jogar
        self.imagem_jogar = pygame.image.load(
            "VesTEA/images/button_jogar.png"
        ).convert_alpha()
        self.botao_jogar = Botao(135, 250, self.imagem_jogar, 1)
        if self.botao_jogar.criar(self.superficie):
            print("continuar")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Jogar",
            )
            self.ultimaPosicao == [-9999, -9999]
            self.tempoSemMovimento = datetime.datetime.now()
            self.jogando = True
        # botao voltar
        self.imagem_voltar = pygame.image.load(
            "VesTEA/images/button_voltar.png"
        ).convert_alpha()
        self.botao_voltar = Botao(50, 350, self.imagem_voltar, 0.15)
        if self.botao_voltar.criar(self.superficie):
            print("voltar")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Voltar Nivel",
            )
            self.acoesVoltaNivel()
            self.jogando = True
            self.posicaoJogador = "0"
            self.jogada = 1
            self.estado = 1
        # botao reiniciar
        self.imagem_reiniciar = pygame.image.load(
            "VesTEA/images/button_reiniciar.png"
        ).convert_alpha()
        self.botao_reiniciar = Botao(180, 350, self.imagem_reiniciar, 0.3)
        if self.botao_reiniciar.criar(self.superficie):
            print("reiniciar")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Reiniciar Nivel",
            )
            self.tempoSemMovimento = 0
            self.colisoes = 0
            self.ajuda = False
            self.ultimaPosicao = [-9999, -9999]
            self.estado = (
                2  # para reiniciar o jogo no mesmo desafio, mas do começo
            )
            self.jogando = True
        # botao avancar
        self.imagem_avancar = pygame.image.load(
            "VesTEA/images/button_avancar.png"
        ).convert_alpha()
        self.botao_avancar = Botao(300, 350, self.imagem_avancar, 0.15)
        if self.botao_avancar.criar(self.superficie):
            print("avancar")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Avancar Nivel",
            )
            self.acoesAvancaNivel()
            self.jogando = True
            self.posicaoJogador = "0"
            self.jogada = 1
            self.estado = 1
        # botão SAIR
        self.imagem_sair = pygame.image.load(
            "VesTEA/images/button_sair.png"
        ).convert_alpha()
        self.botao_sair = Botao(152, 470, self.imagem_sair, 1)
        if self.botao_sair.criar(self.superficie):
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Sair para Menu",
            )
            self.cap.close_camera()
            self.posicaoJogador = "0"
            self.estado = 99
            self.jogando = True

    ################################
    ##      TELA  FEEDBACK        ##
    ################################
    def carregaTelaFeedback(self):
        self.superficie.fill((238, 236, 225))
        trofeu = image.load(f"VesTEA/images/trofeu{self.trofeu}.png")
        image.draw(self.superficie, trofeu, (0, 0))
        ui.draw_text(
            self.superficie,
            "Feedback",
            (450, 100),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            "Quantidade",
            (650, 100),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Tempo",
            (450, 130),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            str(self.totalTempo).split(".")[0],
            (650, 130),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Pontuação (%)",
            (450, 160),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            str(round(self.pontos * 100 / 60, 2)),
            (650, 160),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Roupas certas",
            (450, 190),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            f"{self.totalAcertos} de 3",
            (650, 190),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Acertos com ajuda",
            (450, 220),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            f"{self.totalAcertosAjuda}",
            (650, 220),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Ajudas",
            (450, 250),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            f"{self.totalAjudas}",
            (650, 250),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Paredes Colididas",
            (450, 280),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            f"{self.totalColisoes}",
            (650, 280),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        ui.draw_text(
            self.superficie,
            "Omissões",
            (450, 310),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )
        ui.draw_text(
            self.superficie,
            str(self.totalOmissoes),
            (650, 310),
            (38, 61, 39),
            font=pygame.font.Font(None, 25),
            shadow=False,
        )

        # botao voltar
        self.imagem_voltar = pygame.image.load(
            "VesTEA/images/button_voltar.png"
        ).convert_alpha()
        self.botao_voltar = Botao(220, 410, self.imagem_voltar, 0.15)
        if self.botao_voltar.criar(self.superficie):
            print("voltar")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Voltar Nivel",
            )
            self.acoesVoltaNivel()
            self.jogando = True
            self.posicaoJogador = "0"
            self.jogada = 1
            self.estado = 1

        # botão JOGAR
        self.imagem_inicio = pygame.image.load(
            "VesTEA/images/button_jogar.png"
        ).convert_alpha()
        self.botao_inicio = Botao(322, 420, self.imagem_inicio, 1)
        if self.botao_inicio.criar(self.superficie):
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Jogar",
            )
            if self.trofeu == 1:
                self.acoesVoltaNivel()
            elif self.trofeu == 3:
                self.acoesAvancaNivel()
            # print('START')
            self.jogando = True
            self.posicaoJogador = "0"
            self.jogada = 1
            self.estado = 1
        # botao avancar
        self.imagem_avancar = pygame.image.load(
            "VesTEA/images/button_avancar.png"
        ).convert_alpha()
        self.botao_avancar = Botao(500, 410, self.imagem_avancar, 0.15)
        if self.botao_avancar.criar(self.superficie):
            print("avancar")
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Avancar Nivel",
            )
            self.acoesAvancaNivel()
            self.jogando = True
            self.posicaoJogador = "0"
            self.jogada = 1
            self.estado = 1

        # botão SAIR
        self.imagem_sair = pygame.image.load(
            "VesTEA/images/button_sair.png"
        ).convert_alpha()
        self.botao_sair = Botao(340, 500, self.imagem_sair, 1)
        if self.botao_sair.criar(self.superficie):
            arq.grava_Detalhado(
                self.fase,
                self.nivel,
                self.posicaoJogador,
                "Acao profissional",
                "Botao Sair para Menu",
            )
            if self.trofeu == 1:
                self.acoesVoltaNivel()
            elif self.trofeu == 3:
                self.acoesAvancaNivel()
            self.cap.close_camera()
            self.posicaoJogador = "0"
            self.estado = 99
            self.jogando = True

    def update(self):
        if self.jogando == True:

            if self.estado == 99:
                print("volta pro menu")

            if self.estado == 1:
                # carrega dados
                print("Carregando dados...")
                self.carregaDados()

            elif self.estado == 2:
                # carrega tela
                # print("Carregando tela...")
                self.carregaTelaJogo()

            elif self.estado == 3:
                # carrega inicio da partida
                print("Carregando partida...")
                self.carregaPartida()

            elif self.estado == 4:
                # carrega jogada (movimento, colisão...)
                # print("Jogando...")
                self.gerenciaJogo()

            elif self.estado == 5:
                # carrega pós jogada
                print("Carregando resultado...")
                self.verificaResultado()

            elif self.estado == 6:
                # exibe roupas certas
                print("Exibe roupas certas...")
                self.exibeRoupasCertas()

            elif self.estado == 7:
                # executa pós jogada (ações de acerto/erro e próx jogada ou fim de nível)
                print("Trocando a jogada...")
                self.finalizaJogada()

        elif self.jogando == False:
            # pausa
            if self.estado == 7 and self.jogada == 3:
                self.carregaTelaFeedback()
            else:
                # print("Pausa...")
                self.carregaTelaPausa()

    def setSuperficie(self, superficie):
        print("superficie")
        self.superficie = superficie
        # self.cap.__init__()

    # verificação para ver se tem desafios suficientes para jogar a fase
    def verificaDesafiosDisponiveis(self, fase):
        desafiosindisponiveis = 0
        if self.configDesafio.corpo["nenhum"] == True:
            desafiosindisponiveis = desafiosindisponiveis + 1
        if self.configDesafio.clima["nenhum"] == True:
            desafiosindisponiveis = desafiosindisponiveis + 1
        if self.configDesafio.ocasiao["nenhum"] == True:
            desafiosindisponiveis = desafiosindisponiveis + 1
        if (
            (fase == 1 and desafiosindisponiveis > 2)
            or (fase == 2 and desafiosindisponiveis > 1)
            or (fase == 3 and desafiosindisponiveis > 0)
        ):
            return False
        else:
            return True
