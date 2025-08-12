import webbrowser
import os

from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QColorConstants
from PyQt6.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt

from config import Config
try:
    from ui.doctor_column_ui import Ui_doctorColumn
except ImportError:
    pass
from app.models import AppointmentItem


class AppointmentItemWidget(QWidget):
    STYLE_LOCATION = os.path.join(Config.UI_DIR, "style_doctor.qss")
    UI_LOCATION = os.path.join(Config.UI_DIR, "doctor_column.ui")
    
    def __init__(self, doctor: AppointmentItem):
        super().__init__()  # Use super() instead of QWidget.__init__()
        try:
            self.ui = uic.loadUi(self.UI_LOCATION, self)
        except FileNotFoundError:
            self.ui = Ui_doctorColumn()
            self.ui.setupUi(self)

        with open(self.STYLE_LOCATION, "r") as style_file:
            style_config = style_file.read()
        self.setStyleSheet(style_config)

        self.doctor = doctor
        self.display_description()

        # Initialize animation effects
        self.animation = Animation()
        self.animation.setup_hover_effects(self.ui.doctorCol)
        
        # Connect double click event
        self.ui.doctorCol.mouseDoubleClickEvent = self.handle_double_click
        
        if self.doctor.link != 'None':
            self.ui.doctorCol.setToolTip("Double click to view details")

    def display_description(self):
        description_text = f"Hospital: {self.doctor.hospital}\n" \
                          f"Specialty: {self.doctor.specialty}\n" \
                          f"Rating: {str(self.doctor.rating)}/10"
        img_pixmap = QPixmap(self.doctor.image)
        self.ui.doctorName.setText(self.doctor.name)
        self.ui.doctorInfo.setText(description_text)
        self.ui.doctorView.setPixmap(img_pixmap.scaled(
            self.ui.doctorView.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def handle_double_click(self, event):
        self.open_link(self.doctor.link)
        event.accept()

    def open_link(self, url):
        if url != 'None':
            webbrowser.open(url)


class Animation:
    @staticmethod
    def drop_shadow_on(target_widget):
        effect = QGraphicsDropShadowEffect(target_widget)
        effect.setColor(QColorConstants.White)
        effect.setOffset(*Config.DROP_SHADOW_OFFSET)
        effect.setBlurRadius(Config.DROP_SHADOW_BLUR_RADIUS)
        target_widget.setGraphicsEffect(effect)

    @staticmethod
    def drop_shadow_off(target_widget):
        target_widget.setGraphicsEffect(None)

    def setup_hover_effects(self, target_widget):
        # Store original event functions
        original_enter = target_widget.enterEvent
        original_leave = target_widget.leaveEvent
        
        def enter_event(event):
            self.drop_shadow_on(target_widget)
            if original_enter:
                original_enter(event)
                
        def leave_event(event):
            self.drop_shadow_off(target_widget)
            if original_leave:
                original_leave(event)
                
        target_widget.enterEvent = enter_event
        target_widget.leaveEvent = leave_event