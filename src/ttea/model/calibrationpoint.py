from dataclasses import dataclass, fields
from typing import ClassVar, Dict, List


def initialize_reflexive(cls):
    """Decorator to statically initialize player reflection data.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with initialized PROPERTIES and DATA_PROPERTIES.

    Notes
    -----
    - Adds the list of field names to `PROPERTIES`.
    - Adds default values of initializable fields to `DATA_PROPERTIES`.
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


@initialize_reflexive
@dataclass
class CalibrationPoint:
    pointx1: int
    pointy1: int
    pointx2: int
    pointy2: int
    pointx3: int
    pointy3: int
    pointx4: int
    pointy4: int

    capture_method: str = "unknown"
    coordinate_space: str = "unknown"
    corner_order: str = "unknown"
    capture_width: int = 0
    capture_height: int = 0

    def runtime_calibration(self) -> Dict:
        """Convert evidenced pixel coordinates to raw-camera normalized projection."""
        import cv2
        import numpy as np

        if (self.capture_method not in ("manual", "charuco")
                or self.coordinate_space not in ("raw", "mirror-pixel")
                or self.corner_order != "tl-tr-bl-br"
                or self.capture_width <= 0 or self.capture_height <= 0):
            raise ValueError("Calibration provenance is unknown; recalibrate before launching.")
        source = np.array([
            [getattr(self, f"pointx{i}"), getattr(self, f"pointy{i}")]
            for i in range(1, 5)
        ], dtype=np.float32)
        if self.coordinate_space == "mirror-pixel":
            source[:, 0] = self.capture_width - 1 - source[:, 0]
        source /= (self.capture_width, self.capture_height)
        target = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(source, target)
        if not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-12:
            raise ValueError("Calibration points are degenerate; recalibrate before launching.")
        return {
            "homography": matrix.tolist(),
            "provenance": {
                "capture_method": self.capture_method,
                "coordinate_space": self.coordinate_space,
                "corner_order": self.corner_order,
                "capture_width": self.capture_width,
                "capture_height": self.capture_height,
                "input": "normalized-raw-camera",
                "output": "normalized-projection-top-left",
                "anatomical_labels": "unchanged",
            },
        }

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    ID_VALUE: ClassVar[int] = 1  # Static ID for all calibration points

    def set_data(self, data: Dict) -> None:
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        info = {prop: getattr(self, prop) for prop in self.PROPERTIES}
        return [info]
