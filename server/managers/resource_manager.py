import json
from pathlib import Path

class ResourceManager:
    @staticmethod
    def save_json(file_path, data):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_json(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
