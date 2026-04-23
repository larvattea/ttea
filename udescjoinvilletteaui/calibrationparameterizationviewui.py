# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calibrationparameterizationview.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTabWidget, QVBoxLayout,
    QWidget)
import resources.resources_rc

class Ui_CalibrationParameterizationView(object):
    def setupUi(self, CalibrationParameterizationView):
        if not CalibrationParameterizationView.objectName():
            CalibrationParameterizationView.setObjectName(u"CalibrationParameterizationView")
        CalibrationParameterizationView.resize(680, 594)
        CalibrationParameterizationView.setModal(True)
        self.main_layout = QVBoxLayout(CalibrationParameterizationView)
        self.main_layout.setObjectName(u"main_layout")
        self.tab_widget = QTabWidget(CalibrationParameterizationView)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_mediapipe = QWidget()
        self.tab_mediapipe.setObjectName(u"tab_mediapipe")
        self.lay_mediapipe = QVBoxLayout(self.tab_mediapipe)
        self.lay_mediapipe.setSpacing(12)
        self.lay_mediapipe.setObjectName(u"lay_mediapipe")
        self.lay_mediapipe.setContentsMargins(12, 12, 12, 12)
        self.frm_mediapipe = QFormLayout()
        self.frm_mediapipe.setObjectName(u"frm_mediapipe")
        self.frm_mediapipe.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.frm_mediapipe.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_model_desktop = QLabel(self.tab_mediapipe)
        self.lbl_model_desktop.setObjectName(u"lbl_model_desktop")

        self.frm_mediapipe.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_model_desktop)

        self.grp_model_desktop = QGroupBox(self.tab_mediapipe)
        self.grp_model_desktop.setObjectName(u"grp_model_desktop")
        self.horizontalLayout_desktop = QHBoxLayout(self.grp_model_desktop)
        self.horizontalLayout_desktop.setObjectName(u"horizontalLayout_desktop")
        self.rb_model_desktop_lite = QRadioButton(self.grp_model_desktop)
        self.rb_model_desktop_lite.setObjectName(u"rb_model_desktop_lite")
        self.rb_model_desktop_lite.setChecked(True)

        self.horizontalLayout_desktop.addWidget(self.rb_model_desktop_lite)

        self.rb_model_desktop_full = QRadioButton(self.grp_model_desktop)
        self.rb_model_desktop_full.setObjectName(u"rb_model_desktop_full")

        self.horizontalLayout_desktop.addWidget(self.rb_model_desktop_full)

        self.rb_model_desktop_heavy = QRadioButton(self.grp_model_desktop)
        self.rb_model_desktop_heavy.setObjectName(u"rb_model_desktop_heavy")

        self.horizontalLayout_desktop.addWidget(self.rb_model_desktop_heavy)

        self.hs_model_desktop = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_desktop.addItem(self.hs_model_desktop)


        self.frm_mediapipe.setWidget(0, QFormLayout.ItemRole.FieldRole, self.grp_model_desktop)

        self.lbl_model_embedded = QLabel(self.tab_mediapipe)
        self.lbl_model_embedded.setObjectName(u"lbl_model_embedded")

        self.frm_mediapipe.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_model_embedded)

        self.grp_model_embedded = QGroupBox(self.tab_mediapipe)
        self.grp_model_embedded.setObjectName(u"grp_model_embedded")
        self.horizontalLayout_embedded = QHBoxLayout(self.grp_model_embedded)
        self.horizontalLayout_embedded.setObjectName(u"horizontalLayout_embedded")
        self.rb_model_embedded_lite = QRadioButton(self.grp_model_embedded)
        self.rb_model_embedded_lite.setObjectName(u"rb_model_embedded_lite")
        self.rb_model_embedded_lite.setChecked(True)

        self.horizontalLayout_embedded.addWidget(self.rb_model_embedded_lite)

        self.rb_model_embedded_full = QRadioButton(self.grp_model_embedded)
        self.rb_model_embedded_full.setObjectName(u"rb_model_embedded_full")

        self.horizontalLayout_embedded.addWidget(self.rb_model_embedded_full)

        self.rb_model_embedded_heavy = QRadioButton(self.grp_model_embedded)
        self.rb_model_embedded_heavy.setObjectName(u"rb_model_embedded_heavy")

        self.horizontalLayout_embedded.addWidget(self.rb_model_embedded_heavy)

        self.hs_model_embedded = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_embedded.addItem(self.hs_model_embedded)


        self.frm_mediapipe.setWidget(1, QFormLayout.ItemRole.FieldRole, self.grp_model_embedded)

        self.lbl_embedded_processing = QLabel(self.tab_mediapipe)
        self.lbl_embedded_processing.setObjectName(u"lbl_embedded_processing")

        self.frm_mediapipe.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_embedded_processing)

        self.grp_embedded_processing = QGroupBox(self.tab_mediapipe)
        self.grp_embedded_processing.setObjectName(u"grp_embedded_processing")
        self.horizontalLayout_embedded_proc = QHBoxLayout(self.grp_embedded_processing)
        self.horizontalLayout_embedded_proc.setObjectName(u"horizontalLayout_embedded_proc")
        self.rb_embedded_processing_cpu = QRadioButton(self.grp_embedded_processing)
        self.rb_embedded_processing_cpu.setObjectName(u"rb_embedded_processing_cpu")
        self.rb_embedded_processing_cpu.setChecked(True)

        self.horizontalLayout_embedded_proc.addWidget(self.rb_embedded_processing_cpu)

        self.rb_embedded_processing_gpu = QRadioButton(self.grp_embedded_processing)
        self.rb_embedded_processing_gpu.setObjectName(u"rb_embedded_processing_gpu")

        self.horizontalLayout_embedded_proc.addWidget(self.rb_embedded_processing_gpu)

        self.hs_embedded_processing = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_embedded_proc.addItem(self.hs_embedded_processing)


        self.frm_mediapipe.setWidget(2, QFormLayout.ItemRole.FieldRole, self.grp_embedded_processing)

        self.lbl_linux_processing = QLabel(self.tab_mediapipe)
        self.lbl_linux_processing.setObjectName(u"lbl_linux_processing")

        self.frm_mediapipe.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_linux_processing)

        self.grp_linux_processing = QGroupBox(self.tab_mediapipe)
        self.grp_linux_processing.setObjectName(u"grp_linux_processing")
        self.horizontalLayout_linux = QHBoxLayout(self.grp_linux_processing)
        self.horizontalLayout_linux.setObjectName(u"horizontalLayout_linux")
        self.rb_linux_processing_cpu = QRadioButton(self.grp_linux_processing)
        self.rb_linux_processing_cpu.setObjectName(u"rb_linux_processing_cpu")
        self.rb_linux_processing_cpu.setChecked(True)

        self.horizontalLayout_linux.addWidget(self.rb_linux_processing_cpu)

        self.rb_linux_processing_gpu = QRadioButton(self.grp_linux_processing)
        self.rb_linux_processing_gpu.setObjectName(u"rb_linux_processing_gpu")

        self.horizontalLayout_linux.addWidget(self.rb_linux_processing_gpu)

        self.hs_linux_processing = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_linux.addItem(self.hs_linux_processing)


        self.frm_mediapipe.setWidget(3, QFormLayout.ItemRole.FieldRole, self.grp_linux_processing)

        self.lbl_mac_processing = QLabel(self.tab_mediapipe)
        self.lbl_mac_processing.setObjectName(u"lbl_mac_processing")

        self.frm_mediapipe.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbl_mac_processing)

        self.groupBox_mac = QGroupBox(self.tab_mediapipe)
        self.groupBox_mac.setObjectName(u"groupBox_mac")
        self.horizontalLayout_mac = QHBoxLayout(self.groupBox_mac)
        self.horizontalLayout_mac.setObjectName(u"horizontalLayout_mac")
        self.rb_mac_processing_cpu = QRadioButton(self.groupBox_mac)
        self.rb_mac_processing_cpu.setObjectName(u"rb_mac_processing_cpu")
        self.rb_mac_processing_cpu.setChecked(True)

        self.horizontalLayout_mac.addWidget(self.rb_mac_processing_cpu)

        self.rb_mac_processing_gpu = QRadioButton(self.groupBox_mac)
        self.rb_mac_processing_gpu.setObjectName(u"rb_mac_processing_gpu")

        self.horizontalLayout_mac.addWidget(self.rb_mac_processing_gpu)

        self.hs_mac_processing = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_mac.addItem(self.hs_mac_processing)


        self.frm_mediapipe.setWidget(4, QFormLayout.ItemRole.FieldRole, self.groupBox_mac)

        self.lbl_windows_processing = QLabel(self.tab_mediapipe)
        self.lbl_windows_processing.setObjectName(u"lbl_windows_processing")

        self.frm_mediapipe.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lbl_windows_processing)

        self.groupBox_windows = QGroupBox(self.tab_mediapipe)
        self.groupBox_windows.setObjectName(u"groupBox_windows")
        self.horizontalLayout_windows = QHBoxLayout(self.groupBox_windows)
        self.horizontalLayout_windows.setObjectName(u"horizontalLayout_windows")
        self.rb_windows_processing_cpu = QRadioButton(self.groupBox_windows)
        self.rb_windows_processing_cpu.setObjectName(u"rb_windows_processing_cpu")
        self.rb_windows_processing_cpu.setChecked(True)

        self.horizontalLayout_windows.addWidget(self.rb_windows_processing_cpu)

        self.rb_windows_processing_gpu = QRadioButton(self.groupBox_windows)
        self.rb_windows_processing_gpu.setObjectName(u"rb_windows_processing_gpu")

        self.horizontalLayout_windows.addWidget(self.rb_windows_processing_gpu)

        self.hs_windows_processing = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_windows.addItem(self.hs_windows_processing)


        self.frm_mediapipe.setWidget(5, QFormLayout.ItemRole.FieldRole, self.groupBox_windows)

        self.lbl_execution_mode = QLabel(self.tab_mediapipe)
        self.lbl_execution_mode.setObjectName(u"lbl_execution_mode")

        self.frm_mediapipe.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lbl_execution_mode)

        self.groupBox_execution_mode = QGroupBox(self.tab_mediapipe)
        self.groupBox_execution_mode.setObjectName(u"groupBox_execution_mode")
        self.horizontalLayout_execution_mode = QHBoxLayout(self.groupBox_execution_mode)
        self.horizontalLayout_execution_mode.setObjectName(u"horizontalLayout_execution_mode")
        self.rb_execution_mode_video = QRadioButton(self.groupBox_execution_mode)
        self.rb_execution_mode_video.setObjectName(u"rb_execution_mode_video")
        self.rb_execution_mode_video.setChecked(True)

        self.horizontalLayout_execution_mode.addWidget(self.rb_execution_mode_video)

        self.hs_execution_mode = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_execution_mode.addItem(self.hs_execution_mode)


        self.frm_mediapipe.setWidget(6, QFormLayout.ItemRole.FieldRole, self.groupBox_execution_mode)

        self.lbl_detection_position = QLabel(self.tab_mediapipe)
        self.lbl_detection_position.setObjectName(u"lbl_detection_position")

        self.frm_mediapipe.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lbl_detection_position)

        self.spn_detection_position = QDoubleSpinBox(self.tab_mediapipe)
        self.spn_detection_position.setObjectName(u"spn_detection_position")
        self.spn_detection_position.setDecimals(2)
        self.spn_detection_position.setMinimum(0.000000000000000)
        self.spn_detection_position.setMaximum(1.000000000000000)
        self.spn_detection_position.setSingleStep(0.010000000000000)
        self.spn_detection_position.setValue(0.500000000000000)

        self.frm_mediapipe.setWidget(7, QFormLayout.ItemRole.FieldRole, self.spn_detection_position)

        self.lbl_detection_presence = QLabel(self.tab_mediapipe)
        self.lbl_detection_presence.setObjectName(u"lbl_detection_presence")

        self.frm_mediapipe.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lbl_detection_presence)

        self.spn_detection_presence = QDoubleSpinBox(self.tab_mediapipe)
        self.spn_detection_presence.setObjectName(u"spn_detection_presence")
        self.spn_detection_presence.setDecimals(2)
        self.spn_detection_presence.setMinimum(0.000000000000000)
        self.spn_detection_presence.setMaximum(1.000000000000000)
        self.spn_detection_presence.setSingleStep(0.010000000000000)
        self.spn_detection_presence.setValue(0.500000000000000)

        self.frm_mediapipe.setWidget(8, QFormLayout.ItemRole.FieldRole, self.spn_detection_presence)

        self.lbl_detection_tracking = QLabel(self.tab_mediapipe)
        self.lbl_detection_tracking.setObjectName(u"lbl_detection_tracking")

        self.frm_mediapipe.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lbl_detection_tracking)

        self.spn_detection_tracking = QDoubleSpinBox(self.tab_mediapipe)
        self.spn_detection_tracking.setObjectName(u"spn_detection_tracking")
        self.spn_detection_tracking.setDecimals(2)
        self.spn_detection_tracking.setMinimum(0.000000000000000)
        self.spn_detection_tracking.setMaximum(1.000000000000000)
        self.spn_detection_tracking.setSingleStep(0.010000000000000)
        self.spn_detection_tracking.setValue(0.500000000000000)

        self.frm_mediapipe.setWidget(9, QFormLayout.ItemRole.FieldRole, self.spn_detection_tracking)

        self.lbl_num_position = QLabel(self.tab_mediapipe)
        self.lbl_num_position.setObjectName(u"lbl_num_position")

        self.frm_mediapipe.setWidget(10, QFormLayout.ItemRole.LabelRole, self.lbl_num_position)

        self.spn_num_position = QSpinBox(self.tab_mediapipe)
        self.spn_num_position.setObjectName(u"spn_num_position")
        self.spn_num_position.setEnabled(False)
        self.spn_num_position.setMinimum(1)
        self.spn_num_position.setMaximum(1)
        self.spn_num_position.setValue(1)

        self.frm_mediapipe.setWidget(10, QFormLayout.ItemRole.FieldRole, self.spn_num_position)


        self.lay_mediapipe.addLayout(self.frm_mediapipe)

        self.vs_mediapipe = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.lay_mediapipe.addItem(self.vs_mediapipe)

        self.tab_widget.addTab(self.tab_mediapipe, "")
        self.tab_opencv = QWidget()
        self.tab_opencv.setObjectName(u"tab_opencv")
        self.lay_opencv = QVBoxLayout(self.tab_opencv)
        self.lay_opencv.setSpacing(10)
        self.lay_opencv.setObjectName(u"lay_opencv")
        self.lay_opencv.setContentsMargins(12, 12, 12, 12)
        self.frm_opencv = QFormLayout()
        self.frm_opencv.setObjectName(u"frm_opencv")
        self.frm_opencv.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_embedded_capture = QLabel(self.tab_opencv)
        self.lbl_embedded_capture.setObjectName(u"lbl_embedded_capture")

        self.frm_opencv.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_embedded_capture)

        self.grp_embedded_capture = QGroupBox(self.tab_opencv)
        self.grp_embedded_capture.setObjectName(u"grp_embedded_capture")
        self.hboxLayout = QHBoxLayout(self.grp_embedded_capture)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.rb_embedded_v4l2 = QRadioButton(self.grp_embedded_capture)
        self.rb_embedded_v4l2.setObjectName(u"rb_embedded_v4l2")
        self.rb_embedded_v4l2.setChecked(True)

        self.hboxLayout.addWidget(self.rb_embedded_v4l2)

        self.rb_embedded_gstreamer = QRadioButton(self.grp_embedded_capture)
        self.rb_embedded_gstreamer.setObjectName(u"rb_embedded_gstreamer")

        self.hboxLayout.addWidget(self.rb_embedded_gstreamer)

        self.hs_embedded_capture = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout.addItem(self.hs_embedded_capture)


        self.frm_opencv.setWidget(0, QFormLayout.ItemRole.FieldRole, self.grp_embedded_capture)

        self.lbl_linux_capture = QLabel(self.tab_opencv)
        self.lbl_linux_capture.setObjectName(u"lbl_linux_capture")

        self.frm_opencv.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_linux_capture)

        self.grp_linux_capture = QGroupBox(self.tab_opencv)
        self.grp_linux_capture.setObjectName(u"grp_linux_capture")
        self.hboxLayout1 = QHBoxLayout(self.grp_linux_capture)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.rb_linux_v4l2 = QRadioButton(self.grp_linux_capture)
        self.rb_linux_v4l2.setObjectName(u"rb_linux_v4l2")
        self.rb_linux_v4l2.setChecked(True)

        self.hboxLayout1.addWidget(self.rb_linux_v4l2)

        self.rb_linux_gstreamer = QRadioButton(self.grp_linux_capture)
        self.rb_linux_gstreamer.setObjectName(u"rb_linux_gstreamer")

        self.hboxLayout1.addWidget(self.rb_linux_gstreamer)

        self.hs_linux_capture = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout1.addItem(self.hs_linux_capture)


        self.frm_opencv.setWidget(1, QFormLayout.ItemRole.FieldRole, self.grp_linux_capture)

        self.lbl_mac_capture = QLabel(self.tab_opencv)
        self.lbl_mac_capture.setObjectName(u"lbl_mac_capture")

        self.frm_opencv.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_mac_capture)

        self.grp_mac_capture = QGroupBox(self.tab_opencv)
        self.grp_mac_capture.setObjectName(u"grp_mac_capture")
        self.hboxLayout2 = QHBoxLayout(self.grp_mac_capture)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.rb_mac_avfoundation = QRadioButton(self.grp_mac_capture)
        self.rb_mac_avfoundation.setObjectName(u"rb_mac_avfoundation")
        self.rb_mac_avfoundation.setChecked(True)

        self.hboxLayout2.addWidget(self.rb_mac_avfoundation)

        self.rb_mac_any = QRadioButton(self.grp_mac_capture)
        self.rb_mac_any.setObjectName(u"rb_mac_any")

        self.hboxLayout2.addWidget(self.rb_mac_any)

        self.hs_mac_capture = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout2.addItem(self.hs_mac_capture)


        self.frm_opencv.setWidget(2, QFormLayout.ItemRole.FieldRole, self.grp_mac_capture)

        self.lbl_windows_capture = QLabel(self.tab_opencv)
        self.lbl_windows_capture.setObjectName(u"lbl_windows_capture")

        self.frm_opencv.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_windows_capture)

        self.grp_windows_capture = QGroupBox(self.tab_opencv)
        self.grp_windows_capture.setObjectName(u"grp_windows_capture")
        self.hboxLayout3 = QHBoxLayout(self.grp_windows_capture)
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.rb_windows_dshow = QRadioButton(self.grp_windows_capture)
        self.rb_windows_dshow.setObjectName(u"rb_windows_dshow")
        self.rb_windows_dshow.setChecked(True)

        self.hboxLayout3.addWidget(self.rb_windows_dshow)

        self.rb_windows_msmf = QRadioButton(self.grp_windows_capture)
        self.rb_windows_msmf.setObjectName(u"rb_windows_msmf")

        self.hboxLayout3.addWidget(self.rb_windows_msmf)

        self.hs_windows_capture = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout3.addItem(self.hs_windows_capture)


        self.frm_opencv.setWidget(3, QFormLayout.ItemRole.FieldRole, self.grp_windows_capture)

        self.lbl_buffer_size = QLabel(self.tab_opencv)
        self.lbl_buffer_size.setObjectName(u"lbl_buffer_size")

        self.frm_opencv.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbl_buffer_size)

        self.spn_buffer_size = QSpinBox(self.tab_opencv)
        self.spn_buffer_size.setObjectName(u"spn_buffer_size")
        self.spn_buffer_size.setMinimum(1)
        self.spn_buffer_size.setMaximum(5)
        self.spn_buffer_size.setSingleStep(1)
        self.spn_buffer_size.setValue(1)

        self.frm_opencv.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spn_buffer_size)

        self.lbl_custom_camera = QLabel(self.tab_opencv)
        self.lbl_custom_camera.setObjectName(u"lbl_custom_camera")

        self.frm_opencv.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lbl_custom_camera)

        self.chk_custom_camera = QCheckBox(self.tab_opencv)
        self.chk_custom_camera.setObjectName(u"chk_custom_camera")
        self.chk_custom_camera.setChecked(False)

        self.frm_opencv.setWidget(5, QFormLayout.ItemRole.FieldRole, self.chk_custom_camera)


        self.lay_opencv.addLayout(self.frm_opencv)

        self.grp_camera_info = QGroupBox(self.tab_opencv)
        self.grp_camera_info.setObjectName(u"grp_camera_info")
        self.grp_camera_info.setCheckable(False)
        self.form_camera = QFormLayout(self.grp_camera_info)
        self.form_camera.setObjectName(u"form_camera")
        self.form_camera.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_ratio = QLabel(self.grp_camera_info)
        self.lbl_ratio.setObjectName(u"lbl_ratio")

        self.form_camera.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_ratio)

        self.cbx_ratio = QComboBox(self.grp_camera_info)
        self.cbx_ratio.setObjectName(u"cbx_ratio")
        self.cbx_ratio.setMaxVisibleItems(5)

        self.form_camera.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cbx_ratio)

        self.lbl_width = QLabel(self.grp_camera_info)
        self.lbl_width.setObjectName(u"lbl_width")

        self.form_camera.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_width)

        self.cbx_camera_width = QComboBox(self.grp_camera_info)
        self.cbx_camera_width.setObjectName(u"cbx_camera_width")
        self.cbx_camera_width.setMaxVisibleItems(5)

        self.form_camera.setWidget(1, QFormLayout.ItemRole.FieldRole, self.cbx_camera_width)

        self.lbl_height = QLabel(self.grp_camera_info)
        self.lbl_height.setObjectName(u"lbl_height")

        self.form_camera.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_height)

        self.cbx_camera_height = QComboBox(self.grp_camera_info)
        self.cbx_camera_height.setObjectName(u"cbx_camera_height")
        self.cbx_camera_height.setMaxVisibleItems(5)

        self.form_camera.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cbx_camera_height)

        self.lbl_fps = QLabel(self.grp_camera_info)
        self.lbl_fps.setObjectName(u"lbl_fps")

        self.form_camera.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_fps)

        self.grp_fps = QGroupBox(self.grp_camera_info)
        self.grp_fps.setObjectName(u"grp_fps")
        self.hboxLayout4 = QHBoxLayout(self.grp_fps)
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.rb_fps_30 = QRadioButton(self.grp_fps)
        self.rb_fps_30.setObjectName(u"rb_fps_30")
        self.rb_fps_30.setChecked(True)

        self.hboxLayout4.addWidget(self.rb_fps_30)

        self.rb_fps_60 = QRadioButton(self.grp_fps)
        self.rb_fps_60.setObjectName(u"rb_fps_60")

        self.hboxLayout4.addWidget(self.rb_fps_60)

        self.hs_fps = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout4.addItem(self.hs_fps)


        self.form_camera.setWidget(3, QFormLayout.ItemRole.FieldRole, self.grp_fps)


        self.lay_opencv.addWidget(self.grp_camera_info)

        self.vs_opencv = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.lay_opencv.addItem(self.vs_opencv)

        self.tab_widget.addTab(self.tab_opencv, "")
        self.tab_filter = QWidget()
        self.tab_filter.setObjectName(u"tab_filter")
        self.lay_filter = QVBoxLayout(self.tab_filter)
        self.lay_filter.setSpacing(10)
        self.lay_filter.setObjectName(u"lay_filter")
        self.lay_filter.setContentsMargins(12, 12, 12, 12)
        self.frm_filter = QFormLayout()
        self.frm_filter.setObjectName(u"frm_filter")
        self.frm_filter.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_use_filter = QLabel(self.tab_filter)
        self.lbl_use_filter.setObjectName(u"lbl_use_filter")

        self.frm_filter.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_use_filter)

        self.chk_use_filter = QCheckBox(self.tab_filter)
        self.chk_use_filter.setObjectName(u"chk_use_filter")
        self.chk_use_filter.setChecked(False)

        self.frm_filter.setWidget(0, QFormLayout.ItemRole.FieldRole, self.chk_use_filter)


        self.lay_filter.addLayout(self.frm_filter)

        self.grp_filter = QGroupBox(self.tab_filter)
        self.grp_filter.setObjectName(u"grp_filter")
        self.form_filters = QFormLayout(self.grp_filter)
        self.form_filters.setObjectName(u"form_filters")
        self.form_filters.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_average_smooth_frames = QLabel(self.grp_filter)
        self.lbl_average_smooth_frames.setObjectName(u"lbl_average_smooth_frames")

        self.form_filters.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_average_smooth_frames)

        self.spn_average_smooth_frames = QSpinBox(self.grp_filter)
        self.spn_average_smooth_frames.setObjectName(u"spn_average_smooth_frames")
        self.spn_average_smooth_frames.setMinimum(5)
        self.spn_average_smooth_frames.setMaximum(10)
        self.spn_average_smooth_frames.setSingleStep(1)
        self.spn_average_smooth_frames.setValue(5)

        self.form_filters.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spn_average_smooth_frames)

        self.lbl_clahe_clip = QLabel(self.grp_filter)
        self.lbl_clahe_clip.setObjectName(u"lbl_clahe_clip")

        self.form_filters.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_clahe_clip)

        self.spn_clahe_clip = QSpinBox(self.grp_filter)
        self.spn_clahe_clip.setObjectName(u"spn_clahe_clip")
        self.spn_clahe_clip.setMinimum(1)
        self.spn_clahe_clip.setMaximum(10)
        self.spn_clahe_clip.setSingleStep(1)
        self.spn_clahe_clip.setValue(2)

        self.form_filters.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spn_clahe_clip)

        self.lbl_clahe_grid = QLabel(self.grp_filter)
        self.lbl_clahe_grid.setObjectName(u"lbl_clahe_grid")

        self.form_filters.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_clahe_grid)

        self.cbx_clahe_grid = QComboBox(self.grp_filter)
        self.cbx_clahe_grid.addItem("")
        self.cbx_clahe_grid.addItem("")
        self.cbx_clahe_grid.addItem("")
        self.cbx_clahe_grid.addItem("")
        self.cbx_clahe_grid.setObjectName(u"cbx_clahe_grid")

        self.form_filters.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cbx_clahe_grid)

        self.lbl_clahe_lum_below = QLabel(self.grp_filter)
        self.lbl_clahe_lum_below.setObjectName(u"lbl_clahe_lum_below")

        self.form_filters.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_clahe_lum_below)

        self.spn_clahe_lum_below = QSpinBox(self.grp_filter)
        self.spn_clahe_lum_below.setObjectName(u"spn_clahe_lum_below")
        self.spn_clahe_lum_below.setMinimum(50)
        self.spn_clahe_lum_below.setMaximum(150)
        self.spn_clahe_lum_below.setSingleStep(1)
        self.spn_clahe_lum_below.setValue(100)

        self.form_filters.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spn_clahe_lum_below)

        self.lbl_gamma_factor = QLabel(self.grp_filter)
        self.lbl_gamma_factor.setObjectName(u"lbl_gamma_factor")

        self.form_filters.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbl_gamma_factor)

        self.spn_gamma_factor = QDoubleSpinBox(self.grp_filter)
        self.spn_gamma_factor.setObjectName(u"spn_gamma_factor")
        self.spn_gamma_factor.setDecimals(1)
        self.spn_gamma_factor.setMinimum(1.000000000000000)
        self.spn_gamma_factor.setMaximum(10.000000000000000)
        self.spn_gamma_factor.setSingleStep(0.100000000000000)
        self.spn_gamma_factor.setValue(1.200000000000000)

        self.form_filters.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spn_gamma_factor)

        self.lbl_gamma_lum_above = QLabel(self.grp_filter)
        self.lbl_gamma_lum_above.setObjectName(u"lbl_gamma_lum_above")

        self.form_filters.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lbl_gamma_lum_above)

        self.spn_gamma_lum_above = QSpinBox(self.grp_filter)
        self.spn_gamma_lum_above.setObjectName(u"spn_gamma_lum_above")
        self.spn_gamma_lum_above.setMinimum(100)
        self.spn_gamma_lum_above.setMaximum(200)
        self.spn_gamma_lum_above.setSingleStep(1)
        self.spn_gamma_lum_above.setValue(150)

        self.form_filters.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spn_gamma_lum_above)

        self.lbl_landmark_limit = QLabel(self.grp_filter)
        self.lbl_landmark_limit.setObjectName(u"lbl_landmark_limit")

        self.form_filters.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lbl_landmark_limit)

        self.spn_landmark_limit = QDoubleSpinBox(self.grp_filter)
        self.spn_landmark_limit.setObjectName(u"spn_landmark_limit")
        self.spn_landmark_limit.setDecimals(2)
        self.spn_landmark_limit.setMinimum(0.000000000000000)
        self.spn_landmark_limit.setMaximum(1.000000000000000)
        self.spn_landmark_limit.setSingleStep(0.010000000000000)
        self.spn_landmark_limit.setValue(0.150000000000000)

        self.form_filters.setWidget(6, QFormLayout.ItemRole.FieldRole, self.spn_landmark_limit)


        self.lay_filter.addWidget(self.grp_filter)

        self.vs_filter = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.lay_filter.addItem(self.vs_filter)

        self.tab_widget.addTab(self.tab_filter, "")
        self.tab_telemetry = QWidget()
        self.tab_telemetry.setObjectName(u"tab_telemetry")
        self.vboxLayout = QVBoxLayout(self.tab_telemetry)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.lbl_telemetry_placeholder = QLabel(self.tab_telemetry)
        self.lbl_telemetry_placeholder.setObjectName(u"lbl_telemetry_placeholder")
        self.lbl_telemetry_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vboxLayout.addWidget(self.lbl_telemetry_placeholder)

        self.tab_widget.addTab(self.tab_telemetry, "")

        self.main_layout.addWidget(self.tab_widget)

        self.lay_button = QHBoxLayout()
        self.lay_button.setObjectName(u"lay_button")
        self.hs_button = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.lay_button.addItem(self.hs_button)

        self.pb_ok = QPushButton(CalibrationParameterizationView)
        self.pb_ok.setObjectName(u"pb_ok")
        icon = QIcon()
        icon.addFile(u":/icons/ui/buttons/okicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pb_ok.setIcon(icon)

        self.lay_button.addWidget(self.pb_ok)

        self.pb_cancel = QPushButton(CalibrationParameterizationView)
        self.pb_cancel.setObjectName(u"pb_cancel")
        icon1 = QIcon()
        icon1.addFile(u":/icons/ui/buttons/cancelicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pb_cancel.setIcon(icon1)

        self.lay_button.addWidget(self.pb_cancel)


        self.main_layout.addLayout(self.lay_button)


        self.retranslateUi(CalibrationParameterizationView)

        self.tab_widget.setCurrentIndex(0)
        self.cbx_clahe_grid.setCurrentIndex(1)
        self.pb_ok.setDefault(True)


        QMetaObject.connectSlotsByName(CalibrationParameterizationView)
    # setupUi

    def retranslateUi(self, CalibrationParameterizationView):
        CalibrationParameterizationView.setWindowTitle(QCoreApplication.translate("CalibrationParameterizationView", u"Par\u00e2metros de Calibra\u00e7\u00e3o", None))
        self.lbl_model_desktop.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Modelo MediaPipe Desktop:", None))
        self.grp_model_desktop.setTitle("")
        self.rb_model_desktop_lite.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Lite", None))
        self.rb_model_desktop_full.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Full", None))
        self.rb_model_desktop_heavy.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Heavy", None))
        self.lbl_model_embedded.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Modelo MediaPipe Embarcado:", None))
        self.grp_model_embedded.setTitle("")
        self.rb_model_embedded_lite.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Lite", None))
        self.rb_model_embedded_full.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Full", None))
        self.rb_model_embedded_heavy.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Heavy", None))
        self.lbl_embedded_processing.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Embarcado Processamento:", None))
        self.grp_embedded_processing.setTitle("")
        self.rb_embedded_processing_cpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CPU", None))
        self.rb_embedded_processing_gpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"GPU", None))
        self.lbl_linux_processing.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Linux Processamento:", None))
        self.grp_linux_processing.setTitle("")
        self.rb_linux_processing_cpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CPU", None))
        self.rb_linux_processing_gpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"GPU", None))
        self.lbl_mac_processing.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Mac Processamento:", None))
        self.groupBox_mac.setTitle("")
        self.rb_mac_processing_cpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CPU", None))
        self.rb_mac_processing_gpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"GPU", None))
        self.lbl_windows_processing.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Windows Processamento:", None))
        self.groupBox_windows.setTitle("")
        self.rb_windows_processing_cpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CPU", None))
        self.rb_windows_processing_gpu.setText(QCoreApplication.translate("CalibrationParameterizationView", u"GPU", None))
        self.lbl_execution_mode.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Modo de Execu\u00e7\u00e3o:", None))
        self.groupBox_execution_mode.setTitle("")
        self.rb_execution_mode_video.setText(QCoreApplication.translate("CalibrationParameterizationView", u"V\u00eddeo", None))
        self.lbl_detection_position.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Detec\u00e7\u00e3o de Posi\u00e7\u00e3o (0\u20131):", None))
        self.lbl_detection_presence.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Detec\u00e7\u00e3o de Presen\u00e7a (0\u20131):", None))
        self.lbl_detection_tracking.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Detec\u00e7\u00e3o de Rastreio (0\u20131):", None))
        self.lbl_num_position.setText(QCoreApplication.translate("CalibrationParameterizationView", u"N\u00famero de posi\u00e7\u00f5es:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_mediapipe), QCoreApplication.translate("CalibrationParameterizationView", u"MediaPipe", None))
        self.lbl_embedded_capture.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Embarcado Captura de V\u00eddeo:", None))
        self.grp_embedded_capture.setTitle("")
        self.rb_embedded_v4l2.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_V4L2", None))
        self.rb_embedded_gstreamer.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_GSTREAMER", None))
        self.lbl_linux_capture.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Linux Captura de V\u00eddeo:", None))
        self.grp_linux_capture.setTitle("")
        self.rb_linux_v4l2.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_V4L2", None))
        self.rb_linux_gstreamer.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_GSTREAMER", None))
        self.lbl_mac_capture.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Mac Captura de V\u00eddeo:", None))
        self.grp_mac_capture.setTitle("")
        self.rb_mac_avfoundation.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_AVFOUNDATION", None))
        self.rb_mac_any.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_ANY", None))
        self.lbl_windows_capture.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Windows Captura de V\u00eddeo:", None))
        self.grp_windows_capture.setTitle("")
        self.rb_windows_dshow.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_DSHOW", None))
        self.rb_windows_msmf.setText(QCoreApplication.translate("CalibrationParameterizationView", u"CAP_MSMF", None))
        self.lbl_buffer_size.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Tamanho do Buffer:", None))
        self.lbl_custom_camera.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Customizar Informa\u00e7\u00f5es C\u00e2mera?", None))
        self.grp_camera_info.setTitle(QCoreApplication.translate("CalibrationParameterizationView", u"Informa\u00e7\u00f5es da C\u00e2mera", None))
        self.lbl_ratio.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Propor\u00e7\u00e3o C\u00e2mera:", None))
        self.lbl_width.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Largura C\u00e2mera:", None))
        self.lbl_height.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Altura C\u00e2mera:", None))
        self.lbl_fps.setText(QCoreApplication.translate("CalibrationParameterizationView", u"FPS:", None))
        self.grp_fps.setTitle("")
        self.rb_fps_30.setText(QCoreApplication.translate("CalibrationParameterizationView", u"30", None))
        self.rb_fps_60.setText(QCoreApplication.translate("CalibrationParameterizationView", u"60", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_opencv), QCoreApplication.translate("CalibrationParameterizationView", u"OpenCV", None))
        self.lbl_use_filter.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Usar Filtros?", None))
        self.grp_filter.setTitle(QCoreApplication.translate("CalibrationParameterizationView", u"Configura\u00e7\u00f5es de Filtros", None))
        self.lbl_average_smooth_frames.setText(QCoreApplication.translate("CalibrationParameterizationView", u"M\u00e9dia M\u00f3vel Smooth Frames:", None))
        self.lbl_clahe_clip.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Filtro Clahe Limite Clip:", None))
        self.lbl_clahe_grid.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Filtro Clahe Tamanho Grid:", None))
        self.cbx_clahe_grid.setItemText(0, QCoreApplication.translate("CalibrationParameterizationView", u"4:4", None))
        self.cbx_clahe_grid.setItemText(1, QCoreApplication.translate("CalibrationParameterizationView", u"8:8", None))
        self.cbx_clahe_grid.setItemText(2, QCoreApplication.translate("CalibrationParameterizationView", u"16:16", None))
        self.cbx_clahe_grid.setItemText(3, QCoreApplication.translate("CalibrationParameterizationView", u"32:32", None))

        self.lbl_clahe_lum_below.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Filtro Clahe Aplicar Quando Valor de Luminosidade Abaixo de:", None))
        self.lbl_gamma_factor.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Filtro Gamma Fator de Divis\u00e3o:", None))
        self.lbl_gamma_lum_above.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Filtro Gamma Aplicar Quando Valor de Luminosidade Acima de:", None))
        self.lbl_landmark_limit.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Filtro Landmark Limite de Movimento:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_filter), QCoreApplication.translate("CalibrationParameterizationView", u"Filtros", None))
        self.lbl_telemetry_placeholder.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Configura\u00e7\u00f5es de telemetria ser\u00e3o adicionadas aqui...", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_telemetry), QCoreApplication.translate("CalibrationParameterizationView", u"Telemetria", None))
#if QT_CONFIG(tooltip)
        self.pb_ok.setToolTip(QCoreApplication.translate("CalibrationParameterizationView", u"Gravar opera\u00e7\u00e3o corrente", None))
#endif // QT_CONFIG(tooltip)
        self.pb_ok.setText(QCoreApplication.translate("CalibrationParameterizationView", u"OK", None))
#if QT_CONFIG(tooltip)
        self.pb_cancel.setToolTip(QCoreApplication.translate("CalibrationParameterizationView", u"Cancelar opera\u00e7\u00e3o corrente", None))
#endif // QT_CONFIG(tooltip)
        self.pb_cancel.setText(QCoreApplication.translate("CalibrationParameterizationView", u"Cancelar", None))
    # retranslateUi

