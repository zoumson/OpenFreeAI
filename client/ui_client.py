# client/ui_client.py
import gradio as gr
import requests
import re
import json
from client.config import Config

SERVER_URL = Config.SERVER_URL
API_PREFIX = Config.API_PREFIX
TRUSTED_MODE = Config.TRUSTED_MODE
UI_PORT = Config.CLIENT_PORT

def api_url(path: str) -> str:
    return f"{SERVER_URL}{API_PREFIX}{path}"

def clean_llm_output(text: str) -> str:
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"_+", "", text)
    return text.strip()

# ---------------------------
# Model management functions
# ---------------------------
def get_model_list():
    try:
        resp = requests.get(api_url("/model/list"))
        resp.raise_for_status()
        return resp.json().get("models", [])
    except requests.RequestException:
        return []

def upload_model(file_obj):
    if not file_obj:
        return "No file selected."
    try:
        file_path = file_obj.name if hasattr(file_obj, "name") else file_obj
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        resp = requests.post(api_url("/model/upload"), json=data)
        resp.raise_for_status()
        return resp.json().get("message", "Upload successful!")
    except Exception as e:
        return f"Failed to upload model: {e}"

def clear_models():
    try:
        resp = requests.post(api_url("/model/clear"))
        resp.raise_for_status()
        return resp.json().get("message", "Models cleared successfully!")
    except Exception as e:
        return f"Failed to clear models: {e}"

# ---------------------------
# Chat functions
# ---------------------------
def submit_prompt_ui(prompt, selected_models):
    global previous_selected_models

    models_available = get_model_list()
    if not selected_models:
        # Use previous selection if available, else default to first model
        selected_models = previous_selected_models or ([models_available[0]] if models_available else [])

    # Normalize to list
    if isinstance(selected_models, str):
        selected_models = [selected_models]

    # Save current selection for next call
    previous_selected_models = selected_models

    if not prompt:
        return ["Waiting for question..."] * len(selected_models), ""

    payload = {"prompt": prompt, "models": selected_models, "stream": False}

    try:
        resp = requests.post(api_url("/job/prompt"), json=payload)
        resp.raise_for_status()
        data = resp.json()
        task_ids = data.get("task_ids", [])

        results = []
        for task_id, model in zip(task_ids, selected_models):
            while True:
                job_resp = requests.get(api_url(f"/job/{task_id}"))
                job_resp.raise_for_status()
                job_data = job_resp.json()
                status = job_data.get("status")
                if status == "SUCCESS":
                    text = clean_llm_output(job_data.get("result", ""))
                    results.append(f"### {model}\n{text}")
                    break
                elif status == "FAILURE":
                    results.append(f"### {model}\n(Error in processing)")
                    break

    except requests.RequestException as e:
        results = [f"Error contacting server: {e}"]

    return results, "\n\n".join(results)


# ---------------------------
# Optimized dropdown refresh
# ---------------------------
previous_models = []

def poll_models_optimized():
    global previous_models
    models = get_model_list()
    if models != previous_models:  # Only update if there's a change
        previous_models = models
        if not models:
            return gr.update(choices=[], value=[])
        return gr.update(choices=models, value=[models[0]])
    return None  # No update needed

# ---------------------------
# Build UI
# ---------------------------
def build_ui():
    chat_inputs = [
        gr.Textbox(label="Ask me"),
        gr.Dropdown(
            label="Select Model(s)",
            choices=get_model_list(),
            value=([get_model_list()[0]] if get_model_list() else []),
            multiselect=True,   # ✅ allow multiple selections
        ),
    ]

    chat_outputs = [
        gr.Textbox(label="Status", value="Waiting for question..."),
        gr.Textbox(label="My Response"),
    ]

    with gr.Blocks() as ui:
        gr.Markdown("## Chocolat Chat")

        chat_interface = gr.Interface(
            fn=submit_prompt_ui,
            inputs=chat_inputs,
            outputs=chat_outputs,
            live=False
        )

        # Poll dropdown every 10 seconds, only update if changed
        ui.load(poll_models_optimized, inputs=None, outputs=chat_inputs[1], every=10)

        if TRUSTED_MODE:
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Model Management (Admin)")
                    upload_file = gr.File(label="Upload JSON Model File", file_types=[".json"])
                    upload_btn = gr.Button("Upload Model")
                    upload_output = gr.Textbox(label="Upload Status")

                    clear_btn = gr.Button("Clear All Models")
                    clear_output = gr.Textbox(label="Clear Status")

                    # Admin actions trigger optimized refresh
                    upload_btn.click(upload_model, inputs=upload_file, outputs=upload_output)\
                              .then(poll_models_optimized, None, chat_inputs[1])
                    clear_btn.click(clear_models, inputs=None, outputs=clear_output)\
                              .then(poll_models_optimized, None, chat_inputs[1])

    return ui

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", server_port=UI_PORT, share=False)
