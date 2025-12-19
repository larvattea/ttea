# udescjoinvillettea/mvcs/model/appmodel.py
from typing import Optional


class AppModel:
    """Estado global da aplicação (sessão ativa)."""

    def __init__(self):
        from udescjoinvilletteamodel import Language

        self.current_language: Optional[str] = None
        self.current_player_id: Optional[int] = None
        self.language_model = Language()  # usado apenas no LanguageController
