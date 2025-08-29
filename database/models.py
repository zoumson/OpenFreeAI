from datetime import datetime
from database import db

class LLMModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_model = db.Column(db.String, unique=True, nullable=False)
    provider = db.Column(db.String, nullable=True)
    model_name = db.Column(db.String, nullable=True)
    tag = db.Column(db.String, nullable=True)

class PromptRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    completion_text = db.Column(db.Text, nullable=True)
    model_name = db.Column(db.String, nullable=False)
    streamed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
