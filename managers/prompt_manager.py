from pathlib import Path
from managers.resource_manager import ResourceManager

class PromptManager:
    def __init__(self, file_path=None):
        self.prompts = {}
        self.file_path = Path(file_path) if file_path else None
        if self.file_path and self.file_path.exists():
            self.load_from_file(self.file_path)

    def add_prompt(self, name: str, template: str):
        self.prompts[name] = template

    def get_prompt(self, name: str, **kwargs) -> str:
        template = self.prompts.get(name, "")
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing key for prompt formatting: {e}")

    def export_to_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        if not path:
            raise ValueError("No file path provided for export")
        ResourceManager.save_json(path, self.prompts)
        return path

    def load_from_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        if not path or not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        self.prompts = ResourceManager.load_json(path)
        return self.prompts
