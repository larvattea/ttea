#NÃO USAR, USAR O POSE_TRACKING

import arquivo
import cv2
import numpy as np


class Jogador():
    def __init__(self, jogo):
        super().__init__()

        self.jogo = jogo
        self.posicao = self.getPosicao()
        self.pontos_calibracao_repetea = arquivo.lerCalibracao()
        print("Pontos de Calibracao do RepeTEA: ", self.pontos_calibracao_repetea)

    def getPosicao(self):
        # Função para determinar a posição do jogador na área de projeçao:
        # Transformação de Perspectiva:
        pts1 = np.float32([self.pontos_calibracao_repetea[0], self.pontos_calibracao_repetea[1], self.pontos_calibracao_repetea[2], self.pontos_calibracao_repetea[3]])
        pts2 = np.float32(
            [[0, 0], [largura_tela_controle, 0], [0, altura_tela_controle], [largura_tela_controle, altura_tela_controle]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        perspectiva = cv2.warpPerspective(tela_de_controle, matrix, (largura_tela_controle, altura_tela_controle))

        # Posição do jogador:
        p = (int(x_pose * largura_tela_controle), int(y_pose * altura_tela_controle))
        position_x = (matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]) / (
        (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
        position_y = (matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]) / (
        (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
        p_after = (int((position_x) * (relacao_largura)), int((position_y) * (relacao_altura)))

        return p_after

    def update(self):
        self.getPosicao()
