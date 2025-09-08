# client/ui_client.py
import gradio as gr
import requests
import re
from client.config import SERVER_URL, API_PREFIX

def api_url(path: str) -> str:
    return f"{SERVER_URL}{API_PREFIX}{path}"

def clean_llm_output(text: str) -> str:
    """Remove markdown artifacts like *, **, etc."""
    text = re.sub(r"\*+", "", text)  # remove * and ** emphasis
    text = re.sub(r"_+", "", text)   # remove _ and __ emphasis
    return text.strip()

def submit_prompt_ui(prompt, model_index=None):
    """Send the prompt to the /job/prompt endpoint and return status + result."""
    if not prompt:
        return "Waiting for question...", ""

    if model_index is None or model_index == "":
        model_index = 5  # default fallback
    
    payload = {"prompt": prompt, "model_index": int(model_index), "stream": False}
    try:
        # Show working status immediately
        status = "Working on it..."
        result = ""
        
        resp = requests.post(api_url("/job/prompt"), json=payload)
        resp.raise_for_status()
        task_id = resp.json().get("task_id")
        
        # Poll for the result (blocking for simplicity)
        while True:
            job_resp = requests.get(api_url(f"/job/{task_id}"))
            job_resp.raise_for_status()
            job_data = job_resp.json()
            if job_data.get("status") == "SUCCESS":
                result = clean_llm_output(job_data.get("result", ""))
                status = "Done"
                break
    except requests.RequestException as e:
        return f"Error contacting server: {e}", ""

    return status, result or "(No output)"

# Build Gradio interface
web_chat = gr.Interface(
    fn=submit_prompt_ui,
    inputs=[
        gr.Textbox(label="Ask me"),
        gr.Number(label="Model Index (default = 5)", value=5, precision=0)
    ],
    outputs=[
        gr.Textbox(label="Status", value="Waiting for question..."),
        gr.Textbox(label="My Response"),
    ],
    title="Chocolat Chat",
    description="Chat with your model via /job/prompt endpoint"
)

if __name__ == "__main__":
    web_chat.launch(share=True)
