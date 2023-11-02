from pathlib import Path
import json
import os

def read_storage_options(
    path_to_storage_options: str = f"{Path.home()}/shared/lincc-frameworks/data/ADASS_Tutorial/credentials.json"
):
    if os.path.exists(path_to_storage_options): 
        with open(path_to_storage_options) as _file:
            storage_options = json.load(_file)
        return storage_options
    else:
        raise FileNotFoundError(f"Cannot find: {path_to_storage_options}")