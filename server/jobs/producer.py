from flask import Blueprint, request, jsonify
from redis import Redis
from rq import Queue
from server.jobs.tasks import process_prompt
from server.database.models import LLMModel, PromptRecord
from server.managers.llm_model_manager import LLMModelManager
from server.config import Config

# Redis connection
redis_conn = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
q = Queue(Config.QUEUE_NAME, connection=redis_conn)

model_manager = LLMModelManager()

# Blueprint
api_v1 = Blueprint("api_v1", __name__)

# ---------------------------
# Prompt endpoint (Producer)
# ---------------------------
@api_v1.route("/prompt", methods=["POST"])
def send_prompt():
    data = request.get_json()
    prompt = data.get("prompt")
    model_index = data.get("model_index", 0)

    if not prompt:
        return jsonify({"error": "Missing 'prompt'"}), 400

    # Enqueue task
    job = q.enqueue(process_prompt, prompt, model_index)
    return jsonify({"job_id": job.get_id(), "status": "queued"})

# ---------------------------
# Model endpoints
# ---------------------------
@api_v1.route("/model/load", methods=["POST"])
def load_model():
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing 'path'"}), 400
    count = model_manager.bulk_add_from_json(path)
    return jsonify({"message": f"Loaded {count} models from {path}"})

@api_v1.route("/model/list", methods=["GET"])
def list_models():
    models = [m.full_model for m in LLMModel.query.all()]
    return jsonify({"models": models})

@api_v1.route("/model/grouped", methods=["GET"])
def grouped_models():
    grouped = {}
    for m in LLMModel.query.all():
        provider = m.provider or "unknown"
        grouped.setdefault(provider, []).append({
            "model_name": m.model_name,
            "tag": m.tag
        })
    return jsonify(grouped)

@api_v1.route("/history", methods=["GET"])
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

@api_v1.route("/version", methods=["GET"])
def get_version():
    return jsonify({"version": Config.APP_VERSION})
