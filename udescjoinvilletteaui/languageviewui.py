# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'languageview.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QLabel,
                               QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

import resources.resources_rc


class Ui_LanguageView(object):
    def setupUi(self, LanguageView):
        if not LanguageView.objectName():
            LanguageView.setObjectName(u"LanguageView")
        LanguageView.resize(300, 192)
        icon = QIcon()
        icon.addFile(u":/icons/appicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        LanguageView.setWindowIcon(icon)
        LanguageView.setModal(True)
        self.verticalLayout = QVBoxLayout(LanguageView)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lbl_instruction = QLabel(LanguageView)
        self.lbl_instruction.setObjectName(u"lbl_instruction")
        self.lbl_instruction.setStyleSheet(u"font-size: 14px;")
        self.lbl_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.lbl_instruction)

        self.comboBox = QComboBox(LanguageView)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(260, 40))
        self.comboBox.setMaxVisibleItems(5)

        self.verticalLayout.addWidget(self.comboBox)

        self.verticalSpacer2 = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer2)

        self.btn_confirm = QPushButton(LanguageView)
        self.btn_confirm.setObjectName(u"btn_confirm")
        icon1 = QIcon()
        icon1.addFile(u":/images/okicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_confirm.setIcon(icon1)
        self.btn_confirm.setIconSize(QSize(16, 16))

        self.verticalLayout.addWidget(self.btn_confirm)


        self.retranslateUi(LanguageView)

        self.btn_confirm.setDefault(True)


        QMetaObject.connectSlotsByName(LanguageView)
    # setupUi

    def retranslateUi(self, LanguageView):
        LanguageView.setWindowTitle(QCoreApplication.translate("LanguageView", u"Plataforma T-TEA", None))
        self.lbl_instruction.setText(QCoreApplication.translate("LanguageView", u"Selecione o idioma da aplica\u00e7\u00e3o:", None))
#if QT_CONFIG(tooltip)
        self.btn_confirm.setToolTip(QCoreApplication.translate("LanguageView", u"Gravar opera\u00e7\u00e3o corrente", None))
#endif // QT_CONFIG(tooltip)
        self.btn_confirm.setText(QCoreApplication.translate("LanguageView", u"Confirmar", None))
    # retranslateUi

