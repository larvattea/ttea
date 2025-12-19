# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainview.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
import resources.resources_rc

class Ui_MainView(object):
    def setupUi(self, MainView):
        if not MainView.objectName():
            MainView.setObjectName(u"MainView")
        MainView.resize(1000, 680)
        icon = QIcon()
        icon.addFile(u":/icons/larva.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainView.setWindowIcon(icon)
        self.actionSair = QAction(MainView)
        self.actionSair.setObjectName(u"actionSair")
        self.actionGerenciar_Jogadores = QAction(MainView)
        self.actionGerenciar_Jogadores.setObjectName(u"actionGerenciar_Jogadores")
        icon1 = QIcon()
        icon1.addFile(u":/icons/users.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionGerenciar_Jogadores.setIcon(icon1)
        self.actionConfiguracao_KarTEA = QAction(MainView)
        self.actionConfiguracao_KarTEA.setObjectName(u"actionConfiguracao_KarTEA")
        icon2 = QIcon()
        icon2.addFile(u":/icons/kartea4.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionConfiguracao_KarTEA.setIcon(icon2)
        self.actionCalibracao = QAction(MainView)
        self.actionCalibracao.setObjectName(u"actionCalibracao")
        self.actionAjuda = QAction(MainView)
        self.actionAjuda.setObjectName(u"actionAjuda")
        self.actionSobre = QAction(MainView)
        self.actionSobre.setObjectName(u"actionSobre")
        self.centralwidget = QWidget(MainView)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        MainView.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainView)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 33))
        self.menu_Arquivo = QMenu(self.menubar)
        self.menu_Arquivo.setObjectName(u"menu_Arquivo")
        self.menu_Exergames = QMenu(self.menubar)
        self.menu_Exergames.setObjectName(u"menu_Exergames")
        self.menu_Configuracoes = QMenu(self.menubar)
        self.menu_Configuracoes.setObjectName(u"menu_Configuracoes")
        self.menu_Ajuda = QMenu(self.menubar)
        self.menu_Ajuda.setObjectName(u"menu_Ajuda")
        MainView.setMenuBar(self.menubar)

        self.menubar.addAction(self.menu_Arquivo.menuAction())
        self.menubar.addAction(self.menu_Exergames.menuAction())
        self.menubar.addAction(self.menu_Configuracoes.menuAction())
        self.menubar.addAction(self.menu_Ajuda.menuAction())
        self.menu_Arquivo.addAction(self.actionGerenciar_Jogadores)
        self.menu_Arquivo.addSeparator()
        self.menu_Arquivo.addAction(self.actionSair)
        self.menu_Arquivo.addSeparator()
        self.menu_Configuracoes.addAction(self.actionConfiguracao_KarTEA)
        self.menu_Configuracoes.addSeparator()
        self.menu_Configuracoes.addAction(self.actionCalibracao)
        self.menu_Configuracoes.addSeparator()
        self.menu_Ajuda.addAction(self.actionAjuda)
        self.menu_Ajuda.addSeparator()
        self.menu_Ajuda.addAction(self.actionSobre)

        self.retranslateUi(MainView)

        QMetaObject.connectSlotsByName(MainView)
    # setupUi

    def retranslateUi(self, MainView):
        MainView.setWindowTitle(QCoreApplication.translate("MainView", u"Plataforma T-TEA", None))
        self.actionSair.setText(QCoreApplication.translate("MainView", u"&Sair", None))
#if QT_CONFIG(shortcut)
        self.actionSair.setShortcut(QCoreApplication.translate("MainView", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionGerenciar_Jogadores.setText(QCoreApplication.translate("MainView", u"Jogador", None))
#if QT_CONFIG(shortcut)
        self.actionGerenciar_Jogadores.setShortcut(QCoreApplication.translate("MainView", u"Ctrl+J", None))
#endif // QT_CONFIG(shortcut)
        self.actionConfiguracao_KarTEA.setText(QCoreApplication.translate("MainView", u"KarTEA", None))
        self.actionCalibracao.setText(QCoreApplication.translate("MainView", u"&Calibra\u00e7\u00e3o", None))
#if QT_CONFIG(shortcut)
        self.actionCalibracao.setShortcut(QCoreApplication.translate("MainView", u"F4", None))
#endif // QT_CONFIG(shortcut)
        self.actionAjuda.setText(QCoreApplication.translate("MainView", u"&Ajuda", None))
#if QT_CONFIG(shortcut)
        self.actionAjuda.setShortcut(QCoreApplication.translate("MainView", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.actionSobre.setText(QCoreApplication.translate("MainView", u"&Sobre...", None))
        self.menu_Arquivo.setTitle(QCoreApplication.translate("MainView", u"&Cadastro", None))
        self.menu_Exergames.setTitle(QCoreApplication.translate("MainView", u"&Exergames", None))
        self.menu_Configuracoes.setTitle(QCoreApplication.translate("MainView", u"C&onfigura\u00e7\u00f5es", None))
        self.menu_Ajuda.setTitle(QCoreApplication.translate("MainView", u"&Ajuda", None))
    # retranslateUi

