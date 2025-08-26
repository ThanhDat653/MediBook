import os

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QHBoxLayout, QListWidgetItem
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QPixmap, QIcon

from config import Config
try:
    from PyQt6 import Ui_MainWindow
except ImportError:
    pass

from app.models import AppointmentDatabase
from app.widgets.appointment import AppointmentItemWidget
from app.widgets.dialog import AddAppointmentDialog, EditAppointmentDialog


class MainWindow(QMainWindow):
    UI_LOCATION = os.path.join(Config.UI_DIR, "main_window.ui")
    STYLE_LOCATION = os.path.join(Config.UI_DIR, "style_main.qss")
    
    def __init__(self):
        super(MainWindow, self).__init__()
        try:
            self.ui = uic.loadUi(self.UI_LOCATION, self)
        except FileNotFoundError:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

        with open(self.STYLE_LOCATION, "r") as style_file:
            style_config = style_file.read()
        self.setStyleSheet(style_config)

        # Thay thế biến global bằng instance variables
        self.widgets = self.ui
        self.database = AppointmentDatabase()
        self.horizontal_layout = QHBoxLayout(self.widgets.appointmentListWidget)
        self.horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Khởi tạo các lớp helper với tham chiếu đến main window
        self.crud_handler = AppointmentCRUD(self)
        self.layout_handler = AppointmentHorizontalLayout(self)

        self.widgets.stackedWidget.setCurrentIndex(Config.HOME_PAGE_INDEX)
        self.setup_leftMenu()
        self.setup_CRUD_page()
        self.setup_rank_page()

    def setup_leftMenu(self):
        self.widgets.leftMenu.show()
        self.widgets.logoLabel_3.hide()
        self.widgets.toggleButton.clicked.connect(lambda: self.on_leftMenu_toggled())

    def setup_CRUD_page(self):
        self.database.load_data()
        # Nếu chỉ cần text:
        self.widgets.appointmentList.addItems(
            [f"{item.hospital} - {item.doctor} - {item.time}" for item in self.database.appointment_item_list]
        )
        self.widgets.appointmentList.setCurrentRow(0)
        self.widgets.addButton.clicked.connect(lambda: self.crud_handler.add())
        self.widgets.editButton.clicked.connect(lambda: self.crud_handler.edit())
        self.widgets.removeButton.clicked.connect(lambda: self.crud_handler.delete())
        self.widgets.searchAppointment.clicked.connect(lambda: self.crud_handler.search())

    def setup_rank_page(self):
        self.layout_handler.display_layout()
        self.widgets.sortRankButton.clicked.connect(lambda: self.layout_handler.sort_by_rating())
        self.widgets.sortDateButton.clicked.connect(lambda: self.layout_handler.sort_by_date())
        self.widgets.AtoZButton.clicked.connect(lambda: self.layout_handler.sort_by_alphabet())

    def on_searchButton_clicked(self):
        self.widgets.stackedWidget.setCurrentIndex(Config.RANK_PAGE_INDEX)
        search_text = self.widgets.searchInput.text().strip()

        if search_text:
            matched_items = self.database.search_by_title(search_text)
            self.layout_handler.clear_layout()
            if len(matched_items) != 0:
                formatted_text = f"Search results for \"{search_text}\""
                self.layout_handler.update_layout(item_list=matched_items)
            else:
                formatted_text = f"No results for \"{search_text}\""
            
            self.widgets.searchInput.setPlaceholderText(formatted_text)
            return matched_items

    def on_userButton_clicked(self):
        self.widgets.stackedWidget.setCurrentIndex(Config.USER_PAGE_INDEX)

    def on_homeButton_toggled(self):
        self.widgets.stackedWidget.setCurrentIndex(Config.HOME_PAGE_INDEX)

    def on_tvshowsButton_toggled(self):
        self.widgets.stackedWidget.setCurrentIndex(Config.TVSHOW_PAGE_INDEX)

    def on_CRUDButton_toggled(self):
        self.widgets.stackedWidget.setCurrentIndex(Config.CRUD_MENU_INDEX)

    def on_rankButton_toggled(self):
        self.widgets.stackedWidget.setCurrentIndex(Config.RANK_PAGE_INDEX)
    
    def on_rankButton_clicked(self):
        self.layout_handler.update_layout()

    def on_exitButton_clicked(self):
        QApplication.quit()

    def on_leftMenu_toggled(self):
        # Get width
        width = self.widgets.leftMenu.width()
        maxExtend = Config.MENU_FULL_WIDTH
        standard = Config.MENU_COLLAPSED_WIDTH
        # Get current icon
        icon = QIcon()

        # Set animation width and icon 
        if width == standard:
            widthExtended = maxExtend
            icon.addPixmap(QPixmap("ui/sidebar/x-solid-f26419.svg"))
        else:
            widthExtended = standard
            icon.addPixmap(QPixmap("ui/sidebar/bars-solid-f26419.svg"))

        # Animation 
        self.animation = QPropertyAnimation(self.widgets.leftMenu, b"minimumWidth")
        self.animation.setDuration(Config.TOGGLE_ANIMATION_DURATION)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.animation.start()
        self.widgets.toggleButton.setIcon(icon)


