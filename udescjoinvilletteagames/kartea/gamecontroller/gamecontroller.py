import random
import sys
import time

import pygame

from udescjoinvilletteagames.kartea.gamecore import Camera, PoseTracking
from udescjoinvilletteagames.kartea.gamemodel import (
    Background,
    Car,
    Obstacle,
    Target,
)
from udescjoinvilletteagames.kartea.gameui import UI
from udescjoinvilletteagames.kartea.gameutil import GameSettings
from udescjoinvilletteagames.kartea.util import KarteaPathConfig


# TODO aonde tiver chamada de arquivo fazer o acerto de configurações etc
class GameController:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface

        # Componentes principais
        self.settings = GameSettings()
        self.ui = UI()
        self.camera = Camera()
        self.pose_tracking = PoseTracking()
        self.background = Background()
        self.car = Car()

        self.config = (
            ""  # f"Jogadores/{arquivo.get_Player()}_KarTEA_config.csv"
        )

        # Sons
        self.sounds = {
            "slap": pygame.mixer.Sound(
                KarteaPathConfig.game_sound("point.wav")
            ),
            "screaming": pygame.mixer.Sound(
                KarteaPathConfig.game_sound("neutral_feedback/miss.wav")
            ),
            # "slap": pygame.mixer.Sound("Assets/Kartea/Sounds/point.wav"),
            # "screaming": pygame.mixer.Sound("Assets/Kartea/Sounds/miss.wav"),
        }
        self._apply_sound_settings()

        # Configurações de nível
        self._configure_level()

        # Lista de objetos (Targets + Obstacles)
        self.targets: list[Target | Obstacle] = []
        self.Last_Obj = -1

        # Variáveis de jogo
        self.score = 0
        self.move = 0
        self.finish = 0
        self.PAUSE = False
        self.HUD = False  # arquivo.get_K_HUD(self.config)

        # Timers e tempo
        self.targets_spawn_timer = 0
        self.game_start_time = time.time()
        self.time_left = self.settings.GAME_DURATION

    def _apply_sound_settings(self):
        volume = 1.0  # if arquivo.get_K_SOM(self.config) else 0.0
        self.sounds["slap"].set_volume(volume)
        self.sounds["screaming"].set_volume(volume)

    def _configure_level(self):
        nivel = 1  # arquivo.get_Nivel()
        self.settings.TARGETS_MOVE_SPEED = nivel

        if nivel < 3:
            self.settings.TARGETS_SPAWN_TIME = 8
        elif nivel < 5:
            self.settings.TARGETS_SPAWN_TIME = 4
        else:
            self.settings.TARGETS_SPAWN_TIME = 2

    def reset(self):
        """Reinicia todas as variáveis para começar um novo nível."""
        self.background = Background()
        self.car = Car()
        self.pose_tracking = PoseTracking()
        self.camera = Camera() if not hasattr(self, "camera") else self.camera

        self.targets.clear()
        self.Last_Obj = -1
        self.score = 0
        self.move = 0
        self.finish = 0
        self.targets_spawn_timer = 0
        self.time_left = self.settings.GAME_DURATION
        self.PAUSE = False

        self._configure_level()

        # Reseta variáveis globais de settings
        # settings.score = settings.movimento = settings.alvo = 0
        # settings.alvo_c = settings.alvo_d = settings.obst = 0
        # settings.obst_c = settings.obst_d = 0
        self.settings.reset_game_state()

    def spawn_targets(self):
        """Spawna Target ou Obstacle na posição atual da pista."""
        from udescjoinvilletteagames.kartea.gamemodel import Target

        t = time.time()
        if t <= self.targets_spawn_timer:
            return

        self.targets_spawn_timer = t + self.settings.TARGETS_SPAWN_TIME
        fase = 1  # arquivo.get_K_FASE(self.config)
        pos = self.background.get_start_pos_index()

        # Evita repetir a mesma faixa
        r = random.randint(0, 2) if self.Last_Obj == -1 else self.Last_Obj
        while r == self.Last_Obj and self.Last_Obj != -1:
            r = random.randint(0, 2)
        self.Last_Obj = r

        if fase == 1 or (fase > 2 and random.random() < 0.5):
            obj = Target(r)
            self.settings.target += 1
            log_msg = "Criou Alvo"
        else:
            obj = Obstacle(r)
            self.settings.obstacle += 1
            log_msg = "Criou Obstaculo"

        self.targets.append(obj)
        self.background.lines[pos].target = obj

        # arquivo.grava_Detalhado(
        #    arquivo.get_Player(),
        #    arquivo.get_Sessao(),
        #    arquivo.get_Fase(),
        #    arquivo.get_Nivel(),
        #    settings.pista,
        #    r,
        #    log_msg,
        # )

    def spawn_finish(self):
        """Coloca a linha de chegada."""
        pos = self.background.get_start_pos_index()
        self.background.lines[pos].sprite = pygame.image.load(
            "Assets/Kartea/Finish.png"
        ).convert_alpha()
        self.background.lines[pos].sprite_x = -0.5
        self.finish = 1

    def draw(self):
        """Desenha todos os elementos do jogo."""
        if not self.PAUSE:
            self.background.set_speed_by_level(1)  # arquivo.get_Nivel())
        else:
            self.background.stop()

        self.background.draw(self.surface)
        self.car.draw(self.surface)

        if self.HUD:
            self._draw_hud()

    def _draw_hud(self):
        self.ui.draw_text(
            self.surface,
            f"Pontuação : {self.score}",
            (650, 5),
            self.settings.COLORS["score"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        timer_color = (
            (160, 40, 0)
            if self.time_left < 5
            else self.settings.COLORS["timer"]
        )
        self.ui.draw_text(
            self.surface,
            f"Tempo : {self.time_left}",
            (350, 5),
            timer_color,
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        self.ui.draw_text(
            self.surface,
            f"Fase : {1}",  # arquivo.get_Fase()}",
            (5, 5),
            timer_color,
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        self.ui.draw_text(
            self.surface,
            f"Nivel : {1}",  # arquivo.get_Nivel()}",
            (5, 25),
            timer_color,
            shadow=True,
            shadow_color=(255, 255, 255),
        )

    def update(self):
        """Loop principal de atualização do jogo."""
        if self.PAUSE:
            self.settings.MENU = "Pause"
            self.PAUSE = False
            return "menu"

        # === Captura e processamento da câmera + pose ===
        frame = self.camera.load_camera()
        if frame is not None:
            self.pose_tracking.scan_feets(frame)

        # Atualiza posição do carro com base na pose dos pés
        feet_center = self.pose_tracking.get_feet_center()
        self.car.rect.center = (
            feet_center[0],
            self.settings.SCREEN_HEIGHT - 50,
        )  # movimento apenas horizontal

        # Atualiza tempo
        self.time_left = max(
            self.settings.GAME_DURATION - int(self.settings.TIME_PAST / 1000),
            0,
        )

        self.draw()

        if self.time_left > 0:
            # Spawna alvos/obstáculos
            if self.time_left > (2 * self.settings.TARGETS_SPAWN_TIME):
                self.spawn_targets()
            elif self.finish == 0:
                self.spawn_finish()

            # Processa colisões do carro com alvos
            self.score = self.car.kill_targets(
                self.surface, self.targets, self.score, self.sounds
            )

            # Remove objetos que passaram da tela (desvio)
            for obj in self.targets[:]:
                if obj.current_pos[1] > self.settings.SCREEN_HEIGHT + 100:
                    self.score += obj.kill(
                        self.surface,
                        self.targets,
                        self.sounds,
                        player_hit=False,
                    )

        else:
            # Fim do nível
            self._end_level()
            return "menu"

        # Eventos do Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.camera.close_camera()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                self._handle_key_events(event)

        return None

    # TODO rever questão de alvo e obstáculo
    def _end_level(self):
        """Lógica ao terminar o tempo do nível."""
        # t_point = (self.alvo if hasattr(self, "alvo") else 0) * 12 + (
        #    self.obst if hasattr(self, "obst") else 0
        # ) * 12

        t_point = (self.settings.target * 12) + (self.settings.obstacle * 12)

        if self.score >= (3 * t_point) / 4:
            self.settings.MENU = "Feedback_3"
        elif self.score >= t_point / 4:
            self.settings.MENU = "Feedback_2"
        else:
            self.settings.MENU = "Feedback_1"

        self.settings.score = self.score
        self.settings.movimento = self.move

        # Grava sessão (ajuste os parâmetros conforme sua função)
        # arquivo.grava_Sessao(
        #    arquivo.get_Player(),
        #    arquivo.get_Fase(),
        #    arquivo.get_Nivel(),
        #    self.score,
        #    self.move,
        #    self.settings.target_c,
        #    self.settings.target_d,
        #    self.settings.obstacle_c,
        #    self.settings.obstacle_d,
        # )

    def _handle_key_events(self, event):
        """Tratamento de teclas (pausa, som, HUD, etc.)."""
        if event.key == pygame.K_SPACE:
            self.PAUSE = not self.PAUSE
            if self.PAUSE:
                self.background.stop()
                self.settings.MENU = "Pause"
                return "menu"

        # Adicione aqui outras teclas (S, H, 1, 2, etc.) se desejar manter a funcionalidade original

    def close(self):
        """Fecha recursos ao sair do jogo."""
        self.camera.close_camera()
        self.pose_tracking.close()
