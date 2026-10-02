from datetime import date
import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ttea.games.kartea.service import PlayerKarteaSessionDetailService, PlayerKarteaSessionService
from ttea.sdk.kartea_records import KarteaRecords
from ttea.service import InstitutionFacilityService, PlayerService, ProfessionalService
from ttea.util import PathConfig


class KarteaRecordsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        original = PathConfig.BASE_DIR
        self.addCleanup(PathConfig.set_base_dir, original)
        PathConfig.set_base_dir(self.root)
        self.player = PlayerService().create_player(
            {"id": 0, "name": "Synthetic participant", "birth_date": date(2015, 1, 1), "observation": ""})
        facility = InstitutionFacilityService().create_institutionfacility(
            {"id": 0, "name": "Synthetic facility", "address": "", "phone": "",
             "email": "", "website": "", "social_network": "", "type": 6})
        self.professional = ProfessionalService().create_professional(
            {"id": 0, "name": "Synthetic professional", "type": 20, "institutionfacility": facility})
        self.assertIsNotNone(self.player)
        self.assertIsNotNone(self.professional)

    def defaults(self):
        return {"session_id": None, "phase_id": 1, "level_id": 1, "level_time": 120,
                "vehicle_image": "defaultvehicle", "environment_image_right": "right",
                "environment_image_left": "left", "target_image": "defaultstar",
                "obstacle_image": "defaultobstacle", "positive_feedback_image": "positive",
                "neutral_feedback_image": "neutral", "negative_feedback_image": "negative",
                "positive_feedback_sound": "hit", "neutral_feedback_sound": "miss",
                "negative_feedback_sound": "error", "palette": 0, "hud": True, "sound": True}

    def play(self, score):
        records = KarteaRecords(self.player.id, self.professional.id)
        configuration = records.configuration(self.defaults())
        session = records.start_session({
            "start_date": "01/01/26", "start_time": "10:00:00", "end_date": "01/01/26",
            "end_time": "10:00:00", "phase_reached": 1, "level_reached": 1, "general_score": 0,
            "q_movement": 0, "q_collided_target": 0, "q_avoided_target": 0,
            "q_collided_obstacle": 0, "q_avoided_obstacle": 0})
        records.record_event(session, {
            "date_time": "01/01/26", "event_time": "10:00:01", "phase": 1, "level": 1,
            "player_position": 1, "event_position": 1, "event_type": "Colidiu com Alvo"})
        records.update_session(session, {
            "end_date": "01/01/26", "end_time": "10:02:00", "general_score": score,
            "q_movement": 3, "q_collided_target": 1, "q_avoided_target": 0,
            "q_collided_obstacle": 0, "q_avoided_obstacle": 0})
        records.update_configuration({"session_id": session, "hud": False})
        return configuration, session

    def test_repeated_sessions_persist_to_registered_player_csv(self):
        first_configuration, first = self.play(10)
        second_configuration, second = self.play(20)
        self.assertNotEqual(first, second)
        self.assertTrue(first_configuration["hud"])
        self.assertFalse(second_configuration["hud"])
        sessions = PlayerKarteaSessionService()
        self.assertEqual(sessions.dao.select(first).general_score, 10)
        self.assertEqual(sessions.dao.select(second).general_score, 20)
        details = PlayerKarteaSessionDetailService().dao.list()
        self.assertEqual(sorted(detail.session.id for detail in details), [first, second])
        stored = list((self.root / "exergames" / "kartea" / "players").glob("*"))
        self.assertTrue(stored)

    def test_configuration_updates_accept_only_own_game_settings(self):
        _, session = self.play(10)
        records = KarteaRecords(self.player.id, self.professional.id)
        before = records.configuration(self.defaults())
        for values in ({"player_id": self.player.id + 1, "hud": True},
                       {"session_id": session, "hud": True},
                       {"session_id": session + 99, "hud": True},
                       {"professional_id": 1}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                records.update_configuration(values)
        self.assertEqual(records.configuration(self.defaults()), before)
        records.update_configuration({"hud": True, "level_time": 90})
        after = records.configuration(self.defaults())
        self.assertTrue(after["hud"])
        self.assertEqual(after["level_time"], 90)

    def test_unknown_participant_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "known player"):
            KarteaRecords(self.player.id + 99, self.professional.id)


if __name__ == "__main__":
    unittest.main()
