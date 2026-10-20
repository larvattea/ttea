"""Entry point of Herpules 2: creates and runs the game.

Notes
-----
The modules are imported by plain name (``from controller import
...``), so the game must run with its folder as the current
directory, as ``PlayerGameLaunchController`` does. The platform's
``--lang``, ``--player_id`` and ``--professional_id`` arguments are not
read.
"""

from controller import GameController

if __name__ == "__main__":
    jogo = GameController()
    jogo.run()
