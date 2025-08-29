from flask import Flask, request, jsonify
from database import db
from database.models import LLMModel, PromptRecord
from managers.client_manager import ClientManager
from managers.llm_model_manager import LLMModelManager
from managers.usage_manager import UsageManager

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Managers
with app.app_context():
    db.create_all()  # Create tables

model_manager = LLMModelManager()
usage_manager = UsageManager(model_manager=model_manager)
client_manager = ClientManager(model_manager=model_manager, usage_manager=usage_manager)

# ---------------------------
# API endpoints
# ---------------------------

@app.route("/prompt", methods=["POST"])
def send_prompt():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing 'prompt'"}), 400

    response = client_manager.get_completion(0, prompt)  # adjust index if needed
    return jsonify({"response": response})


@app.route("/model/load", methods=["POST"])
def load_model():
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing 'path'"}), 400

    count = model_manager.bulk_add_from_json(path)
    return jsonify({"message": f"Loaded {count} models from {path}"})


@app.route("/history", methods=["GET"])
def get_history():
    limit = request.args.get("limit", 50, type=int)
    model_name = request.args.get("model_name", type=str)

    query = PromptRecord.query
    if model_name:
        query = query.filter_by(model_name=model_name)

    records = query.order_by(PromptRecord.id.desc()).limit(limit).all()
    history = [
        {"id": r.id, "prompt": r.prompt_text, "response": r.completion_text,
         "model": r.model_name, "streamed": r.streamed}
        for r in records
    ]
    return jsonify(history)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
