# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playerlistview.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                               QGridLayout, QHBoxLayout, QHeaderView, QLabel,
                               QLineEdit, QPushButton, QSizePolicy,
                               QSpacerItem, QTableWidget, QTableWidgetItem,
                               QTabWidget, QVBoxLayout, QWidget)


class Ui_PlayerListView(object):
    def setupUi(self, PlayerListView):
        if not PlayerListView.objectName():
            PlayerListView.setObjectName("PlayerListView")
        PlayerListView.setProperty("modal", False)
        PlayerListView.resize(600, 400)
        self.mainLayout = QHBoxLayout(PlayerListView)
        self.mainLayout.setObjectName("mainLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName("leftLayout")
        self.searchLayout = QHBoxLayout()
        self.searchLayout.setObjectName("searchLayout")
        self.search_label = QLabel(PlayerListView)
        self.search_label.setObjectName("search_label")

        self.searchLayout.addWidget(self.search_label)

        self.search_input = QLineEdit(PlayerListView)
        self.search_input.setObjectName("search_input")

        self.searchLayout.addWidget(self.search_input)

        self.leftLayout.addLayout(self.searchLayout)

        self.table = QTableWidget(PlayerListView)
        if self.table.columnCount() < 2:
            self.table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.table.setObjectName("table")
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.leftLayout.addWidget(self.table)

        self.mainLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName("rightLayout")
        self.tabWidget = QTabWidget(PlayerListView)
        self.tabWidget.setObjectName("tabWidget")
        self.details_tab = QWidget()
        self.details_tab.setObjectName("details_tab")
        self.detailsLayout = QVBoxLayout(self.details_tab)
        self.detailsLayout.setObjectName("detailsLayout")
        self.detailsGrid = QGridLayout()
        self.detailsGrid.setObjectName("detailsGrid")
        self.label_id = QLabel(self.details_tab)
        self.label_id.setObjectName("label_id")
        self.label_id.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_id, 0, 0, 1, 1)

        self.id_label = QLabel(self.details_tab)
        self.id_label.setObjectName("id_label")
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.id_label, 0, 1, 1, 1)

        self.label_name = QLabel(self.details_tab)
        self.label_name.setObjectName("label_name")
        self.label_name.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_name, 1, 0, 1, 1)

        self.name_label = QLabel(self.details_tab)
        self.name_label.setObjectName("name_label")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.name_label, 1, 1, 1, 1)

        self.label_birth_date = QLabel(self.details_tab)
        self.label_birth_date.setObjectName("label_birth_date")
        self.label_birth_date.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_birth_date, 2, 0, 1, 1)

        self.birth_date_label = QLabel(self.details_tab)
        self.birth_date_label.setObjectName("birth_date_label")
        self.birth_date_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.birth_date_label, 2, 1, 1, 1)

        self.label_observation = QLabel(self.details_tab)
        self.label_observation.setObjectName("label_observation")
        self.label_observation.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_observation, 3, 0, 1, 1)

        self.observation_label = QLabel(self.details_tab)
        self.observation_label.setObjectName("observation_label")
        self.observation_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.observation_label, 3, 1, 1, 1)

        self.detailsLayout.addLayout(self.detailsGrid)

        self.detailsSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.detailsLayout.addItem(self.detailsSpacer)

        self.tabWidget.addTab(self.details_tab, "")

        self.rightLayout.addWidget(self.tabWidget)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.new_button = QPushButton(PlayerListView)
        self.new_button.setObjectName("new_button")

        self.buttonLayout.addWidget(self.new_button)

        self.edit_button = QPushButton(PlayerListView)
        self.edit_button.setObjectName("edit_button")

        self.buttonLayout.addWidget(self.edit_button)

        self.delete_button = QPushButton(PlayerListView)
        self.delete_button.setObjectName("delete_button")

        self.buttonLayout.addWidget(self.delete_button)

        self.rightLayout.addLayout(self.buttonLayout)

        self.mainLayout.addLayout(self.rightLayout)

        self.retranslateUi(PlayerListView)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(PlayerListView)

    # setupUi

    def retranslateUi(self, PlayerListView):
        PlayerListView.setWindowTitle("")
        self.search_label.setText(
            QCoreApplication.translate("PlayerListView", "Pesquisar:", None)
        )
        self.search_input.setPlaceholderText(
            QCoreApplication.translate(
                "PlayerListView", "Digite o nome ou ID", None
            )
        )
        ___qtablewidgetitem = self.table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("PlayerListView", "ID", None)
        )
        ___qtablewidgetitem1 = self.table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("PlayerListView", "Nome", None)
        )
        self.label_id.setText(
            QCoreApplication.translate("PlayerListView", "ID:", None)
        )
        self.id_label.setText(
            QCoreApplication.translate("PlayerListView", "ID: ", None)
        )
        self.label_name.setText(
            QCoreApplication.translate("PlayerListView", "Nome:", None)
        )
        self.name_label.setText(
            QCoreApplication.translate("PlayerListView", "Nome: ", None)
        )
        self.label_birth_date.setText(
            QCoreApplication.translate(
                "PlayerListView", "Data de Nascimento:", None
            )
        )
        self.birth_date_label.setText(
            QCoreApplication.translate(
                "PlayerListView", "Data de Nascimento: ", None
            )
        )
        self.label_observation.setText(
            QCoreApplication.translate(
                "PlayerListView", "Observa\u00e7\u00e3o:", None
            )
        )
        self.observation_label.setText(
            QCoreApplication.translate(
                "PlayerListView", "Observa\u00e7\u00e3o: ", None
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.details_tab),
            QCoreApplication.translate("PlayerListView", "Detalhes", None),
        )
        # if QT_CONFIG(tooltip)
        self.new_button.setToolTip(
            QCoreApplication.translate(
                "PlayerListView", "Crie um novo jogador", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.new_button.setText(
            QCoreApplication.translate("PlayerListView", "Novo", None)
        )
        # if QT_CONFIG(tooltip)
        self.edit_button.setToolTip(
            QCoreApplication.translate(
                "PlayerListView", "Edite o jogador selecionado", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.edit_button.setText(
            QCoreApplication.translate("PlayerListView", "Editar", None)
        )
        # if QT_CONFIG(tooltip)
        self.delete_button.setToolTip(
            QCoreApplication.translate(
                "PlayerListView", "Exclua o jogador selecionado", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.delete_button.setText(
            QCoreApplication.translate("PlayerListView", "Excluir", None)
        )

    # retranslateUi
