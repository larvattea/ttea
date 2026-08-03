import cv2
import numpy as np
import csv
import json
import os
import sys
import time
from screeninfo import get_monitors


def _camera_selecionada():
    # Preferencia: settings.CAMERA (quando chamado de dentro do T-TEA, o
    # modulo settings ja esta carregado com a escolha feita na engrenagem).
    try:
        import settings
        return settings.CAMERA
    except Exception:
        pass
    # Uso standalone (fora do T-TEA): le o config.json diretamente.
    base = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    candidatos = [
        os.path.join(base, 'config.json'),
        os.path.join(base, 'Source', 'config.json'),
    ]
    for caminho in candidatos:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return int(json.load(f).get('camera', 0))
        except Exception:
            continue
    return 0


def executar():
    # ==========================
    # 1. DETECÇÃO DO PROJETOR VIA SCREENINFO
    # ==========================
    camera_index = _camera_selecionada()
    monitors = get_monitors()
    try:
        import settings
        indice_projetor = settings.MONITOR if 0 <= settings.MONITOR < len(monitors) else 0
    except Exception:
        indice_projetor = 1 if len(monitors) > 1 else 0
    projector = monitors[indice_projetor]
    # A janela de controle (CALIBRACAO_CAMERA) vai no monitor oposto ao do
    # projetor, para o operador nao perder o ChArUco projetado de vista.
    indice_operador = next((i for i in range(len(monitors)) if i != indice_projetor), indice_projetor)
    operador = monitors[indice_operador]

    PROJ_LARGURA = projector.width
    PROJ_ALTURA = projector.height

    # ==========================
    # 2. CONFIGURAÇÃO DO CHARUCO SEM MARGENS
    # ==========================
    COLS = 6
    ROWS = 4

    SQUARE_WIDTH = PROJ_LARGURA // COLS
    SQUARE_HEIGHT = PROJ_ALTURA // ROWS
    SQUARE_SIZE_AVERAGE = (SQUARE_WIDTH + SQUARE_HEIGHT) / 2
    MARKER_SIZE = int(SQUARE_SIZE_AVERAGE * 0.75)

    # opencv-contrib-python==4.5.4.60 (versao usada no build, para manter
    # compatibilidade com Windows 7) so tem a API "antiga" do aruco: sem
    # ArucoDetector, sem CharucoBoard(...)/generateImage - usa as funcoes
    # *_create() e module-level detectMarkers().
    aruco = cv2.aruco
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
    board = aruco.CharucoBoard_create(COLS, ROWS, SQUARE_SIZE_AVERAGE, MARKER_SIZE, dictionary)

    base_img = board.draw((COLS * 100, ROWS * 100), marginSize=0)
    board_img = cv2.resize(base_img, (PROJ_LARGURA, PROJ_ALTURA), interpolation=cv2.INTER_NEAREST)

    # ==========================
    # 3. CONFIGURAÇÃO DA CÂMERA USB
    # ==========================
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Não foi possível abrir a câmera USB (índice {camera_index}).")
        return

    deteccao_params = aruco.DetectorParameters_create()

    def detectar_marcadores(gray):
        return aruco.detectMarkers(gray, dictionary, parameters=deteccao_params)

    # ==========================
    # 4. CONFIGURAÇÃO DAS JANELAS
    # ==========================
    nome_janela_proj = "CHARUCO_BOARD"
    cv2.namedWindow(nome_janela_proj, cv2.WINDOW_NORMAL)
    cv2.moveWindow(nome_janela_proj, projector.x, projector.y)
    cv2.setWindowProperty(nome_janela_proj, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    nome_janela_cam = "CALIBRACAO_CAMERA"
    cv2.namedWindow(nome_janela_cam, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(nome_janela_cam, operador.x, operador.y)

    print("\n=======================================================")
    print("SISTEMA DE CALIBRAÇÃO CONFIGURADO E PRONTO")
    print("=======================================================\n")

    ultimos_vertices_camera = None
    modo_preview = False
    frame_congelado = None

    # ==========================
    # 5. LOOP DE CALIBRAÇÃO
    # ==========================
    while True:
        if not modo_preview:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejected = detectar_marcadores(gray)

            if ids is not None:
                try:
                    retval, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(
                        corners, ids, gray, board
                    )

                    if retval >= 4:
                        src_points = []
                        dst_points = []
                        chess_corners = board.chessboardCorners

                        for corner_id, detected_corner in zip(charucoIds.flatten(), charucoCorners):
                            world_pt = chess_corners[corner_id][:2]

                            quadrados_x = world_pt[0] / SQUARE_SIZE_AVERAGE
                            quadrados_y = world_pt[1] / SQUARE_SIZE_AVERAGE

                            pixel_x = quadrados_x * SQUARE_WIDTH
                            pixel_y = quadrados_y * SQUARE_HEIGHT

                            src_points.append([pixel_x, pixel_y])
                            dst_points.append(detected_corner[0])

                        src_points = np.array(src_points, dtype=np.float32)
                        dst_points = np.array(dst_points, dtype=np.float32)

                        H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

                        if H is not None:
                            rect_expandido = np.array([
                                [0, 0], [PROJ_LARGURA, 0], [0, PROJ_ALTURA], [PROJ_LARGURA, PROJ_ALTURA]
                            ], dtype=np.float32)

                            rect_expandido = rect_expandido.reshape(-1, 1, 2)
                            projected = cv2.perspectiveTransform(rect_expandido, H)
                            ultimos_vertices_camera = np.round(projected.reshape(4, 2)).astype(int)

                            # Renderização temporária na tela (em tempo real)
                            render_pts = np.array([
                                ultimos_vertices_camera[0], ultimos_vertices_camera[1],
                                ultimos_vertices_camera[3], ultimos_vertices_camera[2]
                            ], dtype=np.int32)

                            cv2.polylines(frame, [render_pts], True, (0, 255, 255), 4)
                            for pt in ultimos_vertices_camera:
                                cv2.circle(frame, (pt[0], pt[1]), 10, (0, 0, 255), -1)

                except Exception as e:
                    pass

            frame_exibicao = frame.copy()
            cv2.putText(frame_exibicao, "Pressione 'S' para ocultar a tela e capturar", (22, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame_exibicao, "Pressione 'S' para ocultar a tela e capturar", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)

        else:
            frame_exibicao = frame_congelado.copy()
            cv2.putText(frame_exibicao, "PREVIEW: ESC p/ ACEITAR e SALVAR | 'R' p/ REPETIR", (22, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame_exibicao, "PREVIEW: ESC p/ ACEITAR e SALVAR | 'R' p/ REPETIR", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

        # Exibe a janela do projetor e a de controle da câmera (se visível)
        cv2.imshow(nome_janela_proj, board_img)
        if cv2.getWindowProperty(nome_janela_cam, cv2.WND_PROP_VISIBLE) >= 0:
            cv2.imshow(nome_janela_cam, frame_exibicao)

        tecla = cv2.waitKey(1)

        # --- AÇÃO S: GATILHO DE FECHAMENTO E CAPTURA LIMPA ---
        if (tecla == ord('s') or tecla == ord('S')) and not modo_preview:
            print("\n[AÇÃO] Ocultando janela de controle para limpeza de projeção...")

            # 1. Fecha a janela da câmera para liberar o espaço visual do ChArUco
            cv2.destroyWindow(nome_janela_cam)
            cv2.waitKey(1)

            # 2. Espera 1 segundo para a iluminação estabilizar
            time.sleep(1.0)

            # 3. Limpa buffers antigos e tira a foto limpa real
            for _ in range(5):
                cap.read()
            ret, frame_limpo = cap.read()

            if ret:
                gray = cv2.cvtColor(frame_limpo, cv2.COLOR_BGR2GRAY)
                corners, ids, rejected = detectar_marcadores(gray)

                if ids is not None:
                    try:
                        retval, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(
                            corners, ids, gray, board
                        )

                        if retval >= 4:
                            src_points = []
                            dst_points = []
                            chess_corners = board.chessboardCorners

                            for corner_id, detected_corner in zip(charucoIds.flatten(), charucoCorners):
                                world_pt = chess_corners[corner_id][:2]
                                quadrados_x = world_pt[0] / SQUARE_SIZE_AVERAGE
                                quadrados_y = world_pt[1] / SQUARE_SIZE_AVERAGE
                                pixel_x = quadrados_x * SQUARE_WIDTH
                                pixel_y = quadrados_y * SQUARE_HEIGHT
                                src_points.append([pixel_x, pixel_y])
                                dst_points.append(detected_corner[0])

                            src_points = np.array(src_points, dtype=np.float32)
                            dst_points = np.array(dst_points, dtype=np.float32)
                            H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

                            if H is not None:
                                rect_expandido = np.array([
                                    [0, 0], [PROJ_LARGURA, 0], [0, PROJ_ALTURA], [PROJ_LARGURA, PROJ_ALTURA]
                                ], dtype=np.float32)
                                rect_expandido = rect_expandido.reshape(-1, 1, 2)
                                projected = cv2.perspectiveTransform(rect_expandido, H)
                                ultimos_vertices_camera = np.round(projected.reshape(4, 2)).astype(int)

                                # Desenha o polígono no frame congelado
                                render_pts = np.array([
                                    ultimos_vertices_camera[0], ultimos_vertices_camera[1],
                                    ultimos_vertices_camera[3], ultimos_vertices_camera[2]
                                ], dtype=np.int32)

                                cv2.polylines(frame_limpo, [render_pts], True, (0, 255, 255), 4)
                                for pt in ultimos_vertices_camera:
                                    cv2.circle(frame_limpo, (pt[0], pt[1]), 10, (0, 0, 255), -1)

                                # Adiciona as siglas originais (referentes à imagem real) para validação visual
                                rotulos = [
                                    ("SE", ultimos_vertices_camera[0], (-25, -15)),
                                    ("SD", ultimos_vertices_camera[1], (15, -15)),
                                    ("IE", ultimos_vertices_camera[2], (-25, 25)),
                                    ("ID", ultimos_vertices_camera[3], (15, 25))
                                ]
                                for texto, pt, offset in rotulos:
                                    pos_x = pt[0] + offset[0]
                                    pos_y = pt[1] + offset[1]
                                    cv2.putText(frame_limpo, texto, (pos_x, pos_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
                                    cv2.putText(frame_limpo, texto, (pos_x, pos_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2, cv2.LINE_AA)

                                frame_congelado = frame_limpo.copy()
                                modo_preview = True
                                print("[SUCESSO] Captura realizada sem obstruções. Janela restaurada em modo PREVIEW.")
                    except Exception as e:
                        print(f"[ERRO NO PROCESSAMENTO]: {e}")

                if not modo_preview:
                    print("[AVISO] O Tabuleiro não pôde ser lido na foto limpa. Retornando ao tempo real...")

                cv2.namedWindow(nome_janela_cam, cv2.WINDOW_AUTOSIZE)
                cv2.moveWindow(nome_janela_cam, operador.x, operador.y)

        # --- AÇÃO R: VOLTA AO RASTREAMENTO REAL ---
        elif (tecla == ord('r') or tecla == ord('R')) and modo_preview:
            modo_preview = False
            frame_congelado = None
            print("[REPETIR] Captura descartada. Rastreamento reativado.")

        # --- AÇÃO ESC: SALVA OU FECHA ---
        elif tecla == 27:
            if modo_preview:
                nome_arquivo = "calibracao.csv"

                # Obtém a largura da resolução atual da câmera para computar o rebatimento horizontal do pixel
                largura_cam = frame_congelado.shape[1]

                with open(nome_arquivo, mode='w', newline='') as f:
                    writer = csv.writer(f, delimiter=';')

                    # Cabeçalho padrão original preservado
                    writer.writerow(["Ponto 1 x", "Ponto 1 y", "Ponto 2 x", "Ponto 2 y", "Ponto 3 x", "Ponto 3 y", "Ponto 4 x", "Ponto 4 y"])

                    # MATEMÁTICA DO FLIP NO ARQUIVO:
                    # O jogo lê o CSV esperando os pontos ordenados como (SD, SE, ID, IE) dentro do frame espelhado dele.
                    # Aplicamos (largura_cam - x) para espelhar a posição X e invertemos a ordem dos pares (D <-> E).

                    x_sd_espelhado = largura_cam - int(ultimos_vertices_camera[0][0])  # X do SE físico vira o SD no jogo
                    y_sd_espelhado = int(ultimos_vertices_camera[0][1])

                    x_se_espelhado = largura_cam - int(ultimos_vertices_camera[1][0])  # X do SD físico vira o SE no jogo
                    y_se_espelhado = int(ultimos_vertices_camera[1][1])

                    x_id_espelhado = largura_cam - int(ultimos_vertices_camera[2][0])  # X do IE físico vira o ID no jogo
                    y_id_espelhado = int(ultimos_vertices_camera[2][1])

                    x_ie_espelhado = largura_cam - int(ultimos_vertices_camera[3][0])  # X do ID físico vira o IE no jogo
                    y_ie_espelhado = int(ultimos_vertices_camera[3][1])

                    # Gravação final com o mapeamento rebatido para o jogo legado
                    writer.writerow([
                        x_sd_espelhado, y_sd_espelhado,   # Ponto 1 (Lido pelo jogo como SD)
                        x_se_espelhado, y_se_espelhado,   # Ponto 2 (Lido pelo jogo como SE)
                        x_id_espelhado, y_id_espelhado,   # Ponto 3 (Lido pelo jogo como ID)
                        x_ie_espelhado, y_ie_espelhado    # Ponto 4 (Lido pelo jogo como IE)
                    ])

                print(f"\n[SUCESSO] Calibração recalculada para compatibilidade com Flip Horizontal e salva em '{nome_arquivo}'.")
                break
            else:
                print("\n[INFO] Fechando sem salvar.")
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    executar()
