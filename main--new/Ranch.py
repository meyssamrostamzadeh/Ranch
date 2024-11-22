import re
import pprint
from file_utils import *
from extract import *

# inputFileName = 'S1-test'
inputFileName = 'S2-Dining'
########################################################################
########################################################################
# extract main block and reactiveclasses  #
with open(f'{inputFileName}.rebeca', 'r') as file:
    rebeca_code = file.read()
class_info = extract_class_info(rebeca_code)
# print(class_info)
reactiveclass_blocks = extract_reactiveclass_blocks(inputFileName, rebeca_code, class_info)
# for block in reactiveclass_blocks:     print(block.strip())
main_block = extract_main_block(inputFileName, rebeca_code)
# print(main_block)
########################################################################
########################################################################
class_dict = {}
class_dict = extract_class_dict(reactiveclass_blocks, class_info, class_dict)
# pprint.pprint(class_dict)
save_dict(f'{inputFileName}_parts', f'{inputFileName}_class_dict.json', class_dict)
########################################################################
########################################################################
actors_dict = create_actor_dicts(main_block, class_dict)
save_dict(f'{inputFileName}_parts', f'{inputFileName}_actors_dict.json', actors_dict)
########################################################################
########################################################################

save_dict(f'{inputFileName}_parts', f'{inputFileName}_actors_dict.json', actors_dict)
