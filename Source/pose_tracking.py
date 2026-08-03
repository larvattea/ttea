import cv2
import mediapipe as mp
from settings import *
import numpy as np
import settings as st

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_poses = mp.solutions.pose

def posicao(x, y):
    # Função para determinar a posição do jogador na área de projeçao:
    # Transformação de Perspectiva:
    pts1 = np.float32([pontos_calibracao[0], pontos_calibracao[1], pontos_calibracao[2], pontos_calibracao[3]])
    pts2 = np.float32([[0, 0], [largura_tela_controle, 0], [0, altura_tela_controle], [largura_tela_controle, altura_tela_controle]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    perspectiva = cv2.warpPerspective(tela_de_controle, matrix, (largura_tela_controle, altura_tela_controle))

    # Posição do jogador:
    p = (int(x * largura_tela_controle), int(y * altura_tela_controle))
    position_x = (matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]) / (
        (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    position_y = (matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]) / (
        (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    p_after = (int((position_x) * (relacao_largura)), int((position_y) * (relacao_altura)))
    #print("p_after: ",p_after)
    return p_after


class PoseTracking:
    def __init__(self):
        # model_complexity=0 (BlazePose Lite): bem mais rapido que o padrao
        # (1, "Full"), com perda de precisao pequena - necessario pra rodar
        # bem em computadores mais fracos.
        self.pose_tracking = mp_poses.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0)
        self.feet_x = 0
        self.feet_y = 0
        self.feet1_x = 0
        self.feet1_y = 0
        self.feet2_x = 0
        self.feet2_y = 0
        self.results = None
        self.pose_closed = False
        self.feet_y_livre = 0



    def scan_feets(self, image):
        rows, cols, _ = image.shape

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #image = cv2.cvtColor(cv2.flip(image, -1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        self.results = self.pose_tracking.process(image)

        # Draw the pose annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        self.feet_closed = False

        if self.results.pose_landmarks:
            landmarks = self.results.pose_landmarks.landmark
            pe_esq = landmarks[30]  # left_heel
            pe_dir = landmarks[29]  # right_heel

            # Fallback: se a camera nao enquadra os pes (jogador perto
            # demais, camera alta etc.), o mediapipe reporta visibility
            # baixa nesses pontos - usa o nariz como aproximacao do centro
            # do jogador em vez de deixar a posicao travada/errada.
            if pe_esq.visibility >= 0.5 and pe_dir.visibility >= 0.5:
                self.feet1_x, self.feet1_y = pe_esq.x, pe_esq.y
                self.feet2_x, self.feet2_y = pe_dir.x, pe_dir.y
                x = (self.feet1_x + self.feet2_x) / 2
                y = (self.feet1_y + self.feet2_y) / 2
                self.feet_x, self.feet_y = posicao(x, y)
            else:
                # O frame ja chega espelhado (camera.py faz cv2.flip antes de
                # processar), entao o x do mediapipe ja esta no espelho certo.
                # A calibracao mapeia o plano do CHAO; o nariz esta na altura
                # da cabeca, fora desse plano, e passar ele pela homografia
                # joga o ponto pra fora da tela. Aqui mapeia direto
                # camera -> tela, que da movimento natural nos dois eixos.
                nariz = landmarks[0]
                self.feet1_x = self.feet2_x = nariz.x
                self.feet1_y = self.feet2_y = nariz.y
                self.feet_x = int(nariz.x * SCREEN_WIDTH)
                self.feet_y = int(nariz.y * SCREEN_HEIGHT)
            self.feet_y_livre = self.feet_y  # posicao Y real, sem o travamento usado durante a corrida
            self.feet_y = SCREEN_HEIGHT - 50  # Jogador deve se mover apenas lateralmente

            mp_drawing.draw_landmarks(
                image,
                self.results.pose_landmarks,
                mp_poses.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        return image

    def get_feet_center(self):
        return (self.feet_x, self.feet_y)

    def get_feet_center_menu(self):
        # Posicao dos pes sem o travamento vertical usado durante a corrida -
        # usada para selecionar botoes do menu nos dois eixos.
        return (self.feet_x, self.feet_y_livre)

    def get_feet1(self):
        return posicao(self.feet1_x, self.feet1_y)

    def get_feet2(self):
        return posicao(self.feet2_x, self.feet2_y)

    def display_feet(self):
        cv2.imshow("image", self.image)
        cv2.waitKey(1)

    def is_feet_closed(self):

        pass


