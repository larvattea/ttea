from udescjoinvilletteaview.selectplayerview import SelectPlayerView
from udescjoinvilletteaview.registerplayerview import RegisterPlayerView
from udescjoinvilletteacontroller.registerplayercontroller import RegisterPlayerController


class SelectPlayerController():

    def __init__(self, view: SelectPlayerView, parent = None): 

        self.view = view
        self.parent = parent
        self.view.get_insert_button().clicked.connect(self.call_register)
    


    def call_register(self): 
        register =  RegisterPlayerView(self.view)
        controller = RegisterPlayerController(register, self.view)

        register.exec()