# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainview.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

import resources.resources_rc


class Ui_MainView(object):
    def setupUi(self, MainView):
        if not MainView.objectName():
            MainView.setObjectName(u"MainView")
        MainView.resize(800, 600)
        MainView.setMaximumSize(QSize(16777214, 16777215))
        icon = QIcon()
        icon.addFile(u":/icons/system/appicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainView.setWindowIcon(icon)
        self.act_exit = QAction(MainView)
        self.act_exit.setObjectName(u"act_exit")
        self.act_player = QAction(MainView)
        self.act_player.setObjectName(u"act_player")
        self.act_kartea = QAction(MainView)
        self.act_kartea.setObjectName(u"act_kartea")
        icon1 = QIcon()
        icon1.addFile(u":/icons/ui/menu/kartea4icon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.act_kartea.setIcon(icon1)
        self.act_calibration = QAction(MainView)
        self.act_calibration.setObjectName(u"act_calibration")
        self.act_help = QAction(MainView)
        self.act_help.setObjectName(u"act_help")
        icon2 = QIcon()
        icon2.addFile(u":/icons/ui/menu/question", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.act_help.setIcon(icon2)
        self.act_about = QAction(MainView)
        self.act_about.setObjectName(u"act_about")
        icon3 = QIcon()
        icon3.addFile(u":/icons/ui/menu/info", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.act_about.setIcon(icon3)
        self.wid_main = QWidget(MainView)
        self.wid_main.setObjectName(u"wid_main")
        self.lay_main = QVBoxLayout(self.wid_main)
        self.lay_main.setObjectName(u"lay_main")
        self.vs_menu = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.lay_main.addItem(self.vs_menu)

        MainView.setCentralWidget(self.wid_main)
        self.mnu_main = QMenuBar(MainView)
        self.mnu_main.setObjectName(u"mnu_main")
        self.mnu_main.setGeometry(QRect(0, 0, 800, 33))
        self.mnu_file = QMenu(self.mnu_main)
        self.mnu_file.setObjectName(u"mnu_file")
        self.mnu_exergames = QMenu(self.mnu_main)
        self.mnu_exergames.setObjectName(u"mnu_exergames")
        self.mnu_settings = QMenu(self.mnu_main)
        self.mnu_settings.setObjectName(u"mnu_settings")
        self.mnu_help = QMenu(self.mnu_main)
        self.mnu_help.setObjectName(u"mnu_help")
        MainView.setMenuBar(self.mnu_main)

        self.mnu_main.addAction(self.mnu_file.menuAction())
        self.mnu_main.addAction(self.mnu_exergames.menuAction())
        self.mnu_main.addAction(self.mnu_settings.menuAction())
        self.mnu_main.addAction(self.mnu_help.menuAction())
        self.mnu_file.addAction(self.act_player)
        self.mnu_file.addSeparator()
        self.mnu_file.addAction(self.act_exit)
        self.mnu_file.addSeparator()
        self.mnu_settings.addAction(self.act_kartea)
        self.mnu_settings.addSeparator()
        self.mnu_settings.addAction(self.act_calibration)
        self.mnu_settings.addSeparator()
        self.mnu_help.addAction(self.act_help)
        self.mnu_help.addSeparator()
        self.mnu_help.addAction(self.act_about)

        self.retranslateUi(MainView)

        QMetaObject.connectSlotsByName(MainView)
    # setupUi

    def retranslateUi(self, MainView):
        MainView.setWindowTitle(QCoreApplication.translate("MainView", u"Plataforma T-TEA", None))
        self.act_exit.setText(QCoreApplication.translate("MainView", u"&Sair", None))
#if QT_CONFIG(shortcut)
        self.act_exit.setShortcut(QCoreApplication.translate("MainView", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.act_player.setText(QCoreApplication.translate("MainView", u"Jogador", None))
#if QT_CONFIG(shortcut)
        self.act_player.setShortcut(QCoreApplication.translate("MainView", u"Ctrl+J", None))
#endif // QT_CONFIG(shortcut)
        self.act_kartea.setText(QCoreApplication.translate("MainView", u"KarTEA", None))
        self.act_calibration.setText(QCoreApplication.translate("MainView", u"&Calibra\u00e7\u00e3o", None))
#if QT_CONFIG(shortcut)
        self.act_calibration.setShortcut(QCoreApplication.translate("MainView", u"F4", None))
#endif // QT_CONFIG(shortcut)
        self.act_help.setText(QCoreApplication.translate("MainView", u"&Ajuda", None))
#if QT_CONFIG(shortcut)
        self.act_help.setShortcut(QCoreApplication.translate("MainView", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.act_about.setText(QCoreApplication.translate("MainView", u"&Sobre...", None))
        self.mnu_file.setTitle(QCoreApplication.translate("MainView", u"&Cadastro", None))
        self.mnu_exergames.setTitle(QCoreApplication.translate("MainView", u"&Exergames", None))
        self.mnu_settings.setTitle(QCoreApplication.translate("MainView", u"C&onfigura\u00e7\u00f5es", None))
        self.mnu_help.setTitle(QCoreApplication.translate("MainView", u"&Ajuda", None))
    # retranslateUi

