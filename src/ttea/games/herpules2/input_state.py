"""Player input of one frame of Herpules 2."""

class InputState:
    """Player input of one game frame.

    Attributes
    ----------
    pular : bool
        Whether the player asked to jump. Default is False.
    abaixar : bool
        Whether the player is crouching. Default is False.
    """

    def __init__(self):
        self.pular = False
        self.abaixar = False
