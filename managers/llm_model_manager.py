import json
from database.models import LLMModel
from database import db
from app import app

class LLMModelManager:
    def __init__(self):
        with app.app_context():
            db.create_all()

    def add_model(self, full_model=None, provider=None, model_name=None, tag=None):
        with app.app_context():
            if not full_model:
                full_model = f"{provider}/{model_name}:{tag}"
            existing = LLMModel.query.filter_by(full_model=full_model).first()
            if existing:
                return False
            provider_val = provider or full_model.split("/")[0]
            model_val = model_name or full_model.split("/")[1].split(":")[0]
            tag_val = tag or full_model.split(":")[1] if ":" in full_model else ""
            new_model = LLMModel(
                full_model=full_model,
                provider=provider_val,
                model_name=model_val,
                tag=tag_val
            )
            db.session.add(new_model)
            db.session.commit()
            return True

    def bulk_add_from_json(self, json_file):
        with open(json_file, "r") as f:
            data = json.load(f)
        count = 0
        for provider, models in data.items():
            for m in models:
                if self.add_model(provider=provider, model_name=m["model"], tag=m.get("tag", "")):
                    count += 1
        return count

    def get_models(self):
        with app.app_context():
            return [m.full_model for m in LLMModel.query.all()]

    def get_grouped_models(self):
        with app.app_context():
            grouped = {}
            for m in LLMModel.query.all():
                grouped.setdefault(m.provider, []).append({"model_name": m.model_name, "tag": m.tag})
            return grouped
