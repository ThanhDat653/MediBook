import operator
from datetime import datetime
import json
import os

# Thay thế import từ data_io bằng hàm trực tiếp
def load_json_data():
    """Load data from JSON file"""
    try:
        with open('appointments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_json_data(data):
    """Write data to JSON file"""
    with open('appointments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class AppointmentItem:
    def __init__(self, appointment_id, hospital, doctor, time, date, price=None, image=None, link=None):
        self.id = appointment_id
        self.hospital = hospital
        self.doctor = doctor
        self.time = time
        self.date = date
        self.price = float(price) if price else None
        self.image = image
        self.link = link

    def __str__(self):
        return f"{self.hospital}\t{self.doctor}\t{self.time}\t{self.date}\t{self.price}\t{bool(self.image)}\t{self.link}"
    
    def update(self, new_data):
        # Empty field is not updated
        for k, v in new_data.items():
            if v:
                setattr(self, k, v)


class AppointmentDatabase:
    def __init__(self):
        self.appointment_item_list = list()
        self.appointment_dict_data = load_json_data()
        self.load_data()
    
    def item_to_data(self):
        json_data = list()
        for appointment in self.appointment_item_list:
            json_data.append({
                "id": appointment.id,
                "hospital": appointment.hospital,
                "doctor": appointment.doctor,
                "time": appointment.time,
                "date": appointment.date,
                "price": appointment.price,
                "image": appointment.image,
                "link": appointment.link
            })
        return json_data

    def load_data(self):
        self.appointment_item_list.clear()
        for appointment_dict in self.appointment_dict_data:
            appointment = AppointmentItem(
                appointment_id=appointment_dict["id"],
                hospital=appointment_dict["hospital"],
                doctor=appointment_dict["doctor"],
                time=appointment_dict["time"],
                date=appointment_dict["date"],
                price=appointment_dict.get("price"),
                image=appointment_dict.get("image"),
                link=appointment_dict.get("link")
            )
            self.appointment_item_list.append(appointment)

    def get_item_by_id(self, item_id) -> AppointmentItem:
        for appointment_item in self.appointment_item_list:
            if appointment_item.id == item_id:
                return appointment_item
        return None

    def get_items_by_hospital(self, hospital_name) -> list[AppointmentItem]:
        matched_items = []
        for appointment_item in self.appointment_item_list:
            if hospital_name.lower() in appointment_item.hospital.lower():
                matched_items.append(appointment_item)
        return matched_items

    def add_item_from_dict(self, appointment_dict):
        # Tạo ID mới dựa trên ID cao nhất hiện có + 1
        max_id = max([item.id for item in self.appointment_item_list]) if self.appointment_item_list else -1
        appointment_dict["id"] = max_id + 1
        
        new_item = AppointmentItem(
            appointment_id=appointment_dict["id"],
            hospital=appointment_dict["hospital"],
            doctor=appointment_dict["doctor"],
            time=appointment_dict["time"],
            date=appointment_dict["date"],
            price=appointment_dict.get("price"),
            image=appointment_dict.get("image"),
            link=appointment_dict.get("link")
        )
        self.appointment_item_list.append(new_item)
        self.appointment_dict_data = self.item_to_data()
        write_json_data(self.appointment_dict_data)
    
    def edit_item_from_dict(self, item_id, appointment_dict):
        appointment_edit = self.get_item_by_id(item_id)
        if appointment_edit:
            appointment_edit.update(appointment_dict)
            self.appointment_dict_data = self.item_to_data()
            write_json_data(self.appointment_dict_data)
            return True
        return False
    
    def delete_item(self, item_id):
        appointment_delete = self.get_item_by_id(item_id)
        if appointment_delete:
            self.appointment_item_list.remove(appointment_delete)
            self.appointment_dict_data = self.item_to_data()
            write_json_data(self.appointment_dict_data)
            return True
        return False
    
    def search_by_hospital(self, search_hospital) -> list[AppointmentItem]:
        matched_items = []
        for appointment_item in self.appointment_item_list:
            if search_hospital.lower() in appointment_item.hospital.lower():
                matched_items.append(appointment_item)
        return matched_items

    def sort_item_by_price(self, top=None):
        # Sắp xếp theo price, items không có price sẽ ở cuối
        sorted_list = sorted(
            self.appointment_item_list, 
            key=lambda x: (x.price is None, x.price),
            reverse=False
        )
        if top:
            return sorted_list[:top]
        return sorted_list
    
    def sort_item_by_date(self, top=None):
        # Sắp xếp theo date, xử lý các định dạng date khác nhau
        def parse_date(date_str):
            try:
                # Thử các định dạng date phổ biến
                for fmt in ('%b %Y', '%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                return datetime.min  # Nếu không parse được, đặt ở đầu
            except:
                return datetime.min
        
        sorted_list = sorted(
            self.appointment_item_list, 
            key=lambda x: parse_date(x.date),
            reverse=True
        )
        if top:
            return sorted_list[:top]
        return sorted_list
    
    def get_hospital_list(self):
        hospitals = list(set([appointment.hospital for appointment in self.appointment_item_list]))
        return sorted(hospitals)


def format_date(date_text):
    """Chuyển date text thành datetime object"""
    try:
        for fmt in ('%b %Y', '%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'):
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue
        return datetime.min
    except:
        return datetime.mins


def date_to_text(date: datetime):
    """Chuyển datetime object thành text theo format chuẩn"""
    return date.strftime("%b %Y")