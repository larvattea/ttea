"""Launch a source game immediately beside a synthetic tracking editor."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget)

from .cartridge import read_project
from .simulator import BODY_EDGES, BODY_NAMES, EXPRESSIONS, HAND_EDGES, HAND_NAMES, SimulatorProvider, write_state
from .tracking import Recording, ReplayProvider


class LandmarkCanvas(QWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        self.dragging = False
        self.setMinimumSize(540, 540)
        self.setToolTip('Drag any joint. Coordinates outside the border remain out of area.')

    def point(self, landmark):
        return QPointF(40 + landmark.x * (self.width()-80), 40 + landmark.y * (self.height()-80))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#18202b'))
        painter.setPen(QPen(QColor('#64748b'),1))
        painter.drawRect(40,40,self.width()-80,self.height()-80)
        model = self.panel.provider
        for group,points in model.observation.landmarks.items():
            color = QColor('#5eead4' if group != 'right' else '#fbbf24')
            if group in model.hidden or not model.observation.present:
                color.setAlpha(65)
            painter.setPen(QPen(color,1))
            edges = BODY_EDGES if group == 'body' else (HAND_EDGES if group != 'face' else [])
            for a,b in edges:
                painter.drawLine(self.point(points[a]),self.point(points[b]))
            for index,point in enumerate(points):
                selected = group == self.panel.group.currentText() and index == self.panel.joint.currentIndex()
                painter.setBrush(QColor('#f87171') if selected else color)
                radius = 5 if selected else (2 if group == 'face' else 4)
                painter.drawEllipse(self.point(point),radius,radius)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        group = self.panel.group.currentText()
        points = self.panel.provider.observation.landmarks[group]
        index = min(range(len(points)), key=lambda i:(self.point(points[i])-event.position()).manhattanLength())
        if (self.point(points[index])-event.position()).manhattanLength() < 25:
            self.panel.joint.setCurrentIndex(index)
            self.dragging = True
            self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.panel.coordinates[0].setValue((event.position().x()-40)/(self.width()-80))
            self.panel.coordinates[1].setValue((event.position().y()-40)/(self.height()-80))

    def mouseReleaseEvent(self, event):
        self.dragging = False


class DeveloperPanel(QMainWindow):
    def __init__(self, project, manifest, state_path, process):
        super().__init__()
        self.provider = SimulatorProvider(manifest['tracking_profile'])
        self.state_path = state_path
        self.process = process
        self.project = project
        self.recorder = None
        self.replaying = False
        self.loading = False
        self.setWindowTitle(f"TSDK developer — {manifest['id']} — synthetic session")
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        self.canvas = LandmarkCanvas(self)
        layout.addWidget(self.canvas,1)
        controls = QVBoxLayout()
        layout.addLayout(controls)
        controls.addWidget(QLabel('Synthetic data only · no camera\nDrag joints or edit exact coordinates.'))
        form = QFormLayout()
        controls.addLayout(form)
        self.group = QComboBox()
        self.group.addItems(list(self.provider.observation.landmarks))
        form.addRow('Subject', self.group)
        self.joint = QComboBox()
        form.addRow('Joint / mesh vertex',self.joint)
        self.coordinates = []
        for label in ('X (camera normalized)','Y (camera normalized)','Z (image-relative depth)','Visibility'):
            spin = QDoubleSpinBox()
            spin.setRange(-1.,1.) if label == 'Visibility' else spin.setRange(-100.,100.)
            if label == 'Visibility':
                spin.setSpecialValueText('Unknown')
            spin.setDecimals(4)
            spin.setSingleStep(.01)
            spin.valueChanged.connect(self.edit_joint)
            self.coordinates.append(spin)
            form.addRow(label,spin)
        self.preset = QComboBox()
        self.preset.addItems({'body':['standing','arms_up','squat'],'hands':['open','fist','pinch'],'face':['neutral','smile','surprise','blink']}[self.provider.profile])
        form.addRow('Preset',self.preset)
        button = QPushButton('Apply preset to selected subject')
        button.clicked.connect(self.apply_preset)
        controls.addWidget(button)
        for axis,label in enumerate(('Move X','Move Y','Move Z')):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            for sign in (-1,1):
                button = QPushButton('−' if sign < 0 else '+')
                button.clicked.connect(lambda checked=False,a=axis,s=sign:self.move_subject(a,s*.025))
                row.addWidget(button)
            controls.addLayout(row)
        for axis,label in enumerate(('Pitch','Yaw','Roll')):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            for sign in (-1,1):
                button = QPushButton('−5°' if sign < 0 else '+5°')
                button.clicked.connect(lambda checked=False,a=axis,s=sign:self.rotate_subject(a,s*5))
                row.addWidget(button)
            controls.addLayout(row)
        self.present = QCheckBox('Participant present')
        self.present.setChecked(True)
        self.present.toggled.connect(self.set_present)
        controls.addWidget(self.present)
        self.subject_present = QCheckBox('Selected subject visible')
        self.subject_present.setChecked(True)
        self.subject_present.toggled.connect(self.set_subject_present)
        controls.addWidget(self.subject_present)
        self.stale = QCheckBox('Freeze timestamp (stale input)')
        self.stale.toggled.connect(self.set_stale)
        controls.addWidget(self.stale)
        if self.provider.profile == 'face':
            self.expression = QComboBox()
            self.expression.addItems(EXPRESSIONS)
            form.addRow('Expression coefficient',self.expression)
            self.expression_value = QSlider(Qt.Orientation.Horizontal)
            self.expression_value.setRange(0,100)
            form.addRow('Expression 0–1',self.expression_value)
            self.expression.currentTextChanged.connect(self.load_expression)
            self.expression_value.valueChanged.connect(self.set_expression)
        self.record_button = QPushButton('Record observations…')
        self.record_button.clicked.connect(self.toggle_record)
        controls.addWidget(self.record_button)
        button = QPushButton('Replay recording…')
        button.clicked.connect(self.start_replay)
        controls.addWidget(button)
        button = QPushButton('Return to live simulation')
        button.clicked.connect(self.stop_replay)
        controls.addWidget(button)
        self.status = QLabel('Live simulation')
        self.status.setWordWrap(True)
        controls.addWidget(self.status)
        controls.addStretch()
        self.group.currentTextChanged.connect(self.load_group)
        self.joint.currentIndexChanged.connect(self.load_joint)
        self.load_group()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def load_group(self):
        self.joint.blockSignals(True)
        self.joint.clear()
        group = self.group.currentText()
        names = BODY_NAMES if group == 'body' else (HAND_NAMES if group != 'face' else [f'vertex {i}' for i in range(478)])
        self.joint.addItems([f'{i}: {name}' for i,name in enumerate(names)])
        self.joint.blockSignals(False)
        self.subject_present.blockSignals(True)
        self.subject_present.setChecked(group not in self.provider.hidden)
        self.subject_present.blockSignals(False)
        self.load_joint()

    def load_joint(self):
        index = self.joint.currentIndex()
        if index < 0:
            return
        point = self.provider.observation.landmarks[self.group.currentText()][index]
        self.loading = True
        for spin,value in zip(self.coordinates,(point.x,point.y,point.z or 0.,point.visibility if point.visibility is not None else -1.)):
            spin.setValue(value)
        self.loading = False
        self.canvas.update()

    def edit_joint(self):
        if not self.loading:
            x,y,z,visibility = [spin.value() for spin in self.coordinates]
            self.provider.set_joint(self.group.currentText(),self.joint.currentIndex(),x,y,z,
                                    None if visibility < 0 else visibility)
            self.canvas.update()

    def apply_preset(self):
        self.provider.preset(self.group.currentText(),self.preset.currentText())
        self.load_joint()
        if self.provider.profile == 'face':
            self.load_expression()

    def move_subject(self, axis, amount):
        delta = [0.,0.,0.]
        delta[axis] = amount
        self.provider.move(self.group.currentText(),*delta)
        self.load_joint()

    def rotate_subject(self, axis, amount):
        angles = [0.,0.,0.]
        angles[axis] = amount
        self.provider.rotate(self.group.currentText(),*angles)
        self.load_joint()

    def set_present(self, value):
        self.provider.observation = replace(self.provider.observation,present=value)
        self.canvas.update()

    def set_subject_present(self, value):
        if value:
            self.provider.hidden.discard(self.group.currentText())
        else:
            self.provider.hidden.add(self.group.currentText())
        self.canvas.update()

    def set_stale(self, value):
        self.provider.stale = value

    def load_expression(self):
        self.expression_value.blockSignals(True)
        self.expression_value.setValue(round(self.provider.observation.expressions.get(self.expression.currentText(),0.)*100))
        self.expression_value.blockSignals(False)

    def set_expression(self, value):
        self.provider.observation.expressions[self.expression.currentText()] = value/100

    def toggle_record(self):
        if self.recorder:
            self.recorder.close()
            self.recorder = None
            self.record_button.setText('Record observations…')
            return
        filename,_ = QFileDialog.getSaveFileName(self,'Record synthetic observations','','JSON Lines (*.jsonl)')
        if filename:
            self.recorder = Recording(Path(filename),self.provider.profile,calibration=None,config={})
            self.record_button.setText('Stop recording')

    def start_replay(self):
        filename,_ = QFileDialog.getOpenFileName(self,'Replay synthetic observations','','JSON Lines (*.jsonl)')
        if not filename:
            return
        try:
            replay = ReplayProvider(Path(filename))
            try:
                if replay.profile != self.provider.profile:
                    raise ValueError('Recording profile does not match this game')
                replay.read()
            finally:
                replay.close()
        except (OSError, ValueError, StopIteration) as exc:
            QMessageBox.warning(self, 'Cannot replay', str(exc))
            return
        if self.recorder:
            self.toggle_record()
        self.restart_game(Path(filename))
        self.replaying = True
        self.record_button.setEnabled(False)
        self.status.setText('Replay runs in game window using recorded calibration and processing times.')

    def stop_replay(self):
        if self.replaying or self.process.poll() is not None:
            write_state(self.state_path, self.provider)
            self.restart_game()
        self.replaying = False
        self.record_button.setEnabled(True)
        self.status.setText('Live simulation')

    def restart_game(self, replay=None):
        self.stop_process()
        stop_file = self.state_path.with_suffix('.stop')
        stop_file.unlink(missing_ok=True)
        config = {'session_root': str(self.state_path.parent/'sessions'), 'synthetic': True, 'stop_file': str(stop_file)}
        if replay is None:
            config['simulation_state'] = str(self.state_path)
        command = [sys.executable, '-m', 'ttea.sdk.runtime', str(self.project), '--config', json.dumps(config)]
        if replay is None:
            command.append('--simulation')
        else:
            command.extend(['--replay', str(replay)])
        self.process = subprocess.Popen(command)
        self.timer.start(16)

    def stop_process(self):
        if self.process.poll() is None:
            self.state_path.with_suffix('.stop').touch()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

    def tick(self):
        if self.process.poll() is not None:
            self.status.setText(f'Game exited with status {self.process.returncode}')
            self.timer.stop()
            if self.recorder:
                self.recorder.close()
                self.recorder = None
                self.record_button.setText('Record observations…')
            return
        if not self.replaying:
            observation = write_state(self.state_path,self.provider)
            if self.recorder:
                self.recorder.write(observation)

    def closeEvent(self, event):
        self.timer.stop()
        if self.recorder:
            self.recorder.close()
        self.stop_process()
        event.accept()


def run(project: Path) -> int:
    project = project.resolve()
    manifest = read_project(project)
    app = QApplication.instance() or QApplication([sys.argv[0]])
    with tempfile.TemporaryDirectory(prefix='tsdk-synthetic-') as directory:
        root = Path(directory)
        state = root/'simulation.json'
        write_state(state,SimulatorProvider(manifest['tracking_profile']))
        config = {'simulation_state':str(state),'session_root':str(root/'sessions'),'synthetic':True, 'stop_file':str(state.with_suffix('.stop'))}
        command = [sys.executable,'-m','ttea.sdk.runtime',str(project),'--simulation','--config',json.dumps(config)]
        process = subprocess.Popen(command)
        panel = None
        try:
            panel = DeveloperPanel(project,manifest,state,process)
            panel.resize(1040,820)
            panel.show()
            return app.exec()
        finally:
            if panel is not None:
                if panel.recorder:
                    panel.recorder.close()
                panel.stop_process()
            elif process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
