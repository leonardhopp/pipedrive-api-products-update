import json

def load_file(file_name):
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data

def save_data(data, file_name):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=2)