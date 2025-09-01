# server/jobs/producer.py
from flask import Blueprint, request, jsonify, current_app
from redis import Redis
from rq import Queue
from rq.job import Job
from server.config import Config
from server.jobs.tasks import process_prompt

# Redis connection & queue
redis_conn = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
q = Queue(Config.QUEUE_NAME, connection=redis_conn)

api_v1 = Blueprint("api_v1", __name__)

# ---------------------------
# Prompt endpoint (Producer)
# ---------------------------
@api_v1.route("/prompt", methods=["POST"])
def send_prompt():
    data = request.get_json()
    prompt = data.get("prompt")
    model_index = data.get("model_index", 0)
    stream = data.get("stream", False)

    if not prompt:
        return jsonify({"error": "Missing 'prompt'"}), 400

    # Enqueue task
    job = q.enqueue(process_prompt, prompt, model_index, stream)
    return jsonify({"job_id": job.get_id(), "status": "queued"})


# ---------------------------
# Job status endpoint
# ---------------------------
@api_v1.route("/job/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return jsonify({
            "id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# ---------------------------
# Model endpoints
# ---------------------------
@api_v1.route("/model/load", methods=["POST"])
def load_model():
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing 'path'"}), 400

    count = current_app.client_manager.model_manager.bulk_add_from_json(path)
    return jsonify({"message": f"Loaded {count} models from {path}"})


@api_v1.route("/model/list", methods=["GET"])
def list_models():
    models = current_app.client_manager.model_manager.get_models()
    return jsonify({"models": models})


@api_v1.route("/model/grouped", methods=["GET"])
def grouped_models():
    grouped = current_app.client_manager.model_manager.get_grouped_models()
    return jsonify(grouped)


# ---------------------------
# History endpoint
# ---------------------------
@api_v1.route("/history", methods=["GET"])
def get_history():
    from server.database.models import PromptRecord

    limit = request.args.get("limit", 50, type=int)
    model_name = request.args.get("model_name", type=str)

    query = PromptRecord.query
    if model_name:
        query = query.filter_by(model_name=model_name)

    records = query.order_by(PromptRecord.id.desc()).limit(limit).all()
    history = [
        {
            "id": r.id,
            "prompt": r.prompt_text,
            "response": r.completion_text,
            "model": r.model_name,
            "streamed": r.streamed
        }
        for r in records
    ]
    return jsonify(history)


# ---------------------------
# Version endpoint
# ---------------------------
@api_v1.route("/version", methods=["GET"])
def get_version():
    return jsonify({"version": Config.APP_VERSION})