class AppointmentCRUD():
    def __init__(self, main_window):
        self.main_window = main_window
        self.widgets = main_window.widgets
        self.database = main_window.database

    def add(self):
        currIndex = self.widgets.appointmentList.currentRow()
        add_dialog = AddAppointmentDialog()
        if add_dialog.exec():
            inputs = add_dialog.return_input_fields()
            self.widgets.appointmentList.insertItem(currIndex, inputs["title"])
            self.database.add_item_from_dict(inputs)

    def edit(self):
        curr_index = self.widgets.appointmentList.currentRow()
        item = self.widgets.appointmentList.item(curr_index)
        if item is not None:
            item_title = item.text()
            edit_item = self.database.get_item_by_title(item_title)
            edit_dialog = EditAppointmentDialog(edit_item)
            if edit_dialog.exec():
                inputs = edit_dialog.return_input_fields()
                item.setText(inputs["title"])
                self.database.edit_item_from_dict(item_title, inputs)

    def delete(self):
        curr_index = self.widgets.appointmentList.currentRow()
        item = self.widgets.appointmentList.item(curr_index)
        if item is None:
            return
        
        item_title = item.text()
        question = QMessageBox.question(self.main_window, "Remove Appointment",
                                        "Do you want to remove this appointment?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if question == QMessageBox.StandardButton.Yes:
            self.widgets.appointmentList.takeItem(curr_index)
            self.database.delete_item(item_title)

    def search(self):
        search_appointment_field = self.widgets.inputappointment.text().strip()
        if search_appointment_field:
            matched_items = self.widgets.appointmentList.findItems(search_appointment_field, Qt.MatchFlag.MatchContains)
            for i in range(self.widgets.appointmentList.count()):
                it = self.widgets.appointmentList.item(i)
                it.setHidden(it not in matched_items)
        else:
            for i in range(self.widgets.appointmentList.count()):
                it = self.widgets.appointmentList.item(i)
                it.setHidden(False)
    

class AppointmentHorizontalLayout():
    def __init__(self, main_window):
        self.main_window = main_window
        self.widgets = main_window.widgets
        self.database = main_window.database
        self.h_layout = main_window.horizontal_layout

    def display_layout(self):
        print("display_layout called")
        print("Number of appointments:", len(self.database.appointment_item_list))
        self.clear_layout()
        if not self.database.appointment_item_list:
            print("No appointments loaded!")
        for appointment in self.database.appointment_item_list:
            print("Adding appointment:", appointment)
            appointment_item_widget = AppointmentItemWidget(appointment)
            self.h_layout.addWidget(appointment_item_widget)
        self.widgets.appointmentListWidget.setLayout(self.h_layout)
    
    def clear_layout(self):
        while self.h_layout.count():
            child = self.h_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_layout(self, item_list=None):
        self.clear_layout()
        
        if item_list is None:
            item_list = self.database.appointment_item_list
        # Update layout from custom item list
        for appointment in item_list:
            appointment_item_widget = AppointmentItemWidget(appointment)
            self.h_layout.addWidget(appointment_item_widget)

    def sort_by_rating(self):
        self.database.sort_item_by_rating()
        self.update_layout()

    def sort_by_date(self):
        self.database.sort_item_by_date()
        self.update_layout()
    
    def sort_by_alphabet(self):
        self.database.sort_item_by_title()
        self.update_layout()