from flask import Blueprint, request, jsonify, current_app
from server.config import Config
from server.infrastructure.celery_app import celery_app
from celery.result import AsyncResult
from server.utils.jwt_decorator import jwt_required
api_v1 = Blueprint("api_v1", __name__)

# ---------------------------
# Job submission endpoints
# ---------------------------
# @api_v1.route("/job/prompt", methods=["POST"])
# def send_prompt():
#     from server.jobs.tasks import process_prompt  # local import to avoid circular import

#     data = request.get_json()
#     prompt = data.get("prompt")
#     model_index = data.get("model_index", 0)
#     stream = data.get("stream", False)

#     if not prompt:
#         return jsonify({"error": "Missing 'prompt'"}), 400

#     # Enqueue Celery task
#     task = process_prompt.apply_async(args=[prompt, model_index, stream])
#     return jsonify({"task_id": task.id, "status": "queued"})

@api_v1.route("/job/prompt", methods=["POST"])
def send_prompt():
    data = request.get_json()
    prompt = data.get("prompt")
    stream = data.get("stream", False)
    model_index = data.get("model_index", 0)
    model_name = data.get("model_name")
    models = data.get("models")  # NEW multi-model support

    if not prompt:
        return jsonify({"error": "Missing 'prompt'"}), 400

    all_models = current_app.client_manager.model_manager.get_models()

    # Determine which models to use
    if models:
        invalid = [m for m in models if m not in all_models]
        if invalid:
            return jsonify({"error": f"Models not found: {invalid}"}), 404
        selected_indexes = [all_models.index(m) for m in models]
    elif model_name:
        if model_name not in all_models:
            return jsonify({"error": f"Model '{model_name}' not found"}), 404
        selected_indexes = [all_models.index(model_name)]
    else:
        selected_indexes = [model_index]

    # Enqueue one task per model
    task_ids = []
    for idx in selected_indexes:
        task = process_prompt.apply_async(args=[prompt, idx, stream])
        task_ids.append(task.id)

    return jsonify({"task_ids": task_ids, "status": "queued"})


@api_v1.route("/job/conversation", methods=["POST"])
def conversation():
    from server.jobs.tasks import process_conversation

    data = request.get_json()
    message = data.get("prompt")  # keep backend key 'prompt' for consistency
    model_index = data.get("model_index", 0)

    if not message:
        return jsonify({"error": "Missing 'prompt'"}), 400

    # Enqueue the conversation task
    task = process_conversation.apply_async(args=[message, model_index])
    return jsonify({"task_id": task.id, "status": "queued"})


# ---------------------------
# Job status / result endpoint
# ---------------------------
@api_v1.route("/job/<task_id>", methods=["GET"])
def get_job(task_id):
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        response = {
            "id": task_result.id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
        }
        return jsonify(response)
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

@api_v1.route("/model/upload", methods=["POST"])
def upload_model():
    """Accept JSON models directly in the request body."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        count = current_app.client_manager.model_manager.bulk_add_from_dict(data)
        return jsonify({"message": f"Uploaded {count} models successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_v1.route("/model/upload", methods=["POST"])
@jwt_required(role="admin")
def upload_model_endpoint(user):
    from server.managers.llm_model_manager import LLMModelManager
    data = request.get_json()
    count = current_app.client_manager.model_manager.bulk_add_from_json_data(data)
    return jsonify({"message": f"Uploaded {count} models"})

@api_v1.route("/model/list", methods=["GET"])
def list_models():
    models = current_app.client_manager.model_manager.get_models()
    return jsonify({"models": models})


@api_v1.route("/model/grouped", methods=["GET"])
def grouped_models():
    grouped = current_app.client_manager.model_manager.get_grouped_models()
    return jsonify(grouped)

@api_v1.route("/model/clear", methods=["POST"])
def clear_models():
    try:
        count = len(current_app.client_manager.model_manager.get_models())
        current_app.client_manager.model_manager.clear_models()
        return jsonify({"message": f"Cleared {count} models"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v1.route("/model/clear", methods=["POST"])
@jwt_required(role="admin")
def clear_model_endpoint(user):
    current_app.client_manager.model_manager.clear_all()
    return jsonify({"message": "All models cleared!"})

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
