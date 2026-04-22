import random
import time

# import arquivo
import cv2
import pygame

from udescjoinvilletteagames.kartea.gamecore import Camera, PoseTracking
from udescjoinvilletteagames.kartea.gamemodel import (Background, Car,
                                                      Obstacle, Target)
from udescjoinvilletteagames.kartea.gameui import UI

# import settings
# from settings import *


class GameController:
    """Classe principal responsável pela lógica do jogo KarTEA."""

    def __init__(self, surface):
        self.surface = surface

        # Componentes principais
        self.background = Background()
        self.pose_tracking = PoseTracking()
        self.car = Car()
        self.cap = Camera()

        # Configuração do jogador
        self.config = f"Jogadores/{arquivo.get_Player()}_KarTEA_config.csv"

        # Sons
        self.sounds = {}
        self._load_sounds()

        # Configurações baseadas no nível
        self._setup_level_settings()

        # Variáveis de jogo
        self.targets = []
        self.Last_Obj = -1
        self.targets_spawn_timer = 0

        self.score = 0
        self.movimento = 0
        self.alvo = 0
        self.alvo_c = 0
        self.alvo_d = 0
        self.obst = 0
        self.obst_c = 0
        self.obst_d = 0
        self.finish = 0

        self.SOM = arquivo.get_K_SOM(self.config)
        self.HUD = arquivo.get_K_HUD(self.config)
        self.PAUSE = False

        self.game_start_time = time.time()
        self.time_left = settings.GAME_DURATION

        # Sincroniza variáveis globais de settings
        self._sync_settings()

    def _load_sounds(self):
        """Carrega os sons do jogo."""
        self.sounds["slap"] = pygame.mixer.Sound(
            "Assets/Kartea/Sounds/point.wav"
        )
        self.sounds["screaming"] = pygame.mixer.Sound(
            "Assets/Kartea/Sounds/miss.wav"
        )

        volume = 1 if arquivo.get_K_SOM(self.config) else 0
        self.sounds["slap"].set_volume(volume)
        self.sounds["screaming"].set_volume(volume)

    def _setup_level_settings(self):
        """Configura velocidade e tempo de spawn conforme o nível."""
        settings.TARGETS_MOVE_SPEED = arquivo.get_Nivel()

        if arquivo.get_Nivel() < 3:
            settings.TARGETS_SPAWN_TIME = 8
        elif arquivo.get_Nivel() < 5:
            settings.TARGETS_SPAWN_TIME = 4
        else:
            settings.TARGETS_SPAWN_TIME = 2

    def _sync_settings(self):
        """Sincroniza as variáveis locais com as globais de settings."""
        settings.score = self.score
        settings.movimento = self.movimento
        settings.alvo = self.alvo
        settings.alvo_c = self.alvo_c
        settings.alvo_d = self.alvo_d
        settings.obst = self.obst
        settings.obst_c = self.obst_c
        settings.obst_d = self.obst_d
        settings.TIME_PAST = 0

    def reset(self):
        """Reseta todas as variáveis necessárias para iniciar um novo nível."""
        self.background = Background()
        self.pose_tracking = PoseTracking()
        self.car = Car()

        self._setup_level_settings()

        self.targets = []
        self.Last_Obj = -1
        self.targets_spawn_timer = 0
        self.game_start_time = time.time()
        self.time_left = settings.GAME_DURATION
        settings.TIME_PAST = 0

        self.score = 0
        self.movimento = 0
        self.alvo = 0
        self.alvo_c = 0
        self.alvo_d = 0
        self.obst = 0
        self.obst_c = 0
        self.obst_d = 0
        self.finish = 0

        self._sync_settings()

    def spawn_targets(self):
        """Spawna um novo alvo ou obstáculo conforme a fase e nível."""
        t = time.time()
        if t <= self.targets_spawn_timer:
            return

        self.targets_spawn_timer = t + settings.TARGETS_SPAWN_TIME

        fase = arquivo.get_K_FASE(self.config)
        pos = self.background.get_startPos()

        # Lógica de escolha do tipo de objeto
        if self.Last_Obj == -1:
            r = random.randint(0, 2)
        else:
            r = self.Last_Obj
            if arquivo.get_Nivel() % 2 == 1:
                if r == 0:
                    r = 1
                elif r == 1:
                    while r == self.Last_Obj:
                        r = random.randint(0, 2)
                else:
                    r = 1
            else:
                while r == self.Last_Obj:
                    r = random.randint(0, 2)

        self.Last_Obj = r

        target = Target(r)
        obstacle = Obstacle(r)

        # Adiciona conforme a fase
        if fase == 1:
            self.targets.append(target)
            self.background.lines[pos].target = target
            self.alvo += 1
            settings.Alvo += 1
            arquivo.grava_Detalhado(
                arquivo.get_Player(),
                arquivo.get_Sessao(),
                arquivo.get_Fase(),
                arquivo.get_Nivel(),
                settings.pista,
                r,
                "Criou Alvo",
            )

        elif fase == 2:
            self.targets.append(obstacle)
            self.background.lines[pos].target = obstacle
            self.obst += 1
            settings.Obst += 1
            arquivo.grava_Detalhado(
                arquivo.get_Player(),
                arquivo.get_Sessao(),
                arquivo.get_Fase(),
                arquivo.get_Nivel(),
                settings.pista,
                r,
                "Criou Obstaculo",
            )

        else:  # fase 3
            if random.randint(0, 100) < 50:
                self.targets.append(obstacle)
                self.background.lines[pos].target = obstacle
                self.obst += 1
                settings.Obst += 1
                arquivo.grava_Detalhado(
                    arquivo.get_Player(),
                    arquivo.get_Sessao(),
                    arquivo.get_Fase(),
                    arquivo.get_Nivel(),
                    settings.pista,
                    r,
                    "Criou Obstaculo",
                )
            else:
                self.targets.append(target)
                self.background.lines[pos].target = target
                self.alvo += 1
                settings.Alvo += 1
                arquivo.grava_Detalhado(
                    arquivo.get_Player(),
                    arquivo.get_Sessao(),
                    arquivo.get_Fase(),
                    arquivo.get_Nivel(),
                    settings.pista,
                    r,
                    "Criou Alvo",
                )

    def spawn_finish(self):
        """Coloca a linha de chegada no fundo."""
        pos = self.background.get_startPos()
        self.background.lines[pos].sprite = pygame.image.load(
            "Assets/Kartea/Finish.png"
        ).convert_alpha()
        self.background.lines[pos].spriteX = -0.5

    def load_camera(self):
        """Carrega/atualiza o frame da câmera."""
        self.cap.load_camera()

    def set_feet_position(self):
        """Atualiza a posição do carro com base na posição dos pés detectados."""
        self.cap.frame = self.pose_tracking.scan_feets(self.cap.frame)
        x, y = self.pose_tracking.get_feet_center()
        Y = SCREEN_HEIGHT - CAR_SIZE / 2
        self.car.rect.center = (x, Y)

    def draw(self):
        """Desenha todos os elementos na tela."""
        # Background
        if not self.PAUSE:
            if arquivo.get_Nivel() < 3:
                self.background.speed1()
            elif arquivo.get_Nivel() < 5:
                self.background.speed2()
            else:
                self.background.speed3()
        else:
            self.background.stop()

        self.background.draw(self.surface)

        # Carro
        self.car.draw(self.surface)

        # HUD
        if self.HUD:
            UI.draw_text(
                self.surface,
                f"Pontuação : {self.score}",
                (650, 5),
                COLORS["score"],
                font=FONTS["medium"],
                shadow=True,
                shadow_color=(255, 255, 255),
            )

            timer_text_color = (
                (160, 40, 0) if self.time_left < 5 else COLORS["timer"]
            )
            UI.draw_text(
                self.surface,
                f"Tempo : {self.time_left}",
                (350, 5),
                timer_text_color,
                font=FONTS["medium"],
                shadow=True,
                shadow_color=(255, 255, 255),
            )

            UI.draw_text(
                self.surface,
                f"Fase : {arquivo.get_Fase()}",
                (5, 5),
                timer_text_color,
                font=FONTS["medium"],
                shadow=True,
                shadow_color=(255, 255, 255),
            )

            UI.draw_text(
                self.surface,
                f"Nivel : {arquivo.get_Nivel()}",
                (5, 25),
                timer_text_color,
                font=FONTS["medium"],
                shadow=True,
                shadow_color=(255, 255, 255),
            )

    def game_time_update(self):
        """Atualiza o tempo restante do nível."""
        self.time_left = settings.GAME_DURATION - int(
            settings.TIME_PAST / 1000
        )

    def update(self):
        """Loop principal de atualização do jogo."""
        self.load_camera()
        self.set_feet_position()

        # Verifica pausa
        if self.PAUSE:
            settings.MENU = "Pause"
            self.PAUSE = False
            return "menu"

        self.game_time_update()
        self.draw()

        if self.time_left > 0:
            # Spawn de alvos/obstáculos
            if self.time_left > (2 * settings.TARGETS_SPAWN_TIME):
                self.spawn_targets()
            else:
                if self.finish == 0:
                    self.spawn_finish()
                    self.finish += 1

            # Detecção de pista e movimento
            x, y = self.pose_tracking.get_feet_center()
            feet1_x, feet1_y = self.pose_tracking.get_feet1()
            feet2_x, feet2_y = self.pose_tracking.get_feet2()

            troca_pista = settings.pista

            # Atualiza pista com base nos pés
            if (div0_pista <= feet1_x < div1_pista) and (
                div0_pista <= feet2_x < div1_pista
            ):
                settings.pista = 0
            elif (div1_pista <= feet1_x < div2_pista) and (
                div1_pista <= feet2_x < div2_pista
            ):
                settings.pista = 1
            elif (div2_pista <= feet1_x < div3_pista) and (
                div2_pista <= feet2_x < div3_pista
            ):
                settings.pista = 2
            elif ((feet1_x < div0_pista) and (feet2_x < div0_pista)) or (
                (feet1_x > div3_pista) and (feet2_x > div3_pista)
            ):
                settings.pista = -1

            # Atualiza pista com base na posição central
            if div0_pista <= x < div1_pista:
                settings.pista = 0
            elif div1_pista <= x < div2_pista:
                settings.pista = 1
            elif div2_pista <= x < div3_pista:
                settings.pista = 2
            else:
                settings.pista = -1

            # Verifica troca de pista
            if settings.pista != troca_pista:
                print(f"Trocou da pista {troca_pista} para {settings.pista}")
                if settings.pista != -1 and troca_pista != -1:
                    self.score += 2
                    self.movimento += 1
                    arquivo.grava_Detalhado(
                        arquivo.get_Player(),
                        arquivo.get_Sessao(),
                        arquivo.get_Fase(),
                        arquivo.get_Nivel(),
                        settings.pista,
                        troca_pista,
                        "Trocou de Pista",
                    )
                elif settings.pista == -1:
                    print("Perdeu o Sinal")
                    arquivo.grava_Detalhado(
                        arquivo.get_Player(),
                        arquivo.get_Sessao(),
                        arquivo.get_Fase(),
                        arquivo.get_Nivel(),
                        settings.pista,
                        troca_pista,
                        "Saiu da area do jogo",
                    )
                    self.PAUSE = True
                    settings.pista = 0

            # Atualiza posição do carro e interação com alvos
            self.car.rect.center = (x, y)
            self.car.left_click = self.pose_tracking.feet_closed
            self.score = self.car.kill_targets(
                self.surface, self.targets, self.score, self.sounds
            )

            # Remove alvos que saíram da tela
            for alvo in self.targets[:]:
                if alvo.current_pos[1] > (SCREEN_HEIGHT + 100):
                    self.score += alvo.kill(
                        self.surface, self.targets, self.sounds
                    )

        else:
            # Fim do nível - Feedback
            print("Terminou o Nível!")

            ponto_T = self.alvo * 12 + self.obst * 12

            if self.score >= (3 * ponto_T) / 4:
                arquivo.grava_Detalhado(
                    arquivo.get_Player(),
                    arquivo.get_Sessao(),
                    arquivo.get_Fase(),
                    arquivo.get_Nivel(),
                    settings.pista,
                    settings.pista,
                    "Controle Jogo: Avanca Nivel",
                )
                settings.MENU = "Feedback_3"
            elif self.score >= ponto_T / 4:
                arquivo.grava_Detalhado(
                    arquivo.get_Player(),
                    arquivo.get_Sessao(),
                    arquivo.get_Fase(),
                    arquivo.get_Nivel(),
                    settings.pista,
                    settings.pista,
                    "Controle Jogo: Permanece Nivel",
                )
                settings.MENU = "Feedback_2"
            else:
                arquivo.grava_Detalhado(
                    arquivo.get_Player(),
                    arquivo.get_Sessao(),
                    arquivo.get_Fase(),
                    arquivo.get_Nivel(),
                    settings.pista,
                    settings.pista,
                    "Controle Jogo: Retrocede Nivel",
                )
                settings.MENU = "Feedback_1"

            # Gravação final da sessão
            settings.score = self.score
            settings.movimento = self.movimento
            arquivo.grava_Sessao(
                arquivo.get_Player(),
                arquivo.get_Fase(),
                arquivo.get_Nivel(),
                self.score,
                self.movimento,
                settings.Alvo_c,
                settings.Alvo_d,
                settings.Obst_c,
                settings.Obst_d,
            )

            return "menu"

        # Eventos do Pygame (mantidos originais)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Space game.py")
                    if self.background.speed == 0:
                        self.PAUSE = False
                        print("Unpause")
                        arquivo.grava_Detalhado(
                            arquivo.get_Player(),
                            arquivo.get_Sessao(),
                            arquivo.get_Fase(),
                            arquivo.get_Nivel(),
                            settings.pista,
                            settings.pista,
                            "Controle UFE: Unpause",
                        )
                    else:
                        self.PAUSE = True
                        print("Pause")
                        arquivo.grava_Detalhado(
                            arquivo.get_Player(),
                            arquivo.get_Sessao(),
                            arquivo.get_Fase(),
                            arquivo.get_Nivel(),
                            settings.pista,
                            settings.pista,
                            "Controle UFE: Pause",
                        )
                        self.background.stop()
                        settings.MENU = "Pause"
                        return "menu"

                # Atalhos de som e HUD (mantidos exatamente como no original)
                if event.key in (pygame.K_s, pygame.K_1):
                    self.SOM = not self.SOM
                    volume = 1 if self.SOM else 0
                    self.sounds["slap"].set_volume(volume)
                    self.sounds["screaming"].set_volume(volume)
                    arquivo.set_K_SOM(self.config, self.SOM)
                    status = "Habilita Som" if self.SOM else "Desabilita Som"
                    arquivo.grava_Detalhado(
                        arquivo.get_Player(),
                        arquivo.get_Sessao(),
                        arquivo.get_Fase(),
                        arquivo.get_Nivel(),
                        settings.pista,
                        settings.pista,
                        f"Controle UFE: {status}",
                    )

                if event.key in (pygame.K_h, pygame.K_2):
                    self.HUD = not self.HUD
                    arquivo.set_K_HUD(self.config, self.HUD)
                    status = "Habilita HUD" if self.HUD else "Desabilita HUD"
                    arquivo.grava_Detalhado(
                        arquivo.get_Player(),
                        arquivo.get_Sessao(),
                        arquivo.get_Fase(),
                        arquivo.get_Nivel(),
                        settings.pista,
                        settings.pista,
                        f"Controle UFE: {status}",
                    )

        cv2.waitKey(1)
