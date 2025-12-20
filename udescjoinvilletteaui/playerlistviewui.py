# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playerlistview.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
            PlayerListView.setObjectName(u"PlayerListView")
        PlayerListView.setProperty(u"modal", False)
        PlayerListView.resize(600, 400)
        self.mainLayout = QHBoxLayout(PlayerListView)
        self.mainLayout.setObjectName(u"mainLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.searchLayout = QHBoxLayout()
        self.searchLayout.setObjectName(u"searchLayout")
        self.search_label = QLabel(PlayerListView)
        self.search_label.setObjectName(u"search_label")

        self.searchLayout.addWidget(self.search_label)

        self.search_input = QLineEdit(PlayerListView)
        self.search_input.setObjectName(u"search_input")

        self.searchLayout.addWidget(self.search_input)


        self.leftLayout.addLayout(self.searchLayout)

        self.table = QTableWidget(PlayerListView)
        if (self.table.columnCount() < 2):
            self.table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.table.setObjectName(u"table")
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.leftLayout.addWidget(self.table)


        self.mainLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.tabWidget = QTabWidget(PlayerListView)
        self.tabWidget.setObjectName(u"tabWidget")
        self.details_tab = QWidget()
        self.details_tab.setObjectName(u"details_tab")
        self.detailsLayout = QVBoxLayout(self.details_tab)
        self.detailsLayout.setObjectName(u"detailsLayout")
        self.detailsGrid = QGridLayout()
        self.detailsGrid.setObjectName(u"detailsGrid")
        self.label_id = QLabel(self.details_tab)
        self.label_id.setObjectName(u"label_id")
        self.label_id.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_id, 0, 0, 1, 1)

        self.id_label = QLabel(self.details_tab)
        self.id_label.setObjectName(u"id_label")
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.id_label, 0, 1, 1, 1)

        self.label_name = QLabel(self.details_tab)
        self.label_name.setObjectName(u"label_name")
        self.label_name.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_name, 1, 0, 1, 1)

        self.name_label = QLabel(self.details_tab)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.name_label, 1, 1, 1, 1)

        self.label_birth_date = QLabel(self.details_tab)
        self.label_birth_date.setObjectName(u"label_birth_date")
        self.label_birth_date.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_birth_date, 2, 0, 1, 1)

        self.birth_date_label = QLabel(self.details_tab)
        self.birth_date_label.setObjectName(u"birth_date_label")
        self.birth_date_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.birth_date_label, 2, 1, 1, 1)

        self.label_observation = QLabel(self.details_tab)
        self.label_observation.setObjectName(u"label_observation")
        self.label_observation.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.label_observation, 3, 0, 1, 1)

        self.observation_label = QLabel(self.details_tab)
        self.observation_label.setObjectName(u"observation_label")
        self.observation_label.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.detailsGrid.addWidget(self.observation_label, 3, 1, 1, 1)


        self.detailsLayout.addLayout(self.detailsGrid)

        self.detailsSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.detailsLayout.addItem(self.detailsSpacer)

        self.tabWidget.addTab(self.details_tab, "")

        self.rightLayout.addWidget(self.tabWidget)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.new_button = QPushButton(PlayerListView)
        self.new_button.setObjectName(u"new_button")

        self.buttonLayout.addWidget(self.new_button)

        self.edit_button = QPushButton(PlayerListView)
        self.edit_button.setObjectName(u"edit_button")

        self.buttonLayout.addWidget(self.edit_button)

        self.delete_button = QPushButton(PlayerListView)
        self.delete_button.setObjectName(u"delete_button")

        self.buttonLayout.addWidget(self.delete_button)


        self.rightLayout.addLayout(self.buttonLayout)


        self.mainLayout.addLayout(self.rightLayout)


        self.retranslateUi(PlayerListView)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(PlayerListView)
    # setupUi

    def retranslateUi(self, PlayerListView):
        PlayerListView.setWindowTitle("")
        self.search_label.setText(QCoreApplication.translate("PlayerListView", u"Pesquisar:", None))
        self.search_input.setPlaceholderText(QCoreApplication.translate("PlayerListView", u"Digite o nome ou ID", None))
        ___qtablewidgetitem = self.table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("PlayerListView", u"ID", None));
        ___qtablewidgetitem1 = self.table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("PlayerListView", u"Nome", None));
        self.label_id.setText(QCoreApplication.translate("PlayerListView", u"ID:", None))
        self.id_label.setText(QCoreApplication.translate("PlayerListView", u"ID: ", None))
        self.label_name.setText(QCoreApplication.translate("PlayerListView", u"Nome:", None))
        self.name_label.setText(QCoreApplication.translate("PlayerListView", u"Nome: ", None))
        self.label_birth_date.setText(QCoreApplication.translate("PlayerListView", u"Data de Nascimento:", None))
        self.birth_date_label.setText(QCoreApplication.translate("PlayerListView", u"Data de Nascimento: ", None))
        self.label_observation.setText(QCoreApplication.translate("PlayerListView", u"Observa\u00e7\u00e3o:", None))
        self.observation_label.setText(QCoreApplication.translate("PlayerListView", u"Observa\u00e7\u00e3o: ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.details_tab), QCoreApplication.translate("PlayerListView", u"Detalhes", None))
#if QT_CONFIG(tooltip)
        self.new_button.setToolTip(QCoreApplication.translate("PlayerListView", u"Crie um novo jogador", None))
#endif // QT_CONFIG(tooltip)
        self.new_button.setText(QCoreApplication.translate("PlayerListView", u"Novo", None))
#if QT_CONFIG(tooltip)
        self.edit_button.setToolTip(QCoreApplication.translate("PlayerListView", u"Edite o jogador selecionado", None))
#endif // QT_CONFIG(tooltip)
        self.edit_button.setText(QCoreApplication.translate("PlayerListView", u"Editar", None))
#if QT_CONFIG(tooltip)
        self.delete_button.setToolTip(QCoreApplication.translate("PlayerListView", u"Exclua o jogador selecionado", None))
#endif // QT_CONFIG(tooltip)
        self.delete_button.setText(QCoreApplication.translate("PlayerListView", u"Excluir", None))
    # retranslateUi

