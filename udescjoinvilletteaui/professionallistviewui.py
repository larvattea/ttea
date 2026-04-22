# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'professionallistview.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
from resources import resources_rc

class Ui_ProfessionalListView(object):
    def setupUi(self, ProfessionalListView):
        if not ProfessionalListView.objectName():
            ProfessionalListView.setObjectName(u"ProfessionalListView")
        ProfessionalListView.resize(600, 400)
        icon = QIcon()
        icon.addFile(u":/icons/system/appicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ProfessionalListView.setWindowIcon(icon)
        ProfessionalListView.setModal(True)
        self.mainLayout = QHBoxLayout(ProfessionalListView)
        self.mainLayout.setObjectName(u"mainLayout")
        self.lay_left = QVBoxLayout()
        self.lay_left.setObjectName(u"lay_left")
        self.lay_search = QHBoxLayout()
        self.lay_search.setObjectName(u"lay_search")
        self.lbl_search = QLabel(ProfessionalListView)
        self.lbl_search.setObjectName(u"lbl_search")

        self.lay_search.addWidget(self.lbl_search)

        self.led_search = QLineEdit(ProfessionalListView)
        self.led_search.setObjectName(u"led_search")

        self.lay_search.addWidget(self.led_search)


        self.lay_left.addLayout(self.lay_search)

        self.tbl_health = QTableWidget(ProfessionalListView)
        if (self.tbl_health.columnCount() < 2):
            self.tbl_health.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tbl_health.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tbl_health.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tbl_health.setObjectName(u"tbl_health")
        self.tbl_health.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_health.setAlternatingRowColors(True)
        self.tbl_health.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl_health.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_health.setSortingEnabled(True)
        self.tbl_health.setColumnCount(2)
        self.tbl_health.horizontalHeader().setStretchLastSection(True)

        self.lay_left.addWidget(self.tbl_health)


        self.mainLayout.addLayout(self.lay_left)

        self.lay_right = QVBoxLayout()
        self.lay_right.setObjectName(u"lay_right")
        self.tab_health = QTabWidget(ProfessionalListView)
        self.tab_health.setObjectName(u"tab_health")
        self.lay_detail = QWidget()
        self.lay_detail.setObjectName(u"lay_detail")
        self.detailsLayout = QVBoxLayout(self.lay_detail)
        self.detailsLayout.setObjectName(u"detailsLayout")
        self.grd_detail = QGridLayout()
        self.grd_detail.setObjectName(u"grd_detail")
        self.lbl_id = QLabel(self.lay_detail)
        self.lbl_id.setObjectName(u"lbl_id")
        self.lbl_id.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.grd_detail.addWidget(self.lbl_id, 0, 0, 1, 1)

        self.lbl_id_value = QLabel(self.lay_detail)
        self.lbl_id_value.setObjectName(u"lbl_id_value")
        self.lbl_id_value.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.grd_detail.addWidget(self.lbl_id_value, 0, 1, 1, 1)

        self.lbl_name = QLabel(self.lay_detail)
        self.lbl_name.setObjectName(u"lbl_name")
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.grd_detail.addWidget(self.lbl_name, 1, 0, 1, 1)

        self.lbl_name_value = QLabel(self.lay_detail)
        self.lbl_name_value.setObjectName(u"lbl_name_value")
        self.lbl_name_value.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.grd_detail.addWidget(self.lbl_name_value, 1, 1, 1, 1)

        self.lbl_type = QLabel(self.lay_detail)
        self.lbl_type.setObjectName(u"lbl_type")
        self.lbl_type.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.grd_detail.addWidget(self.lbl_type, 2, 0, 1, 1)

        self.lbl_type_value = QLabel(self.lay_detail)
        self.lbl_type_value.setObjectName(u"lbl_type_value")
        self.lbl_type_value.setAlignment(Qt.AlignmentFlag.AlignLeading)

        self.grd_detail.addWidget(self.lbl_type_value, 2, 1, 1, 1)


        self.detailsLayout.addLayout(self.grd_detail)

        self.sp_detail = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.detailsLayout.addItem(self.sp_detail)

        self.tab_health.addTab(self.lay_detail, "")

        self.lay_right.addWidget(self.tab_health)

        self.lay_button = QHBoxLayout()
        self.lay_button.setObjectName(u"lay_button")
        self.pb_new = QPushButton(ProfessionalListView)
        self.pb_new.setObjectName(u"pb_new")
        icon1 = QIcon()
        icon1.addFile(u":/icons/ui/buttons/newicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pb_new.setIcon(icon1)

        self.lay_button.addWidget(self.pb_new)

        self.pb_edit = QPushButton(ProfessionalListView)
        self.pb_edit.setObjectName(u"pb_edit")
        icon2 = QIcon()
        icon2.addFile(u":/icons/ui/buttons/editicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pb_edit.setIcon(icon2)

        self.lay_button.addWidget(self.pb_edit)

        self.pb_delete = QPushButton(ProfessionalListView)
        self.pb_delete.setObjectName(u"pb_delete")
        icon3 = QIcon()
        icon3.addFile(u":/icons/ui/buttons/trashicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pb_delete.setIcon(icon3)

        self.lay_button.addWidget(self.pb_delete)


        self.lay_right.addLayout(self.lay_button)


        self.mainLayout.addLayout(self.lay_right)


        self.retranslateUi(ProfessionalListView)

        self.tab_health.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ProfessionalListView)
    # setupUi

    def retranslateUi(self, ProfessionalListView):
        ProfessionalListView.setWindowTitle(QCoreApplication.translate("ProfessionalListView", u"Plataforma T-TEA - Profissional", None))
        self.lbl_search.setText(QCoreApplication.translate("ProfessionalListView", u"Pesquisar:", None))
        self.led_search.setPlaceholderText(QCoreApplication.translate("ProfessionalListView", u"Digite o nome ou ID", None))
        ___qtablewidgetitem = self.tbl_health.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ProfessionalListView", u"ID", None))
        ___qtablewidgetitem1 = self.tbl_health.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ProfessionalListView", u"Nome", None))
        self.lbl_id.setText(QCoreApplication.translate("ProfessionalListView", u"ID:", None))
        self.lbl_id_value.setText(QCoreApplication.translate("ProfessionalListView", u"ID:", None))
        self.lbl_name.setText(QCoreApplication.translate("ProfessionalListView", u"Nome:", None))
        self.lbl_name_value.setText(QCoreApplication.translate("ProfessionalListView", u"Nome: ", None))
        self.lbl_type.setText(QCoreApplication.translate("ProfessionalListView", u"Tipo:", None))
        self.lbl_type_value.setText(QCoreApplication.translate("ProfessionalListView", u"Tipo:", None))
        self.tab_health.setTabText(self.tab_health.indexOf(self.lay_detail), QCoreApplication.translate("ProfessionalListView", u"Detalhes", None))
#if QT_CONFIG(tooltip)
        self.pb_new.setToolTip(QCoreApplication.translate("ProfessionalListView", u"Criar um novo registro", None))
#endif // QT_CONFIG(tooltip)
        self.pb_new.setText(QCoreApplication.translate("ProfessionalListView", u"Novo", None))
#if QT_CONFIG(tooltip)
        self.pb_edit.setToolTip(QCoreApplication.translate("ProfessionalListView", u"Editar o registro selecionado", None))
#endif // QT_CONFIG(tooltip)
        self.pb_edit.setText(QCoreApplication.translate("ProfessionalListView", u"Editar", None))
#if QT_CONFIG(tooltip)
        self.pb_delete.setToolTip(QCoreApplication.translate("ProfessionalListView", u"Excluir o registro selecionado", None))
#endif // QT_CONFIG(tooltip)
        self.pb_delete.setText(QCoreApplication.translate("ProfessionalListView", u"Excluir", None))
    # retranslateUi

