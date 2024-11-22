import re
from file_utils import save_file

def extract_class_info(rebeca_code):
    find_class_names = re.findall(r'reactiveclass\s+(\w+)\s*\(([^)]*)\)', rebeca_code)
    class_info = [{"name": name, "queue_length": param} for name, param in find_class_names]
    return class_info

def extract_reactiveclass_blocks(inputFileName, rebeca_code, class_info):
    reactiveclass_blocks = re.findall(r'reactiveclass\s+\w+\s*\([^)]*\)\s*\{(.*?)\}(?=\s*reactiveclass|\s*main|\Z)', rebeca_code, re.DOTALL)
    for i, block in enumerate(reactiveclass_blocks):
        save_file(f'{inputFileName}_parts', f"{class_info[i]['name']}.txt", block.strip())
    return reactiveclass_blocks

def extract_main_block(inputFileName, rebeca_code):
    temp_main_block = re.findall(r'\s*main\s*\{(?:[^{}]|\{[^{}]*\})*\}', rebeca_code, re.DOTALL)
    main_block = temp_main_block[0].strip()
    main_block = main_block[main_block.find("{") + 1 : main_block.rfind("}")]
    main_block = main_block.strip()
    save_file(f'{inputFileName}_parts', "main.txt", main_block)
    return main_block

def extract_class_dict(reactiveclass_blocks, class_info, class_dict):
    for i, block in enumerate(reactiveclass_blocks):
        knownrebecs_match = re.search(r'knownrebecs\s*\{(.*?)\}', block, re.DOTALL)
        if knownrebecs_match:
            knownrebecs_raw = knownrebecs_match.group(1).strip()
            knownrebecs = {
                variable.split()[1].strip(";"): variable.split()[0]  # نام متغیر به عنوان کلید و نوع آن به عنوان مقدار
                for variable in knownrebecs_raw.splitlines() if variable.strip()
            }
        else:
            knownrebecs = {}

        statevars_match = re.search(r'statevars\s*\{(.*?)\}', block, re.DOTALL)
        if statevars_match:
            statevars_raw = statevars_match.group(1).strip()
            statevars = {
                variable.split()[1].strip(";"): variable.split()[0]  # نام متغیر به عنوان کلید و نوع آن به عنوان مقدار
                for variable in statevars_raw.splitlines() if variable.strip()
            }
        else:
            statevars = {}

        matches = re.finditer(r'msgsrv\s+(\w+)\s*\(\)\s*\{', block)
        results = []
        for match in matches:
            func_name = match.group(1)  # نام تابع
            start_index = match.end()  # شروع از بعد از {
            open_braces = 1
            end_index = start_index
            while open_braces > 0 and end_index < len(block):
                if block[end_index] == '{':
                    open_braces += 1
                elif block[end_index] == '}':
                    open_braces -= 1
                end_index += 1
            # ذخیره نتیجه
            full_body = block[match.start():end_index].strip()
            results.append((func_name, full_body))

        # for result in results: print(f"Function: {result[0]}\nBody:\n{result[1]}\n")
        msgsrvs = {name: body.strip() for name, body in results}
        class_dict[class_info[i]['name']] = {
            "knownrebecs": knownrebecs,
            "statevars": statevars,
            "msgsrvs": msgsrvs,
        }
    return class_dict



# extract real actors and build their dictionaries
def create_actor_dicts(main_block, class_dict):
    actors_dict = {}
    main_block = main_block.splitlines()
    for i, actor_str in enumerate(main_block):
        if actor_str.strip():
            pattern = r'(\w+)\s+(\w+)\s*\((.*?)\)\s*:?;?'
            match = re.match(pattern, actor_str.strip())
            if match:
                actor_type = match.group(1)  # نوع اکتور
                actor_name = match.group(2)  # نام اکتور
                actor_knownrebecs = match.group(3)  # پارامترها
                knownrebecs_list = actor_knownrebecs.split(",")
                knownrebecs_keys = class_dict[actor_type]['knownrebecs'].keys()
            else:
                print("No match found.")
            

            # Build the actor dictionary
            actor_dict_temp = {
                "statevars": class_dict[actor_type]["statevars"],
                "msgsrvs": class_dict[actor_type]["msgsrvs"]
            }
            actor_dict_temp['knownrebecs'] = dict(zip(knownrebecs_keys, knownrebecs_list))
            actors_dict[actor_name]= actor_dict_temp
    #generating flags
    for actor_name, actor_data in actors_dict.items():
        # لیست فلگ‌ها برای این اکتور
        flags = []
        
        # فلگ برای مسیج سرورهای خود اکتور
        for msgsrv_name in actor_data.get("msgsrvs", {}):
            flags.append(f"flag_{msgsrv_name}")
        
        # فلگ برای مسیج سرورهای اکتورهای همسایه
        for rebec_alias, rebec_name in actor_data.get("knownrebecs", {}).items():
            rebec_name = rebec_name.strip()  # حذف فاصله‌های اضافی
            if rebec_name in actors_dict:  # اگر اکتور همسایه در داده‌ها وجود دارد
                for msgsrv_name in actors_dict[rebec_name].get("msgsrvs", {}):
                    flags.append(f"flag_{msgsrv_name}_{rebec_name}")
        
        # افزودن لیست فلگ‌ها به اکتور
        actors_dict[actor_name]["flags"] = flags
    return actors_dict