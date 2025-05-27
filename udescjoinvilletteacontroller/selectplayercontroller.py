from udescjoinvilletteaview.selectplayerview import SelectPlayerView
from udescjoinvilletteaview.registerplayerview import RegisterPlayerView
from udescjoinvilletteacontroller.registerplayercontroller import RegisterPlayerController
from udescjoinvilletteautil.cvshandler import CSVHandler
from udescjoinvilletteautil.pathconfig import PathConfig


class SelectPlayerController():

    def __init__(self, view: SelectPlayerView, parent = None): 

        self.view = view
        self.parent = parent
    
        self.view.get_insert_button().clicked.connect(self.call_register)
    


    def call_register(self): 
        register =  RegisterPlayerView(self.view)
        controller = RegisterPlayerController(register, self)


        register.exec()


    def update_registers(self):

        self.view.update_table(self.__get_registers())        

    def __get_registers(self): 

        register = CSVHandler()
        return register.get_archives(PathConfig.players_dir)