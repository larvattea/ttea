from PySide6.QtWidgets import (QWidget, 
                               QDialog, 
                               QTableWidget,
                               QTableWidgetItem, 
                               QHBoxLayout, 
                               QLabel,
                               QAbstractItemView,
                               QSplitter,
                               QHeaderView,
                               QFormLayout,
                               QLineEdit,
                               QDateEdit,
                               QTextEdit,
                               QPushButton,
                               QLayout,
                               QVBoxLayout)


from PySide6.QtCore import Qt, QDate
from udescjoinvilletteaapp.windowconfig import WindowConfig


class TableView(QTableWidget): 

    def __init__(self, parent = None): 
        
        self.width = 300
        self.height = 300

        super().__init__(parent); 
        self.setRowCount(20)
        self.setColumnCount(3)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setHorizontalHeaderLabels(["ID", "Nome", "Data Nascimento"])
        print(self.row)

    
    def update_table_items(self, item_list):
        
        size = len(item_list)

        for i in range(size):
            for j in range(size): 
                item = QTableWidgetItem(item_list[i])
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(i,j, item)



class RowDatailed(QWidget): 

    def __init__(self, parent = None):  
        super().__init__(parent) 


        main_layout = QVBoxLayout()

        # Form Title 
        self.h1 =  QLabel("Informação", alignment= Qt.AlignmentFlag.AlignHCenter, ObjectName = "titulo")

        #Form 
        self.name_input = QLineEdit(text= "Luis Eduardo Bet", readOnly=True)
        # self.name_input.setPlaceholderText("Digite o nome")  # Placeholder para orientação
        self.birth_date_input = QDateEdit(readOnly=True)  # Ativa o popup do calendário
        self.birth_date_input.setDate(QDate.fromString("22/10/2003"))
        self.birth_date_input.setDisplayFormat("dd/MM/yyyy")  # Formato dd/mm/aaaa
        self.birth_date_input.setToolTip("Digite a data no formato dd/mm/aaaa ou use o calendário")  # Dica para formato
        self.birth_date_input.setSpecialValueText("")  # Evita texto padrão para data inválida
        self.observations_input = QTextEdit(plainText="asdasdasdaskasfnas asdmaskdpamsdkpmas", readOnly = True)
        # Layout
        form = QFormLayout()
        form.addRow(QLabel("Nome:", alignment= Qt.AlignmentFlag.AlignRight), self.name_input)
        form.addRow(QLabel("Data de Nascimento:",alignment= Qt.AlignmentFlag.AlignRight), self.birth_date_input)
        form.addRow(QLabel("Observações:", alignment= Qt.AlignmentFlag.AlignRight), self.observations_input)

        buttons_layout =  QHBoxLayout()
        self.edit_button = QPushButton("Editar Jogador")
        self.insert_button = QPushButton("Novo Jogador")

        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.insert_button)


        main_layout.addWidget(self.h1)
        main_layout.addLayout(form)
        main_layout.addLayout(buttons_layout)

        self._style()

        self.setLayout(main_layout)


    def _style(self): 
    
        self.setStyleSheet("""
                           
        QLabel#titulo{
            font: bold 20px;  
        
        }
                           
                           """)


class SelectPlayerView(QDialog, WindowConfig): 

    TITLE = "Jogadores"
    def __init__(self, parent = None):
        super().__init__()
        self._setup_window(
            self.TITLE,                          
            parent.windowIcon() if parent else None,  
            WindowConfig.DECREMENT_SIZE_PERCENT, 
            10,                                  
            10,                                  
            parent                               
        )

        layout = QHBoxLayout()
        
        self.table = TableView(self)
        self.rowdetailed = RowDatailed(self)

        layout.addWidget(self.table, 1)
        layout.addWidget(self.rowdetailed, 1)

        self.setLayout(layout)

    
    def get_edit_button(self):

        return self.rowdetailed.edit_button


    def get_insert_button(self): 

        return self.rowdetailed.insert_button
    
    def update_table(self, values): 
        return self.table.update_table_items(values) 