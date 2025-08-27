import click
from clients.llm_client import send_prompt, stream_prompt, model_manager

@click.group(help="Interactive LLM client for sending prompts and managing models.")
def cli():
    pass

@cli.command(help="Send a prompt to the LLM.")
@click.option("--prompt", prompt="Enter your prompt", help="The input text prompt to send to the LLM.")
@click.option("--model", default=None, help="LLM model name (default: first model in list).")
@click.option("--stream", is_flag=True, help="Enable streaming mode for output.")
def run(prompt, model, stream):
    available_models = model_manager.get_models()

    click.echo("\n[MODELS AVAILABLE]:")
    for m in available_models:
        click.echo(f"- {m}")

    if model:
        if model not in available_models:
            click.echo(f"[ERROR]: Model '{model}' is not available.")
            click.echo("Please choose one from the list above.")
            return
        model_name = model
    else:
        model_name = available_models[0]

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

@cli.command(help="Add a new LLM model to the system.")
@click.option("--name", prompt="Model name", help="Name of the new LLM model (e.g., openai/gpt-4).")
def add_model(name):
    """Adds a new LLM model to the model manager."""
    try:
        model_manager.add_model(name)
        click.echo(f"[SUCCESS]: Model '{name}' added.")
    except Exception as e:
        click.echo(f"[ERROR]: Failed to add model: {e}")

if __name__ == "__main__":
    cli()
