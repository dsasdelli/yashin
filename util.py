from pathlib import Path
import json

def adjust_filename(filename):
    return filename.replace('/', '_')
    
def file_exists(dir, filename):
    return (Path(dir) / adjust_filename(filename)).is_file()
    
def dump_json(dir, filename, data):
    with open((Path(dir) / adjust_filename(filename)), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_dir(dir_name):
    output_dir = Path(dir_name)
    output_dir.mkdir(parents=True, exist_ok=True)