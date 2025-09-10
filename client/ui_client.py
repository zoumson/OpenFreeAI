# client/ui_client.py
import gradio as gr
import requests
import re
import json
from client.config import SERVER_URL, API_PREFIX

# Toggle for showing upload/clear features
TRUSTED_MODE = True  # set False if running in public mode

def api_url(path: str) -> str:
    return f"{SERVER_URL}{API_PREFIX}{path}"

def clean_llm_output(text: str) -> str:
    """Remove markdown artifacts like *, **, etc."""
    text = re.sub(r"\*+", "", text)  # remove * and ** emphasis
    text = re.sub(r"_+", "", text)   # remove _ and __ emphasis
    return text.strip()

# ---------------------------
# Model management functions
# ---------------------------
def get_model_list():
    """Fetch available models from server."""
    try:
        resp = requests.get(api_url("/model/list"))
        resp.raise_for_status()
        return resp.json().get("models", [])
    except requests.RequestException:
        return []

def upload_model(file_obj):
    """Upload JSON model file to server."""
    if not file_obj:
        return "No file selected."
    try:
        # file_obj is a dict with 'name' attribute
        file_path = file_obj.name if hasattr(file_obj, "name") else file_obj
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # validate JSON
        resp = requests.post(api_url("/model/upload"), json=data)
        resp.raise_for_status()
        return resp.json().get("message", "Upload successful!")
    except Exception as e:
        return f"Failed to upload model: {e}"


def clear_models():
    """Clear all models on server."""
    try:
        resp = requests.post(api_url("/model/clear"))
        resp.raise_for_status()
        return resp.json().get("message", "Models cleared successfully!")
    except Exception as e:
        return f"Failed to clear models: {e}"

# ---------------------------
# Chat functions
# ---------------------------
def submit_prompt_ui(prompt, model_full_name):
    """Send the prompt to the /job/prompt endpoint and return status + result."""
    if not prompt:
        return "Waiting for question...", ""

    if not model_full_name:
        return "No model selected!", ""

    payload = {"prompt": prompt, "model_index": 0, "model_name": model_full_name, "stream": False}
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
def refresh_model_dropdown():
    models = get_model_list()
    if not models:
        return gr.update(choices=[], value=None)
    return gr.update(choices=models, value=models[0])

chat_inputs = [
    gr.Textbox(label="Ask me"),
    gr.Dropdown(label="Select Model", choices=get_model_list(), value=(get_model_list()[0] if get_model_list() else None))
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
                upload_btn.click(
                    upload_model, 
                    inputs=upload_file, 
                    outputs=upload_output
                ).then(refresh_model_dropdown, None, chat_inputs[1])
                
                clear_btn.click(
                    clear_models, 
                    inputs=None, 
                    outputs=clear_output
                ).then(refresh_model_dropdown, None, chat_inputs[1])
else:
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
