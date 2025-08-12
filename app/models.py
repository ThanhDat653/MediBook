import operator
from datetime import datetime

from app.data_io import load_json_data, write_json_data


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
        # self.hospital_list = self.get_hospital_list()
    
    def item_to_data(self):
        json_data = list()
        for appointment in self.appointment_item_list:
            json_data.append(appointment.__dict__)
        return json_data

    def load_data(self):
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

    def get_item_by_hospital(self, hospital_name) -> AppointmentItem:
        for appointment_item in self.appointment_item_list:
            if appointment_item.hospital == hospital_name:
                return appointment_item

    def add_item_from_dict(self, appointment_dict):
        appointment_dict["id"] = len(self.appointment_item_list)
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
        self.appointment_dict_data.append(appointment_dict)
        write_json_data(self.appointment_dict_data)
    
    def edit_item_from_dict(self, edit_hospital, appointment_dict: AppointmentItem):
        appointment_edit = self.get_item_by_hospital(edit_hospital)
        appointment_edit.update(appointment_dict)
        self.appointment_dict_data = self.item_to_data()
        write_json_data(self.appointment_dict_data)
    
    def delete_item(self, delete_hospital):
        appointment_delete = self.get_item_by_hospital(delete_hospital)
        self.appointment_item_list.remove(appointment_delete)
        self.appointment_dict_data = self.item_to_data()
        write_json_data(self.appointment_dict_data)
    
    def search_by_hospital(self, search_hospital) -> list[AppointmentItem]:
        matched_items = []
        for appointment_item in self.appointment_item_list:
            if search_hospital in appointment_item.hospital:
                matched_items.append(appointment_item)
        return matched_items

    def sort_item_by_price(self, top=None):
        self.appointment_item_list = sorted(
            self.appointment_item_list, 
            key=operator.attrgetter('price'),
            reverse=True
        )
        if top:
            return self.appointment_item_list[:top]
    
    def sort_item_by_date(self, top=None):
        self.appointment_item_list = sorted(
            self.appointment_item_list, 
            key=lambda x: format_date(x.date),
            reverse=True
        )
        if top:
            return self.appointment_item_list[:top]
    
    def get_hospital_list(self):
        hospitals = [appointment["hospital"] for appointment in self.appointment_dict_data]
        return hospitals


def format_date(date_text):
    return datetime.strptime(date_text, '%b %Y')


def date_to_text(date: datetime):
    return date.strftime("%b %Y")
