class ConfigDesafio:
    def __init__(self):
        self.corpo = {
            "nenhum": False,
            "todos": True,
            "1": True,
            "2": True,
            "3": True,
            "4": True,
        }
        self.clima = {"nenhum": False, "todos": True, "1": True, "2": True}
        self.ocasiao = {
            "nenhum": False,
            "todos": True,
            "1": True,
            "2": True,
            "3": True,
            "4": True,
            "5": True,
            "6": True,
            "7": True,
            "8": True,
        }

    def print(self):
        print("Configurações do desafio:")
        print(
            "Corpo: 1 - ",
            self.corpo["1"],
            ", 2 - ",
            self.corpo["2"],
            ", 3 - ",
            self.corpo["3"],
            ", 4 - ",
            self.corpo["4"],
        )
        print("Clima: 1 - ", self.clima["1"], ", 2 - ", self.clima["2"])
        print(
            "Ocasiao: 1 - ",
            self.ocasiao["1"],
            ", 2 - ",
            self.ocasiao["2"],
            ", 3 - ",
            self.ocasiao["3"],
            ", 4 - ",
            self.ocasiao["4"],
            ", 5 - ",
            self.ocasiao["5"],
            ", 6 - ",
            self.ocasiao["6"],
            ", 7 - ",
            self.ocasiao["7"],
            ", 8 - ",
            self.ocasiao["8"],
        )
