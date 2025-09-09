from datetime import datetime
from server.database import db 

class LLMModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_model = db.Column(db.String(255), unique=True, nullable=False)
    provider = db.Column(db.String(100), nullable=True)
    model_name = db.Column(db.String(100), nullable=True)
    tag = db.Column(db.String(50), nullable=True)

class PromptRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    completion_text = db.Column(db.Text, nullable=True)
    model_name = db.Column(db.String(100), nullable=False)  # <-- add length
    streamed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
