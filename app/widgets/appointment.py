import webbrowser
import os

from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QColorConstants
from PyQt6.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt

from config import Config
try:
    from ui.appointment_column_ui import Ui_AppointmentColumn
except ImportError:
    pass
from app.models import AppointmentItem


class AppointmentItemWidget(QWidget):
    STYLE_LOCATION = os.path.join(Config.UI_DIR, "style_appointment.qss")
    UI_LOCATION = os.path.join(Config.UI_DIR, "appointment_column.ui")
    
    def __init__(self, appointment: AppointmentItem):
        super().__init__()  # Use super() instead of QWidget.__init__()
        try:
            self.ui = uic.loadUi(self.UI_LOCATION, self)
        except FileNotFoundError:
            self.ui = Ui_AppointmentColumn()
            self.ui.setupUi(self)

        with open(self.STYLE_LOCATION, "r") as style_file:
            style_config = style_file.read()
        self.setStyleSheet(style_config)

        self.appointment = appointment
        self.display_description()

        # Initialize animation effects
        self.animation = Animation()
        self.animation.setup_hover_effects(self.ui.appointmentCol)
        
        # Connect double click event
        self.ui.appointmentCol.mouseDoubleClickEvent = self.handle_double_click
        
        if self.appointment.link != 'None':
            self.ui.appointmentCol.setToolTip("Double click to view details")

    def display_description(self):
        description_text = f"Hospital: {self.appointment.hospital}\n" \
                          f"Specialty: {self.appointment.date}\n" \
                          f"Price: {str(self.appointment.price)}/10"
        img_pixmap = QPixmap(self.appointment.image)
        self.ui.appointmentTitle.setText(self.appointment.name)
        self.ui.appointmentInfo.setText(description_text)
        self.ui.appointmentView.setPixmap(img_pixmap.scaled(
            self.ui.appointmentView.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def handle_double_click(self, event):
        self.open_link(self.appointment.link)
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