import json
from config import Config


def load_json_data():
    print("Config.JSON_PATH:", Config.JSON_PATH)
    appointment_dict_data = []
    try:
        with open(Config.JSON_PATH, "r", encoding="utf-8") as json_in:
            json_data = json.load(json_in)
        appointment_dict_data.extend(json_data)
    except FileNotFoundError:
        print("Không tìm thấy file:", Config.JSON_PATH)
    print("appointment_dict_data:", appointment_dict_data)
    return appointment_dict_data

def write_json_data(json_data):
    with open(Config.JSON_PATH, "w", encoding="utf-8") as json_out:
        json.dump(json_data, json_out, ensure_ascii=False, indent=4)
    
    