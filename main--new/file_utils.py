import os
import json

def save_file(folder_name, file_name, content):

    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'w') as file:
        file.write(content)

    # print(f"File '{file_name}' saved in folder '{folder_name}'.")

def save_dict(folder_name, file_name, content):

    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=4, ensure_ascii=False)


    # print(f"File '{file_name}' saved in folder '{folder_name}'.")

