from udescjoinvilletteaview.selectplayerview import SelectPlayerView
from udescjoinvilletteacontroller.registerplayercontroller import RegisterPlayerView

class SelectPlayerController():

    def __init__(self, view: SelectPlayerView, parent = None): 

        self.view = view
        self.parent = parent
        self.view.get_insert_button().clicked.connect(self.call_register)

    def call_register(self): 

        register =  RegisterPlayerView(self.view)
        register.exec()