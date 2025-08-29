# client/chat_client.py
import requests
import click
from client.config import SERVER_URL  # Make sure config.py defines SERVER_URL

@click.group()
def cli():
    """CLI client for interacting with the LLM Flask server."""
    pass

# ---------------------------
# Prompt command
# ---------------------------
@cli.command(help="Send a prompt to the LLM.")
@click.option("--prompt", prompt="Enter your prompt", help="The input text prompt to send to the LLM.")
@click.option("--model", default=None, help="Model name to use (optional).")
@click.option("--stream", is_flag=True, help="Enable streaming mode for output.")
def run(prompt, model, stream):
    data = {"prompt": prompt}
    if model:
        data["model"] = model

    url = f"{SERVER_URL}/prompt"
    if stream:
        with requests.post(url, json=data, stream=True) as r:
            if r.status_code != 200:
                click.echo(f"[ERROR]: {r.text}")
                return
            for chunk in r.iter_lines(decode_unicode=True):
                if chunk:
                    click.echo(chunk, nl=False)
            click.echo()
    else:
        try:
            r = requests.post(url, json=data)
            r.raise_for_status()
            resp = r.json()
            click.echo(f"[COMPLETION]: {resp.get('response')}")
        except requests.RequestException as e:
            click.echo(f"[ERROR]: {e}")

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
        r = requests.post(f"{SERVER_URL}/model/load", json={"path": json_file})
        r.raise_for_status()
        click.echo(r.json().get("message"))
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

@model.command("list", help="List all stored models.")
def list_models():
    try:
        r = requests.get(f"{SERVER_URL}/model/list")
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
        r = requests.get(f"{SERVER_URL}/model/grouped")
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
        r = requests.get(f"{SERVER_URL}/version")
        r.raise_for_status()
        click.echo(f"Server version: {r.json().get('version')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: Could not get server version. {e}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
