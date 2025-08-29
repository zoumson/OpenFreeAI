import requests
import click

SERVER_URL = "http://127.0.0.1:5000"

@click.group()
def cli():
    """CLI client for interacting with the LLM Flask server."""
    pass

# ---------------------------
# Run prompt commands
# ---------------------------
@cli.command(help="Send a prompt to the LLM.")
@click.option("--prompt", prompt="Enter your prompt", help="The input text prompt to send to the LLM.")
@click.option("--model", default=None, help="Model name to use (optional).")
@click.option("--stream", is_flag=True, help="Enable streaming mode for output.")
def run(prompt, model, stream):
    data = {"prompt": prompt}
    if model:
        data["model"] = model

    if stream:
        with requests.post(f"{SERVER_URL}/prompt", json=data, stream=True) as r:
            if r.status_code != 200:
                click.echo(f"[ERROR]: {r.text}")
                return
            for chunk in r.iter_lines(decode_unicode=True):
                if chunk:
                    click.echo(chunk, nl=False)
            click.echo()
    else:
        r = requests.post(f"{SERVER_URL}/prompt", json=data)
        if r.status_code == 200:
            resp = r.json()
            click.echo(f"[COMPLETION]: {resp.get('response')}")
        else:
            click.echo(f"[ERROR]: {r.text}")

# ---------------------------
# Model management commands
# ---------------------------
@cli.group(help="Manage models via the Flask server.")
def model():
    pass

@model.command("load", help="Load models from a JSON file.")
@click.argument("json_file", type=click.Path(exists=True))
def load(json_file):
    r = requests.post(f"{SERVER_URL}/model/load", json={"path": json_file})
    if r.status_code == 200:
        click.echo(r.json().get("message"))
    else:
        click.echo(f"[ERROR]: {r.text}")

@model.command("list", help="List all stored models.")
def list_models():
    r = requests.get(f"{SERVER_URL}/model/list")
    if r.status_code == 200:
        models = r.json().get("models", [])
        if not models:
            click.echo("[INFO]: No models in the database.")
        else:
            click.echo("Models:")
            for m in models:
                click.echo(f"- {m}")
    else:
        click.echo(f"[ERROR]: {r.text}")

@model.command("grouped", help="List models grouped by provider.")
def grouped_models():
    r = requests.get(f"{SERVER_URL}/model/grouped")
    if r.status_code == 200:
        grouped = r.json()
        if not grouped:
            click.echo("[INFO]: No models in the database.")
        else:
            for provider, models in grouped.items():
                click.echo(f"Provider: {provider}")
                for m in models:
                    click.echo(f"  - {m['model_name']}:{m['tag']}")
    else:
        click.echo(f"[ERROR]: {r.text}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
