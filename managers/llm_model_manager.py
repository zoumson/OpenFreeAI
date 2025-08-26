from enum import Enum
from pathlib import Path
from managers.resource_manager import ResourceManager

class LLMModelsEnum(str, Enum):
    OPENAI_GPT_OSS = "openai/gpt-oss-20b:free"
    Z_AI_GLM = "z-ai/glm-4.5-air:free"
    QWEN_CODER = "qwen/qwen3-coder:free"
    MOONSHOT_AI_KIMI = "moonshotai/kimi-k2:free"
    VENICE_UNCENSORED = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
    GOOGLE_GEMMA = "google/gemma-3n-e2b-it:free"


class LLMModelManager:
    def __init__(self, file_path="models.json"):
        self.file_path = Path(file_path)
        self.models = []
        if self.file_path.exists():
            self.load_from_file()
        else:
            self.models = [model.value for model in LLMModelsEnum]
            self.export_to_file()

    def add_model(self, model_name: str) -> bool:
        if model_name not in self.models:
            self.models.append(model_name)
            self.export_to_file()
            return True
        return False

    def remove_model(self, model_name: str) -> bool:
        if model_name in self.models:
            self.models.remove(model_name)
            self.export_to_file()
            return True
        return False

    def get_models(self):
        return self.models

    def export_to_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        ResourceManager.save_json(path, self.models)
        return path

    def load_from_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        self.models = ResourceManager.load_json(path)
        return self.models
