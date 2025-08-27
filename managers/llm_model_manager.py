import json
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Flask app and DB
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///llm_models.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class LLMModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_model = db.Column(db.String, unique=True, nullable=False)
    provider = db.Column(db.String, nullable=True)
    model_name = db.Column(db.String, nullable=True)
    tag = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<LLMModel {self.full_model}>"

class LLMModelManager:
    def __init__(self):
        with app.app_context():
            db.create_all()

    def add_model(self, full_model, provider=None, model_name=None, tag=None):
        if ":" in full_model and not tag:
            parts = full_model.split(":")
            full_model_name = parts[0]
            tag = parts[1]
        else:
            full_model_name = full_model

        if "/" in full_model_name and not model_name:
            provider, model_name = full_model_name.split("/", 1)

        # Check if already exists
        existing = LLMModel.query.filter_by(full_model=full_model).first()
        if existing:
            return False

        model = LLMModel(
            full_model=full_model,
            provider=provider,
            model_name=model_name,
            tag=tag,
        )
        db.session.add(model)
        db.session.commit()
        return True

    def bulk_add_from_json(self, file_path):
        path = Path(file_path)
        if not path.exists():
            return 0
        with open(path, "r") as f:
            models = json.load(f)
        count = 0
        for m in models:
            if self.add_model(m):
                count += 1
        return count

    def get_models(self):
        return [m.full_model for m in LLMModel.query.all()]

    def get_grouped_models(self):
        grouped = {}
        for m in LLMModel.query.all():
            prov = m.provider or "unknown"
            if prov not in grouped:
                grouped[prov] = []
            grouped[prov].append({"model_name": m.model_name, "tag": m.tag, "full_model": m.full_model})
        return grouped
