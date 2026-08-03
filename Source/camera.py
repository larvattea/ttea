import cv2
import numpy as np
import settings
import ttea_log

class Camera:
    def __init__(self):
        # Load camera
        self.cap = cv2.VideoCapture(settings.CAMERA, cv2.CAP_DSHOW)
        ttea_log.debug(f'Camera {settings.CAMERA}: aberta={self.cap.isOpened()}')
        self._falhas = 0
        self._janela_posicionada = False
        self.ret, self.frame = self.cap.read()
        if not self.ret or self.frame is None:
            # Sem imagem: usa um frame preto para o jogo nao travar.
            ttea_log.debug(f'Camera {settings.CAMERA}: sem imagem no primeiro frame')
            self.ret = False
            self.frame = np.zeros((settings.altura_tela_controle, settings.largura_tela_controle, 3), np.uint8)
        else:
            altura, largura = self.frame.shape[:2]
            ttea_log.debug(f'Camera {settings.CAMERA}: capturando em {largura}x{altura}')

    def load_camera(self):
        ret, frame = self.cap.read()
        if ret and frame is not None:
            self.ret = True
            self.frame = cv2.flip(frame, 1)
        else:
            # Mantem o ultimo frame valido para o jogo continuar rodando.
            self._falhas += 1
            if self._falhas == 1 or self._falhas % 300 == 0:
                ttea_log.debug(f'Camera {settings.CAMERA}: falha ao ler frame (total={self._falhas})')
        # Desenha a borda da area de calibração
        cv2.line(self.frame, (settings.pontos_calibracao[0]), (settings.pontos_calibracao[1]), (settings.verde), 2)
        cv2.line(self.frame, (settings.pontos_calibracao[1]), (settings.pontos_calibracao[3]), (settings.verde), 2)
        cv2.line(self.frame, (settings.pontos_calibracao[2]), (settings.pontos_calibracao[0]), (settings.verde), 2)
        cv2.line(self.frame, (settings.pontos_calibracao[2]), (settings.pontos_calibracao[3]), (settings.verde), 2)

        cv2.circle(self.frame, (settings.pontos_calibracao[0]), 5, settings.azul, 3)
        cv2.circle(self.frame, (settings.pontos_calibracao[1]), 5, settings.azul, 3)
        cv2.circle(self.frame, (settings.pontos_calibracao[2]), 5, settings.azul, 3)
        cv2.circle(self.frame, (settings.pontos_calibracao[3]), 5, settings.azul, 3)

    def show(self):
        # Chamado DEPOIS do rastreamento de pose (que desenha o esqueleto em
        # cima de self.frame) - se fosse chamado dentro de load_camera(), o
        # esqueleto so apareceria um frame atrasado (nunca, na pratica, ja
        # que o proximo load_camera() sobrescreve self.frame antes de exibir).
        cv2.imshow("Tela de Captura", self.frame)
        if not self._janela_posicionada:
            # A janela do operador vai sempre no monitor oposto ao da
            # projecao do jogo (settings.MONITOR), para nao sobrepor.
            cv2.moveWindow("Tela de Captura", *settings.janela_operador_pos())
            self._janela_posicionada = True

    def close_camera(self):
        self.cap.release()
        cv2.destroyWindow("Tela de Captura")
