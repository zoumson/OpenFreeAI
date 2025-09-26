# client/ui_client.py
import gradio as gr
import requests
import re
import json
from client.config import Config
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

SERVER_URL = Config.SERVER_URL
API_PREFIX = Config.API_PREFIX
TRUSTED_MODE = Config.TRUSTED_MODE
UI_PORT = Config.CLIENT_PORT


# ---------------------------
# Globals
# ---------------------------
previous_models = []
previous_selected_models = []
SPINNER_FRAMES = ["⏳", "🔄", "⌛"]


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
def poll_job(task_id, model, idx, timeout=300):
    """Polls a single job until finished or timeout."""
    start = time.time()

    while True:
        if time.time() - start > timeout:
            return idx, f"{idx}. **{model}** ⏳ Timed out"

        try:
            job_resp = requests.get(api_url(f"/job/{task_id}"))
            job_resp.raise_for_status()
            job_data = job_resp.json()
            logging.debug(f"[{model}] Job data: {job_data}")

            status = job_data.get("status")
            result_text = job_data.get("result", "")

            if status == "FAILURE":
                return idx, f"{idx}. **{model}** ❌ Failure"

            elif status == "SUCCESS":
                cleaned_text = clean_llm_output(result_text)
                if not cleaned_text or "error" in cleaned_text.lower():
                    return idx, f"{idx}. **{model}** ❌ Invalid output"
                return idx, f"{idx}. **{model}** ✅\n\n{cleaned_text}"

            else:  # PENDING
                time.sleep(0.5)  # Let spinner update outside

        except Exception as e:
            logging.exception(f"Error polling job {task_id} for {model}")
            return idx, f"{idx}. **{model}** ❌ Error: {e}"


def submit_prompt_ui(prompt, selected_models):
    if not prompt: 
        yield "Waiting for question...", "" 
        return   
    models_available = get_model_list()
    if not models_available:
        yield "No models available. Please contact the administrator.", ""
        return    
    if not selected_models:
        yield "No model selected. Please choose at least one model.", ""
        return
    
    if isinstance(selected_models, str):
        selected_models = [selected_models]


    payload = {"prompt": prompt, "models": selected_models, "stream": False}

    try:
        resp = requests.post(api_url("/job/prompt"), json=payload)
        resp.raise_for_status()
        data = resp.json()
        task_ids = data.get("task_ids", [])

        results = [f"{idx}. **{model}** ⏳" for idx, model in enumerate(selected_models, start=1)]

        # Spinner state
        frame = 0
        yield f"Working {SPINNER_FRAMES[frame]}", "\n\n".join(results)

        with ThreadPoolExecutor(max_workers=len(task_ids)) as executor:
            futures = {
                executor.submit(poll_job, task_id, model, idx): (task_id, model, idx)
                for idx, (task_id, model) in enumerate(zip(task_ids, selected_models), start=1)
            }

            while futures:
                done, _ = wait(futures, timeout=0.5, return_when="FIRST_COMPLETED")
                frame = (frame + 1) % len(SPINNER_FRAMES)

                # Update spinner in status
                finished = sum(1 for r in results if not any(s in r for s in SPINNER_FRAMES))
                status_msg = f"{finished}/{len(task_ids)} models finished {SPINNER_FRAMES[frame]}"
                yield status_msg, "\n\n".join(results)

                for future in list(done):
                    try:
                        idx, result = future.result()
                        results[idx - 1] = result
                    except Exception as e:
                        task_id, model, idx = futures[future]
                        results[idx - 1] = f"{idx}. **{model}** ❌ Error: {e}"
                    del futures[future]

            # Final update
            yield "Done ✅", "\n\n".join(results)

    except requests.RequestException as e:
        logging.exception("Error contacting server")
        yield f"Error contacting server: {e}", ""


# ---------------------------
# Optimized dropdown refresh
# ---------------------------
def poll_models_optimized():
    global previous_models
    models = get_model_list()
    if models != previous_models:  # Only update if there's a change
        previous_models = models
        if not models:
            return gr.update(choices=[], value=[])
        # return gr.update(choices=models, value=[models[0]])
        # remove default model upon update 
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
            # Keep default model upon start up
            value=([get_model_list()[0]] if get_model_list() else []),
            multiselect=True,   # ✅ allow multiple selections
        ),
    ]

    chat_outputs = [
        gr.Textbox(label="Status", value="Waiting for question..."),
        gr.Markdown(label="My Response"),  # ✅ Markdown for clean output
    ]

    with gr.Blocks() as ui:
        gr.Markdown("## Chocolat Chat")

        gr.Interface(
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
