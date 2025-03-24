import customtkinter as ctk
from tkinter.ttk import Separator
from os import listdir
from PIL import Image, ImageTk
from CTkMenuBar import menu_bar


class SidebarFrame(ctk.CTkFrame): 
    def __init__(self, master, games): 
        super().__init__(master)
        

        self.rowconfigure((0,1,2,3,4,5),weight=1) 

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._corner_radius = 0


        image = Image.open(r"menu_assets\ttea-logo.png")
        image = ImageTk.PhotoImage(image)

        self.label_title = ctk.CTkLabel(self,image= image, text = None)
        self.label_title.grid(row=0, column = 0, padx = 20)
        self.button = []

        print(self.size())

        home = ctk.CTkButton(self,text="Cadastro", font=(20,20)) 
        home.grid(row = 1, column = 0, padx = 50, sticky = "ew")
        self.button.append(home)


        for _ in games:
            temp = ctk.CTkButton(self,text=_, font=(20,20))
            temp.grid(row= games.index(_)+2, column = 0,  padx = 50, sticky = "ew")
            self.button.append(temp)



class MenuSettings(ctk.CTkFrame): 
    def __init__(self, master): 
        super().__init__(master)

        self._corner_radius = 0

        self.rowconfigure((0,1,2,3,4), weight = 1)
        self.columnconfigure((0,1), weight = 1)

        self.label_title = ctk.CTkLabel(self, text = "Configurações da Interface", font=(20,20))
        self.label_title.grid(row = 0, column = 0, padx = 5, columnspan =2, sticky = "nsew")


        self.label_scale = ctk.CTkLabel(self, text = "Escala da Interface", font=(15,15))
        self.label_scale.grid(row = 1, column = 0, columnspan = 2, padx = 5, sticky = "s")

        self.menu_scale = ctk.CTkOptionMenu(self, values=["80%", "90%","100%", "110%", "120%"], command=None)
        self.menu_scale.grid(row=2, column = 0, columnspan = 2, padx=50)

        self.label_calibration = ctk.CTkLabel(self, text = "Calibração", font = (15,15))
        self.label_calibration.grid(row = 3, column = 0, columnspan = 2, padx = 5, sticky = "s")

        self.button_auto_cal = ctk.CTkButton(self, text = "Automática")
        self.button_auto_cal.grid(row=4, column = 0, padx = 5, sticky= "e")

        self.button_manual_cal = ctk.CTkButton(self, text = "Manual")
        self.button_manual_cal.grid(row=4, column = 1, padx = 5, sticky= "w")

class RegisterMenu(ctk.CTkFrame): 
     def __init__(self, master): 
        super().__init__(master)

        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight=1)

        self.label_version = ctk.CTkLabel(self, text = "Versão 2.0 - Release 22/03/2025", font = (10,10))
        self.label_version.grid(row = 3, column = 0, columnspan = 2, padx = 5, sticky = "s")


class RepeTEAMenu(ctk.CTkFrame):  

    def __init__(self, master): 
        super().__init__(master)
        
        self._corner_radius = 0

        self.columnconfigure(0, weight= 1)
        self.rowconfigure (0, weight= 1)

        self.nav_bar =  ctk.CTkTabview(self)

        self.nav_bar.add("Jogar")
        self.nav_bar.add("Configurações")
        self.nav_bar.add("Manual")

        self.nav_bar.grid(row =0, column = 0, sticky = "nsew")



class App(ctk.CTk): 
    def __init__(self): 
        super().__init__()


        self.geometry("800x600")
        self.title("T-TEA")
        self.games = listdir(r"Games")

        self.columnconfigure(0, weight= 1)
        self.columnconfigure(1, weight= 9)
        self.rowconfigure ((0,1,2), weight= 5)
        self.rowconfigure(3)


        
        self.sidebar_frame = SidebarFrame(self, self.games)
        self.sidebar_frame.grid(row = 0, column=0, rowspan = 2,  sticky = "nsew")

        self.sidebar_settings = MenuSettings(self)
        self.sidebar_settings.grid(row=2, column=0, sticky = "nsew")

        self.game_menu = RepeTEAMenu(self)
        self.game_menu.grid(row = 0, column = 1, rowspan = 3, sticky = "nsew")

        self.register_form =  RegisterMenu(self)
        self.register_form.grid (row=3, column=0, columnspan=2, sticky = 'e')


app = App()
app.mainloop()


    