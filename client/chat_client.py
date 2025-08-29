# client/chat_client.py
import requests
import click
import time
from client.config import SERVER_URL  # SERVER_URL should be like "http://127.0.0.1:5000"

@click.group()
def cli():
    """CLI client for interacting with the LLM Flask server."""
    pass

# ---------------------------
# Prompt command (producer)
# ---------------------------
@cli.command(help="Send a prompt to the LLM.")
@click.option("--prompt", prompt="Enter your prompt", help="The input text prompt to send to the LLM.")
@click.option("--model-index", default=0, help="Index of model to use.")
@click.option("--poll", is_flag=True, help="Poll until the result is ready.")
@click.option("--interval", default=1.0, help="Polling interval in seconds.")
def run(prompt, model_index, poll, interval):
    data = {"prompt": prompt, "model_index": model_index}
    try:
        r = requests.post(f"{SERVER_URL}/api/v1/prompt", json=data)
        r.raise_for_status()
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")
        return

    job_info = r.json()
    job_id = job_info.get("job_id")
    click.echo(f"[INFO]: Task queued with job_id: {job_id}")

    if poll:
        click.echo("[INFO]: Polling for result...")
        while True:
            try:
                res = requests.get(f"{SERVER_URL}/api/v1/job/{job_id}")
                res.raise_for_status()
                job_result = res.json()
                status = job_result.get("status")
                if status == "completed":
                    click.echo(f"[COMPLETION]: {job_result.get('response')}")
                    break
                elif status == "failed":
                    click.echo(f"[ERROR]: Job failed: {job_result.get('error')}")
                    break
                time.sleep(interval)
            except requests.RequestException as e:
                click.echo(f"[ERROR]: {e}")
                break

# ---------------------------
# Model management commands
# ---------------------------
@cli.group(help="Manage models via the Flask server.")
def model():
    pass

@model.command("load", help="Load models from a JSON file.")
@click.argument("json_file", type=click.Path(exists=True))
def load(json_file):
    try:
        r = requests.post(f"{SERVER_URL}/api/v1/model/load", json={"path": json_file})
        r.raise_for_status()
        click.echo(r.json().get("message"))
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

@model.command("list", help="List all stored models.")
def list_models():
    try:
        r = requests.get(f"{SERVER_URL}/api/v1/model/list")
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
        r = requests.get(f"{SERVER_URL}/api/v1/model/grouped")
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
# Server version command
# ---------------------------
@cli.command(help="Get server API version.")
def version():
    try:
        r = requests.get(f"{SERVER_URL}/api/v1/version")
        r.raise_for_status()
        click.echo(f"Server version: {r.json().get('version')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Could not get server version. {e}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
