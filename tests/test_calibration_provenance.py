import csv
import logging
from pathlib import Path
from shutil import copytree
import tempfile
import unittest

import numpy as np
from PySide6.QtCore import QSettings

from ttea.dao.calibrationpointcsvdao import CalibrationPointCsvDAO
from ttea.model.calibrationpoint import CalibrationPoint
from ttea.util import PathConfig


class CalibrationProvenanceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.addCleanup(self.close_log_file)
        self.addCleanup(PathConfig.set_base_dir, PathConfig.BASE_DIR)
        self.root = Path(temporary.name)

    @staticmethod
    def close_log_file():
        logger = logging.getLogger("Log")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def points(self, mirrored=False):
        xs = (639, -1) if mirrored else (0, 640)
        return CalibrationPoint(xs[0], 0, xs[1], 0, xs[0], 480, xs[1], 480,
                                capture_method="manual", coordinate_space="mirror-pixel" if mirrored else "raw",
                                corner_order="tl-tr-bl-br", capture_width=640, capture_height=480)

    def test_mirrored_pixel_capture_projects_like_raw_capture(self):
        raw = self.points().runtime_calibration()
        mirrored = self.points(True).runtime_calibration()
        np.testing.assert_allclose(raw["homography"], mirrored["homography"], atol=1e-7)
        matrix = np.array(mirrored["homography"])
        for source, expected in [((0, 0, 1), (0, 0)), ((1, 1, 1), (1, 1)),
                                 ((0.25, 0.75, 1), (0.25, 0.75)), ((-0.2, 0.5, 1), (-0.2, 0.5))]:
            projected = matrix @ source
            np.testing.assert_allclose(projected[:2] / projected[2], expected, atol=1e-7)

    def test_charuco_projector_corners_map_without_an_extra_reflection(self):
        points = CalibrationPoint(100, 50, 500, 50, 100, 450, 500, 450,
                                  capture_method="charuco", coordinate_space="raw",
                                  corner_order="tl-tr-bl-br", capture_width=640, capture_height=480)
        matrix = np.array(points.runtime_calibration()["homography"])
        for source, expected in [((100 / 640, 50 / 480, 1), (0, 0)),
                                 ((500 / 640, 450 / 480, 1), (1, 1)),
                                 ((300 / 640, 250 / 480, 1), (0.5, 0.5))]:
            projected = matrix @ source
            np.testing.assert_allclose(projected[:2] / projected[2], expected, atol=1e-7)

    def test_unknown_legacy_and_degenerate_points_require_recalibration(self):
        with self.assertRaisesRegex(ValueError, "provenance"):
            CalibrationPoint(0, 0, 640, 0, 0, 480, 640, 480).runtime_calibration()
        points = self.points()
        points.pointx2 = points.pointx1
        with self.assertRaisesRegex(ValueError, "degenerate"):
            points.runtime_calibration()

    def test_persistence_retains_signed_coordinates_and_capture_provenance(self):
        PathConfig.set_base_dir(self.root)
        CalibrationPointCsvDAO().insert(self.points(True))
        restored = CalibrationPointCsvDAO().select(1)
        self.assertEqual(restored, self.points(True))
        np.testing.assert_allclose(restored.runtime_calibration()["homography"], np.eye(3))

    def test_documented_migration_preserves_legacy_and_refuses_existing_target(self):
        legacy, target = self.root / "legacy", self.root / "target"
        (legacy / "calibration").mkdir(parents=True)
        (legacy / "config").mkdir()
        points_file = legacy / "calibration" / PathConfig.CALIBRATION_POINT_FILENAME
        with points_file.open("w", newline="") as stream:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(CalibrationPoint.PROPERTIES[:8])
            writer.writerow([0, 0, 640, 0, 0, 480, 640, 480])
        config = legacy / "config" / PathConfig.CONFIG_FILENAME
        config.write_text("[synthetic]\nlanguage=en\n", encoding="utf-8")
        before = {p.relative_to(legacy): p.read_bytes() for p in legacy.rglob("*") if p.is_file()}
        copytree(legacy, target)
        PathConfig.set_base_dir(target)
        loaded = CalibrationPointCsvDAO().select(1)
        self.assertEqual(loaded.capture_method, "unknown")
        with self.assertRaisesRegex(ValueError, "provenance"):
            loaded.runtime_calibration()
        settings = QSettings(str(target / "config" / PathConfig.CONFIG_FILENAME), QSettings.IniFormat)
        self.assertEqual(settings.value("synthetic/language"), "en")
        target_config = target / "config" / PathConfig.CONFIG_FILENAME
        target_config.write_text("[synthetic]\nlanguage=pt\n", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            copytree(legacy, target)
        self.assertEqual(target_config.read_text(), "[synthetic]\nlanguage=pt\n")
        self.assertEqual(before, {p.relative_to(legacy): p.read_bytes() for p in legacy.rglob("*") if p.is_file()})
        self.assertEqual(points_file.read_bytes(), (target / "calibration" / PathConfig.CALIBRATION_POINT_FILENAME).read_bytes())


if __name__ == "__main__":
    unittest.main()
