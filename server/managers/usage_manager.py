from pathlib import Path
from server.managers.llm_model_manager import LLMModelManager
from server.managers.resource_manager import ResourceManager

class UsageManager:
    def __init__(self, file_path="usage.json", model_manager: LLMModelManager = None):
        self.file_path = Path(file_path)
        self.model_manager = model_manager or LLMModelManager()
        self.usage = {}

        if self.file_path.exists():
            self.load_from_file()
        else:
            self.usage = {model: 0 for model in self.model_manager.get_models()}
            self.export_to_file()

    def log_usage(self, model: str, tokens: int) -> bool:
        if model not in self.model_manager.get_models():
            raise ValueError(f"Model '{model}' not recognized in LLMModelManager")
        self.usage[model] = self.usage.get(model, 0) + tokens
        self.export_to_file()
        return True

    def get_usage(self, model: str) -> int:
        return self.usage.get(model, 0)

    def get_total_usage(self) -> int:
        return sum(self.usage.values())

    def reset(self):
        self.usage = {model: 0 for model in self.model_manager.get_models()}
        self.export_to_file()

    def export_to_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        ResourceManager.save_json(path, self.usage)
        return path

    def load_from_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        self.usage = ResourceManager.load_json(path)
        return self.usage
