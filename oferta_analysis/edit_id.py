

import pandas as pd
import json
import os
    
# List of scrapped offerts
json_offerts = []

if __name__ == '__main__':
    filename = input("Please, introduce the relative path of the json you want to update the indexes:")
    remove_indx = int(input("Now, tell me the index absolute value to remove:"))

    with open(f"./{filename}", "r") as my_json:
        data = json.load(my_json)

    for offert in data:
        offert["id"] -= remove_indx
        json_offerts.append(offert)

    # JSON Writing after each iteration  
    with open(f"./{filename}_modified.json", 'w',  encoding='utf8') as fout:
        json.dump(json_offerts , fout, ensure_ascii = False)