import click
from clients.llm_client import send_prompt, stream_prompt, model_manager

@click.group(help="Interactive LLM client for sending prompts and managing models.")
def cli():
    pass

# ---------------------------
# Run a prompt
# ---------------------------
@cli.command(help="Send a prompt to the LLM.")
@click.option("--prompt", prompt="Enter your prompt", help="The input text prompt to send to the LLM.")
@click.option("--model", default=None, help="LLM model name (full identifier like 'openai/gpt-oss-20b:free').")
@click.option("--stream", is_flag=True, help="Enable streaming mode for output.")
def run(prompt, model, stream):
    available_models = model_manager.get_models()

    # Use first model if none provided
    model_name = model or (available_models[0] if available_models else None)
    if not model_name:
        click.echo("[ERROR]: No models available to run.")
        return

    if model_name not in available_models:
        click.echo(f"[ERROR]: Model '{model_name}' is not available.")
        click.echo("Use 'list-models' to see available models.")
        return

    try:
        if stream:
            click.echo(f"\n[STREAMING RESPONSE] from {model_name}:")
            for chunk in stream_prompt(prompt, model_name=model_name):
                click.echo(chunk, nl=False)
            click.echo()
        else:
            completion = send_prompt(prompt, model_name=model_name)
            click.echo(f"\n[COMPLETION] from {model_name}: {completion}")
    except Exception as e:
        click.echo(f"[ERROR]: {e}")

# ---------------------------
# Add a new model
# ---------------------------
@cli.command(help="Add a new LLM model to the system.")
@click.option("--full", "full_model", default=None, help="Full model string (e.g., 'openai/gpt-oss-20b:free').")
@click.option("--provider", default=None, help="Provider name (e.g., openai).")
@click.option("--model", "model_name", default=None, help="Model name (e.g., gpt-4).")
@click.option("--tag", default="free", help="Tag for the model (default: free).")
def add_model(full_model, provider, model_name, tag):
    """
    Add a new LLM model. Priority rules:
    1. If --full is provided, it is used and --provider/--model are ignored.
    2. Otherwise, both --provider and --model must be provided.
    """
    if full_model:
        added = model_manager.add_model(full_model=full_model)
    elif provider and model_name:
        added = model_manager.add_model(provider=provider, model_name=model_name, tag=tag)
    else:
        click.echo("[ERROR]: You must provide either --full or both --provider and --model.")
        return

    if added:
        click.echo(f"[SUCCESS]: Model added successfully.")
    else:
        click.echo(f"[INFO]: Model already exists.")

# ---------------------------
# List models
# ---------------------------
@cli.command(help="List all available models grouped by provider.")
def list_models():
    grouped = model_manager.get_models_grouped_by_provider()
    if not grouped:
        click.echo("[INFO]: No models available.")
        return

    click.echo("\n[AVAILABLE MODELS GROUPED BY PROVIDER]:")
    for provider, models in grouped.items():
        click.echo(f"\n{provider.upper()}:")
        for m in models:
            tag_str = f" ({m['tag']})" if m["tag"] else ""
            click.echo(f"  - {m['model']}{tag_str}")

# ---------------------------
# Main entry
# ---------------------------
if __name__ == "__main__":
    cli()
