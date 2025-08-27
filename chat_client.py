import click
from clients.llm_client import send_prompt, stream_prompt  # keep run prompt functions
from managers.llm_model_manager import app, db, LLMModelManager

manager = LLMModelManager()

@click.group()
def cli():
    """Main CLI for LLM operations"""
    pass

# ---------------------------
# Run prompt commands (existing)
# ---------------------------
@cli.command(help="Send a prompt to the LLM.")
@click.option("--prompt", prompt="Enter your prompt", help="The input text prompt to send to the LLM.")
@click.option("--model", default=None, help="LLM model name (full identifier like 'openai/gpt-oss-20b:free').")
@click.option("--stream", is_flag=True, help="Enable streaming mode for output.")
def run(prompt, model, stream):
    available_models = manager.get_models()  # use DB models
    if not available_models:
        click.echo("[INFO]: No models available. Please load models first.")
        return

    model_name = model or available_models[0]
    if model_name not in available_models:
        click.echo(f"[ERROR]: Model '{model_name}' is not available in DB.")
        return

    try:
        if stream:
            click.echo(f"[STREAMING RESPONSE] from {model_name}:")
            for chunk in stream_prompt(prompt, model_name=model_name):
                click.echo(chunk, nl=False)
            click.echo()
        else:
            completion = send_prompt(prompt, model_name=model_name)
            click.echo(f"[COMPLETION] from {model_name}: {completion}")
    except Exception as e:
        click.echo(f"[ERROR]: {e}")

# ---------------------------
# Model management commands
# ---------------------------
@cli.group(help="Manage LLM models in the database.")
def model():
    pass

@model.command("load", help="Load models from a JSON file into the database.")
@click.argument("json_file", type=click.Path(exists=True))
def load(json_file):
    count = manager.bulk_add_from_json(json_file)
    click.echo(f"[SUCCESS]: Added {count} models from {json_file}")

@model.command("list", help="List all models stored in the database.")
def list_models():
    models = manager.get_models()
    if not models:
        click.echo("[INFO]: No models in the database.")
        return
    click.echo("Stored models:")
    for m in models:
        click.echo(f"- {m}")

@model.command("grouped", help="List models grouped by provider.")
def grouped():
    grouped = manager.get_grouped_models()
    if not grouped:
        click.echo("[INFO]: No models in the database.")
        return
    for provider, models in grouped.items():
        click.echo(f"Provider: {provider}")
        for m in models:
            click.echo(f"  - {m['model_name']}:{m['tag']}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
