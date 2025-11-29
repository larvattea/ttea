# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playereditview.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDateEdit,
                               QDialog, QDialogButtonBox, QFormLayout, QLabel,
                               QLineEdit, QSizePolicy, QTabWidget, QTextEdit,
                               QVBoxLayout, QWidget)


class Ui_PlayerEditView(object):
    def setupUi(self, PlayerEditView):
        if not PlayerEditView.objectName():
            PlayerEditView.setObjectName("PlayerEditView")
        PlayerEditView.resize(400, 300)
        PlayerEditView.setModal(True)
        self.main_layout = QVBoxLayout(PlayerEditView)
        self.main_layout.setObjectName("main_layout")
        self.tab_widget = QTabWidget(PlayerEditView)
        self.tab_widget.setObjectName("tab_widget")
        self.details_tab = QWidget()
        self.details_tab.setObjectName("details_tab")
        self.details_layout = QFormLayout(self.details_tab)
        self.details_layout.setObjectName("details_layout")
        self.details_layout.setLabelAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )
        self.label_name = QLabel(self.details_tab)
        self.label_name.setObjectName("label_name")

        self.details_layout.setWidget(
            0, QFormLayout.LabelRole, self.label_name
        )

        self.name_input = QLineEdit(self.details_tab)
        self.name_input.setObjectName("name_input")

        self.details_layout.setWidget(
            0, QFormLayout.FieldRole, self.name_input
        )

        self.label_birth_date = QLabel(self.details_tab)
        self.label_birth_date.setObjectName("label_birth_date")

        self.details_layout.setWidget(
            1, QFormLayout.LabelRole, self.label_birth_date
        )

        self.birth_date_input = QDateEdit(self.details_tab)
        self.birth_date_input.setObjectName("birth_date_input")
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())

        self.details_layout.setWidget(
            1, QFormLayout.FieldRole, self.birth_date_input
        )

        self.label_observation = QLabel(self.details_tab)
        self.label_observation.setObjectName("label_observation")

        self.details_layout.setWidget(
            2, QFormLayout.LabelRole, self.label_observation
        )

        self.observation_input = QTextEdit(self.details_tab)
        self.observation_input.setObjectName("observation_input")
        self.observation_input.setMaximumHeight(80)

        self.details_layout.setWidget(
            2, QFormLayout.FieldRole, self.observation_input
        )

        self.tab_widget.addTab(self.details_tab, "")

        self.main_layout.addWidget(self.tab_widget)

        self.button_box = QDialogButtonBox(PlayerEditView)
        self.button_box.setObjectName("button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        )

        self.main_layout.addWidget(self.button_box)

        self.retranslateUi(PlayerEditView)
        self.button_box.accepted.connect(PlayerEditView.accept)
        self.button_box.rejected.connect(PlayerEditView.reject)

        self.tab_widget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(PlayerEditView)

    # setupUi

    def retranslateUi(self, PlayerEditView):
        PlayerEditView.setWindowTitle(
            QCoreApplication.translate(
                "PlayerEditView", "Jogador - Novo", None
            )
        )
        self.label_name.setText(
            QCoreApplication.translate("PlayerEditView", "Nome:", None)
        )
        self.name_input.setPlaceholderText(
            QCoreApplication.translate("PlayerEditView", "Nome", None)
        )
        self.label_birth_date.setText(
            QCoreApplication.translate(
                "PlayerEditView", "Data de Nascimento:", None
            )
        )
        self.birth_date_input.setDisplayFormat(
            QCoreApplication.translate("PlayerEditView", "dd/MM/yyyy", None)
        )
        self.label_observation.setText(
            QCoreApplication.translate(
                "PlayerEditView", "Observa\u00e7\u00e3o:", None
            )
        )
        self.observation_input.setPlaceholderText(
            QCoreApplication.translate(
                "PlayerEditView", "Observa\u00e7\u00e3o", None
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.details_tab),
            QCoreApplication.translate("PlayerEditView", "Dados", None),
        )

    # retranslateUi
