import requests
import click
import time
from client.config import SERVER_URL, API_PREFIX

# ---------------------------
# Helper
# ---------------------------
def api_url(path: str) -> str:
    return f"{SERVER_URL}{API_PREFIX}{path}"

# ---------------------------
# CLI entry
# ---------------------------
@click.group()
def cli():
    """CLI client for interacting with the LLM Flask server."""
    pass

# ---------------------------
# Job commands
# ---------------------------
@cli.group(help="Manage jobs on the server.")
def job():
    pass

@job.command("submit", help="Submit a prompt as a job.")
@click.option("--prompt", prompt="Enter your prompt", help="The text prompt to send.")
@click.option("--model-index", default=0, help="Index of model to use.")
@click.option("--stream", is_flag=True, help="Whether to stream the result.")
def submit(prompt, model_index, stream):
    payload = {
        "prompt": prompt,
        "model_index": model_index,
        "stream": stream
    }
    try:
        r = requests.post(api_url("/prompt"), json=payload)
        r.raise_for_status()
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")
        return

    job_info = r.json()
    click.echo(f"[INFO]: Job submitted with job_id: {job_info.get('job_id')}")

@job.command("result", help="Get the result of a submitted job.")
@click.argument("job_id")
@click.option("--poll", is_flag=True, help="Poll until the result is ready.")
@click.option("--interval", default=1.0, help="Polling interval in seconds.")
def result(job_id, poll, interval):
    try:
        while True:
            r = requests.get(api_url(f"/job/{job_id}"))
            r.raise_for_status()
            job_info = r.json()
            status = job_info.get("status")

            if status == "completed":
                click.echo(f"[RESULT]: {job_info.get('result')}")
                break
            elif status == "failed":
                click.echo(f"[ERROR]: Job failed: {job_info.get('error')}")
                break

            if not poll:
                click.echo(f"[INFO]: Job status: {status}")
                break

            time.sleep(interval)

    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

# ---------------------------
# Model commands
# ---------------------------
@cli.group(help="Manage models via the Flask server.")
def model():
    pass

@model.command("load", help="Load models from a JSON file.")
@click.argument("json_file", type=click.Path(exists=True))
def load(json_file):
    payload = {"path": json_file}
    try:
        r = requests.post(api_url("/model/load"), json=payload)
        r.raise_for_status()
        click.echo(r.json().get("message"))
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

@model.command("list", help="List all stored models.")
def list_models():
    try:
        r = requests.get(api_url("/model/list"))
        r.raise_for_status()
        models = r.json().get("models", [])
        if not models:
            click.echo("[INFO]: No models in the database.")
        else:
            click.echo("Models:")
            for m in models:
                click.echo(f"- {m}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

@model.command("grouped", help="List models grouped by provider.")
def grouped_models():
    try:
        r = requests.get(api_url("/model/grouped"))
        r.raise_for_status()
        grouped = r.json()
        if not grouped:
            click.echo("[INFO]: No models in the database.")
        else:
            for provider, models in grouped.items():
                click.echo(f"Provider: {provider}")
                for m in models:
                    click.echo(f"  - {m['model_name']}:{m['tag']}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

# ---------------------------
# Version command
# ---------------------------
@cli.command(help="Get server API version.")
def version():
    try:
        r = requests.get(api_url("/version"))
        r.raise_for_status()
        click.echo(f"Server version: {r.json().get('version')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Could not get server version. {e}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
