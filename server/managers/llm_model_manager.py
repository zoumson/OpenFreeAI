import json
import os
import logging
from server.database import db
from server.database.models import LLMModel
from server.config import Config

logger = logging.getLogger(__name__)


class LLMModelManager:
    def __init__(self):
        # Tables are created once in app.py with db.create_all()
        self.shared_dir = Config.SHARED_DIR
        self.json_file = os.path.join(self.shared_dir, "models.json")

    def add_model(self, full_model=None, provider=None, model_name=None, tag=None):
        """
        Add a model to the DB if not already present. Also updates the JSON file.
        """
        if not full_model:
            full_model = f"{provider}/{model_name}:{tag}"

        existing = LLMModel.query.filter_by(full_model=full_model).first()
        if existing:
            return False

        provider_val = provider or full_model.split("/")[0]
        model_val = model_name or full_model.split("/")[1].split(":")[0]
        tag_val = tag or (full_model.split(":")[1] if ":" in full_model else "")

        new_model = LLMModel(
            full_model=full_model,
            provider=provider_val,
            model_name=model_val,
            tag=tag_val
        )
        db.session.add(new_model)
        db.session.commit()
        self._save_to_json()
        return True

    def bulk_add_from_json(self, json_file=None):
        """
        Load models from the JSON file and insert them into the DB.
        Supports both old {"model": ...} and new {"model_name": ...} formats.
        """
        json_file = json_file or self.json_file
        if not os.path.exists(json_file):
            logger.info(f"No models.json found at {json_file}")
            return 0

        with open(json_file, "r") as f:
            data = json.load(f)

        count = 0
        for provider, models in data.items():
            for m in models:
                # accept both "model" and "model_name" keys
                model_name = m.get("model") or m.get("model_name")
                tag = m.get("tag", "")

                if not model_name:
                    logger.warning(f"Skipping invalid model entry: {m}")
                    continue

                if self.add_model(provider=provider, model_name=model_name, tag=tag):
                    count += 1
        return count

    def get_models(self):
        """Return all models as a flat list of full_model strings."""
        return [m.full_model for m in LLMModel.query.all()]

    def get_grouped_models(self):
        """
        Return grouped dict of models by provider, e.g.:
        {
          "openai": [
            {"model_name": "gpt-4", "tag": "latest"}
          ]
        }
        """
        grouped = {}
        for m in LLMModel.query.all():
            grouped.setdefault(m.provider, []).append({
                "model_name": m.model_name,
                "tag": m.tag
            })
        return grouped

    def _save_to_json(self):
        """Save all models to the shared JSON file for persistence."""
        grouped = self.get_grouped_models()
        os.makedirs(self.shared_dir, exist_ok=True)
        with open(self.json_file, "w") as f:
            json.dump(grouped, f, indent=2)
        logger.info(f"Saved models to {self.json_file}")
import json
import os
import logging
from server.database import db
from server.database.models import LLMModel
from server.config import Config

logger = logging.getLogger(__name__)


class LLMModelManager:
    def __init__(self):
        # Tables are created once in app.py with db.create_all()
        self.shared_dir = Config.SHARED_DIR
        self.json_file = os.path.join(self.shared_dir, "models.json")

    def add_model(self, full_model=None, provider=None, model_name=None, tag=None):
        """
        Add a model to the DB if not already present. Also updates the JSON file.
        """
        if not full_model:
            full_model = f"{provider}/{model_name}:{tag}"

        existing = LLMModel.query.filter_by(full_model=full_model).first()
        if existing:
            return False

        provider_val = provider or full_model.split("/")[0]
        model_val = model_name or full_model.split("/")[1].split(":")[0]
        tag_val = tag or (full_model.split(":")[1] if ":" in full_model else "")

        new_model = LLMModel(
            full_model=full_model,
            provider=provider_val,
            model_name=model_val,
            tag=tag_val
        )
        db.session.add(new_model)
        db.session.commit()
        self._save_to_json()
        return True

    def bulk_add_from_json(self, json_file=None):
        """
        Load models from the JSON file and insert them into the DB.
        Supports both old {"model": ...} and new {"model_name": ...} formats.
        """
        json_file = json_file or self.json_file
        if not os.path.exists(json_file):
            logger.info(f"No models.json found at {json_file}")
            return 0

        with open(json_file, "r") as f:
            data = json.load(f)

        count = 0
        for provider, models in data.items():
            for m in models:
                # accept both "model" and "model_name" keys
                model_name = m.get("model") or m.get("model_name")
                tag = m.get("tag", "")

                if not model_name:
                    logger.warning(f"Skipping invalid model entry: {m}")
                    continue

                if self.add_model(provider=provider, model_name=model_name, tag=tag):
                    count += 1
        return count

    def get_models(self):
        """Return all models as a flat list of full_model strings."""
        return [m.full_model for m in LLMModel.query.all()]

    def get_grouped_models(self):
        """
        Return grouped dict of models by provider, e.g.:
        {
          "openai": [
            {"model_name": "gpt-4", "tag": "latest"}
          ]
        }
        """
        grouped = {}
        for m in LLMModel.query.all():
            grouped.setdefault(m.provider, []).append({
                "model_name": m.model_name,
                "tag": m.tag
            })
        return grouped

    def _save_to_json(self):
        """Save all models to the shared JSON file for persistence."""
        grouped = self.get_grouped_models()
        os.makedirs(self.shared_dir, exist_ok=True)
        with open(self.json_file, "w") as f:
            json.dump(grouped, f, indent=2)
        logger.info(f"Saved models to {self.json_file}")
