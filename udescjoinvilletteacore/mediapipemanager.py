from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from udescjoinvilletteaservice import CalibrationService
from udescjoinvilletteautil import PathConfig


class MediaPipeManager:
    def __init__(self):
        # 1. Detecção de Hardware e Sistema
        self.service = CalibrationService()
        self.is_rpi = self.service.is_raspberry_pi()
        self.is_windows = self.service.is_windows()

        # 2. Definição de Caminhos
        path_full = PathConfig.model_path("pose_landmarker_full.task")
        path_heavy = PathConfig.model_path("pose_landmarker_heavy.task")
        # path_full = PathConfig.model_path("pose_landmarker_lite.task")
        # path_heavy = PathConfig.model_path("pose_landmarker_lite.task")

        # 3. Lógica de Seleção de Modelo e Delegate
        if self.is_windows:
            # No Windows/PC, usamos o modelo Heavy para máxima precisão.
            # O Delegate deve ser CPU para evitar erros de compatibilidade com Python.
            self.delegate = python.BaseOptions.Delegate.CPU
            self.model_path = path_heavy
        elif self.is_rpi:
            # No Raspberry Pi, usamos o modelo Full (mais leve) para manter o FPS estável.
            self.delegate = python.BaseOptions.Delegate.CPU
            self.model_path = path_full
        else:
            self.model_path = path_heavy
            try:
                self.delegate = python.BaseOptions.Delegate.GPU
            except Exception:
                self.delegate = python.BaseOptions.Delegate.CPU

        # 4. Inicialização do Detector com Parâmetros Equilibrados
        base_options = python.BaseOptions(
            model_asset_path=self.model_path, delegate=self.delegate
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            # min_pose_detection_confidence: Rigor para detectar a pessoa pela primeira vez.
            # 0.5 evita "fantasmas" em sombras sem ser exigente demais com câmeras simples.
            min_pose_detection_confidence=0.5,
            # min_pose_detection_confidence=0.55,
            # min_pose_presence_confidence: Certeza de que o corpo ainda está na imagem.
            min_pose_presence_confidence=0.5,
            # min_tracking_confidence: Estabilidade dos pontos entre os frames.
            # 0.5 garante que o pé não "pule" em câmeras com ruído, mantendo a precisão.
            min_tracking_confidence=0.5,
            # min_tracking_confidence=0.6,
            num_poses=1,
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def detect(self, mp_image, timestamp_ms):
        """Executa a detecção de pose para um frame de vídeo."""
        return self.detector.detect_for_video(mp_image, timestamp_ms)
