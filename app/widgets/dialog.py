from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6.QtCore import QDate

class AppointmentDialog(QDialog):
    STYLE_LOCATION = "style_popup.qss"
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        with open(self.STYLE_LOCATION, "r") as style_file:
            self.setStyleSheet(style_file.read())
        
    def setup_connections(self):
        pass
        
    def get_appointment_data(self):
        return {
            "hospital": self.ui.hospitalInput.text(),
            "doctor": self.ui.doctorInput.text(),
            "date": self.ui.dateInput.date().toPyDate(),
            "time": self.ui.timeInput.time().toString(),
            "price": float(self.ui.priceInput.text())
        }

class AddAppointmentDialog(AppointmentDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("add_appointment_dialog.ui", self)
        self.ui.dateInput.setDisplayFormat("dd/MM/yyyy")

class EditAppointmentDialog(AppointmentDialog):
    def __init__(self, appointment_data):
        super().__init__()
        self.ui = uic.loadUi("edit_appointment_dialog.ui", self)
        self.ui.dateInput.setDisplayFormat("dd/MM/yyyy")
        
        # Pre-fill fields with existing data
        self.ui.hospitalInput.setText(appointment_data["hospital"])
        self.ui.doctorInput.setText(appointment_data["doctor"])
        qdate = QDate(appointment_data["date"].year, 
                     appointment_data["date"].month, 
                     appointment_data["date"].day)
        self.ui.dateInput.setDate(qdate)
        self.ui.timeInput.setTime(appointment_data["time"])
        self.ui.priceInput.setText(str(appointment_data["price"]))