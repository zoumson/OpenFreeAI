# client/ui_client.py
import gradio as gr
import requests
import re
import json
from client.config import SERVER_URL, API_PREFIX

# ---------------------------
# Configuration
# ---------------------------
TRUSTED_MODE = True  # Admin features toggle
token = None  # For admin authentication (JWT or Bearer token)

# ---------------------------
# Utility functions
# ---------------------------
def api_url(path: str) -> str:
    return f"{SERVER_URL}{API_PREFIX}{path}"

def clean_llm_output(text: str) -> str:
    """Remove markdown artifacts like *, **, etc."""
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"_+", "", text)
    return text.strip()

def get_model_list():
    """Fetch available models from server."""
    try:
        resp = requests.get(api_url("/model/list"))
        resp.raise_for_status()
        return resp.json().get("models", [])
    except requests.RequestException:
        return []

# ---------------------------
# Admin functions
# ---------------------------
def upload_model(file_obj):
    """Upload JSON model file to server."""
    if not token:
        return "Login required", get_model_list(), gr.update(interactive=False)
    if not file_obj:
        return "No file selected.", get_model_list(), gr.update(interactive=False)
    try:
        with open(file_obj.name, "r", encoding="utf-8") as f:
            data = json.load(f)
        resp = requests.post(
            api_url("/model/upload"),
            json=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        resp.raise_for_status()
        message = resp.json().get("message", "Upload successful!")
        models = get_model_list()
        return message, models, gr.update(interactive=bool(models))
    except Exception as e:
        models = get_model_list()
        return f"Failed to upload model: {e}", models, gr.update(interactive=bool(models))

def clear_models():
    """Clear all models on server."""
    if not token:
        return "Login required", get_model_list(), gr.update(interactive=False)
    try:
        resp = requests.post(
            api_url("/model/clear"),
            headers={"Authorization": f"Bearer {token}"}
        )
        resp.raise_for_status()
        message = resp.json().get("message", "Models cleared!")
        models = get_model_list()
        return message, models, gr.update(interactive=bool(models))
    except Exception as e:
        models = get_model_list()
        return f"Failed to clear models: {e}", models, gr.update(interactive=bool(models))

# ---------------------------
# Chat functions
# ---------------------------
def submit_prompt_ui(prompt, model_full_name):
    """Send the prompt to the /job/prompt endpoint and return status + result."""
    if not prompt:
        return "Waiting for question...", ""
    if not model_full_name:
        return "No model selected!", ""

    payload = {
        "prompt": prompt,
        "model_index": 0,
        "model_name": model_full_name,
        "stream": False
    }
    try:
        status = "Working on it..."
        result = ""

        resp = requests.post(api_url("/job/prompt"), json=payload)
        resp.raise_for_status()
        task_id = resp.json().get("task_id")

        # Poll for the result
        while True:
            job_resp = requests.get(api_url(f"/job/{task_id}"))
            job_resp.raise_for_status()
            job_data = job_resp.json()
            if job_data.get("status") == "SUCCESS":
                result = clean_llm_output(job_data.get("result", ""))
                status = "Done"
                break
            elif job_data.get("status") == "FAILURE":
                status = "Failed"
                result = "(Error in processing)"
                break
    except requests.RequestException as e:
        return f"Error contacting server: {e}", ""

    return status, result or "(No output)"

# ---------------------------
# Build UI
# ---------------------------
available_models = get_model_list()
chat_dropdown = gr.Dropdown(
    label="Select Model",
    choices=available_models,
    value=available_models[0] if available_models else None,
    interactive=bool(available_models)
)
chat_inputs = [
    gr.Textbox(label="Ask me"),
    chat_dropdown
]
chat_outputs = [
    gr.Textbox(label="Status", value="Waiting for question..."),
    gr.Textbox(label="My Response"),
]

if TRUSTED_MODE:
    with gr.Blocks() as ui:
        gr.Markdown("## Chocolat Chat")
        with gr.Row():
            with gr.Column(scale=3):
                # Chat section
                chat_interface = gr.Interface(
                    fn=submit_prompt_ui,
                    inputs=chat_inputs,
                    outputs=chat_outputs,
                    live=False
                )
            with gr.Column(scale=1):
                # Admin section
                gr.Markdown("### Model Management (Admin)")
                upload_file = gr.File(label="Upload JSON Model File", file_types=[".json"])
                upload_btn = gr.Button("Upload Model")
                upload_output = gr.Textbox(label="Upload Status")

                clear_btn = gr.Button("Clear All Models")
                clear_output = gr.Textbox(label="Clear Status")

                # Bind actions
                upload_btn.click(upload_model, inputs=upload_file, outputs=[upload_output, chat_dropdown, chat_dropdown])
                clear_btn.click(clear_models, inputs=None, outputs=[clear_output, chat_dropdown, chat_dropdown])
else:
    # Simple interface without admin section
    chat_interface = gr.Interface(
        fn=submit_prompt_ui,
        inputs=chat_inputs,
        outputs=chat_outputs,
        title="Chocolat Chat",
        description="Chat with your model via /job/prompt endpoint"
    )
    ui = chat_interface

if __name__ == "__main__":
    ui.launch(share=True)
