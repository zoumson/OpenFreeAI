from pathlib import Path
from managers.resource_manager import ResourceManager
from collections import defaultdict

class LLMModelManager:
    def __init__(self, file_path="models.json"):
        self.file_path = Path(file_path)
        self.models = {}  # {provider: [{"model":..., "tag":...}]}
        if self.file_path.exists():
            self.load_from_file()
        else:
            self._initialize_default_models()
            self.export_to_file()

    def _initialize_default_models(self):
        # Example defaults
        self.models = {
            "openai": [{"model": "gpt-oss-20b", "tag": "free"}],
            "google": [{"model": "gemini-2.5-flash-image-preview", "tag": "free"}],
        }

    @staticmethod
    def parse_full_model(full_model: str):
        """Parse a full model string like 'openai/gpt-oss-20b:free'"""
        if ":" in full_model:
            model_id, tag = full_model.split(":", 1)
        else:
            model_id, tag = full_model, "free"

        if "/" in model_id:
            provider, model_name = model_id.split("/", 1)
        else:
            provider, model_name = "unknown", model_id

        return provider, model_name, tag

    def add_model(self, full_model: str = None, provider: str = None, model_name: str = None, tag: str = "free") -> bool:
        """Add a model using full string or separate fields."""
        if full_model:
            provider, model_name, tag = self.parse_full_model(full_model)

        if provider not in self.models:
            self.models[provider] = []

        # Avoid duplicates
        for m in self.models[provider]:
            if m["model"] == model_name and m["tag"] == tag:
                return False

        self.models[provider].append({"model": model_name, "tag": tag})
        self.export_to_file()
        return True

    def remove_model(self, provider: str, model_name: str, tag: str = "free") -> bool:
        if provider not in self.models:
            return False
        for m in self.models[provider]:
            if m["model"] == model_name and m["tag"] == tag:
                self.models[provider].remove(m)
                self.export_to_file()
                return True
        return False

    def get_models(self):
        """Flattened list for CLI/API: ['provider/model:tag']"""
        full_list = []
        for provider, models in self.models.items():
            for m in models:
                full_list.append(f"{provider}/{m['model']}:{m['tag']}")
        return full_list

    def get_models_grouped_by_provider(self):
        """Return grouped dict for CLI display."""
        return self.models

    def get_models_grouped_by_tag(self):
        """Return dict {tag: [models]}"""
        grouped = defaultdict(list)
        for provider, models in self.models.items():
            for m in models:
                grouped[m["tag"]].append({"provider": provider, "model": m["model"]})
        return dict(grouped)

    def export_to_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        ResourceManager.save_json(path, self.models)
        return path

    def load_from_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        self.models = ResourceManager.load_json(path)
        return self.models
