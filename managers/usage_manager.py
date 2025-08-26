import json
from pathlib import Path
from managers.llm_model_manager import LLMModelManager


class UsageManager:
    def __init__(self, file_path="usage.json", model_manager: LLMModelManager = None):
        self.file_path = Path(file_path)
        self.model_manager = model_manager or LLMModelManager()
        self.usage = {}

        if self.file_path.exists():
            self.load_from_file()
        else:
            # Initialize usage with 0 for all models
            self.usage = {model: 0 for model in self.model_manager.get_models()}
            self.export_to_file()

    def log_usage(self, model: str, tokens: int) -> bool:
        """Logs token usage for a given model if it's valid."""
        if model not in self.model_manager.get_models():
            raise ValueError(f"Model '{model}' not recognized in LLMModelManager")

        self.usage[model] = self.usage.get(model, 0) + tokens
        self.export_to_file()
        return True

    def get_usage(self, model: str) -> int:
        """Returns token usage for a given model (0 if none)."""
        return self.usage.get(model, 0)

    def get_total_usage(self) -> int:
        """Returns total tokens used across all models."""
        return sum(self.usage.values())

    def reset(self):
        """Resets usage for all models to 0."""
        self.usage = {model: 0 for model in self.model_manager.get_models()}
        self.export_to_file()

    def export_to_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        with open(path, "w") as f:
            json.dump(self.usage, f, indent=4)
        return path

    def load_from_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        with open(path, "r") as f:
            self.usage = json.load(f)
        return self.usage
