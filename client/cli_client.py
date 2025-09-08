import requests
import click
from client.config import SERVER_URL, API_PREFIX


def api_url(path: str) -> str:
    """Build the full API URL."""
    return f"{SERVER_URL}{API_PREFIX}{path}"


def submit_job(endpoint: str, payload: dict):
    """Helper to submit a job to the server and print task ID."""
    try:
        resp = requests.post(api_url(endpoint), json=payload)
        resp.raise_for_status()
        data = resp.json()
        click.echo(f"[INFO]: Job submitted. Task ID: {data.get('task_id')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to submit job → {e}")


@click.group()
def cli():
    """CLI client for interacting with the LLM Flask server."""
    pass


# ---------------------------
# Job commands
# ---------------------------
@cli.group(help="Manage jobs.")
def job():
    pass


@job.command("prompt", help="Submit a text prompt as a job.")
@click.option("--prompt", required=True, help="The input text prompt to send to the LLM.")
@click.option("--model-index", default=5, help="Index of the model to use.")
@click.option("--stream", is_flag=True, default=False, help="Enable streaming output.")
def submit_prompt(prompt, model_index, stream):
    payload = {"prompt": prompt, "model_index": model_index, "stream": stream}
    submit_job("/job/prompt", payload)


@job.command("conversation", help="Submit a conversation prompt as a job.")
@click.option("--message", required=True, help="The input message for the conversation.")
@click.option("--model-index", default=0, help="Index of the model to use.")
def submit_conversation(message, model_index):
    payload = {"prompt": message, "model_index": model_index}
    submit_job("/job/conversation", payload)


@job.command("status", help="Check the status of a job.")
@click.argument("task_id")
def status(task_id):
    try:
        resp = requests.get(api_url(f"/job/{task_id}"))
        resp.raise_for_status()
        data = resp.json()
        click.echo(f"[INFO]: Job {task_id} → Status: {data.get('status')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to fetch job status → {e}")


@job.command("result", help="Fetch the result of a job.")
@click.argument("task_id")
def result(task_id):
    try:
        resp = requests.get(api_url(f"/job/{task_id}"))
        resp.raise_for_status()
        data = resp.json()
        result = data.get("result")
        if result:
            click.echo(f"[RESULT]: {result}")
        else:
            click.echo(f"[INFO]: Job not finished yet. Status: {data.get('status')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to fetch job result → {e}")


# ---------------------------
# Model commands
# ---------------------------
@cli.group(help="Manage models.")
def model():
    pass


@model.command("load", help="Load models from a JSON file.")
@click.option("--path", required=True, help="Path to the JSON file with models.")
def load(path):
    payload = {"path": path}
    try:
        resp = requests.post(api_url("/model/load"), json=payload)
        resp.raise_for_status()
        data = resp.json()
        click.echo(f"[INFO]: {data.get('message')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to load models → {e}")


@model.command("list", help="List all available models.")
def list_models():
    try:
        resp = requests.get(api_url("/model/list"))
        resp.raise_for_status()
        data = resp.json()
        click.echo("[INFO]: Available models:")
        for m in data.get("models", []):
            click.echo(f" - {m}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to list models → {e}")


@model.command("grouped", help="List models grouped by category.")
def grouped_models():
    try:
        resp = requests.get(api_url("/model/grouped"))
        resp.raise_for_status()
        data = resp.json()
        click.echo("[INFO]: Models grouped by category:")
        for group, models in data.items():
            click.echo(f"{group}:")
            for m in models:
                click.echo(f"  - {m}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to fetch grouped models → {e}")


# ---------------------------
# History command
# ---------------------------
@cli.command("history", help="Fetch past prompts and results.")
@click.option("--limit", default=50, help="Number of history records to fetch.")
@click.option("--model-name", default=None, help="Filter history by model name.")
def history(limit, model_name):
    params = {"limit": limit}
    if model_name:
        params["model_name"] = model_name
    try:
        resp = requests.get(api_url("/history"), params=params)
        resp.raise_for_status()
        data = resp.json()
        click.echo("[INFO]: History:")
        for r in data:
            click.echo(f"ID: {r['id']} | Model: {r['model']} | Prompt: {r['prompt']} | Response: {r['response']}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to fetch history → {e}")


# ---------------------------
# Version command
# ---------------------------
@cli.command("version", help="Check the server version.")
def version():
    try:
        resp = requests.get(api_url("/version"))
        resp.raise_for_status()
        data = resp.json()
        click.echo(f"[INFO]: Server version: {data.get('version')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Failed to fetch version → {e}")


# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
