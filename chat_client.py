import click
from clients.llm_client import send_prompt, stream_prompt, model_manager

@click.command(help="Interactive LLM client that sends prompts to available models.")
@click.option(
    "--prompt", 
    prompt="Enter your prompt", 
    help="The input text prompt to send to the LLM."
)
@click.option(
    "--model", 
    default=None, 
    help="Name of the LLM model to use. "
         "If not provided, the first available model will be used."
)
@click.option(
    "--stream", 
    is_flag=True, 
    help="Enable streaming mode to receive the model's output as it is generated."
)
def main(prompt, model, stream):
    """Interactive LLM client using Click."""
    available_models = model_manager.get_models()

    # Show available models
    click.echo("\n[MODELS AVAILABLE]:")
    for m in available_models:
        click.echo(f"- {m}")

    # Validate model argument
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
            click.echo()  # newline after stream
        else:
            completion = send_prompt(prompt, model_name=model_name)
            click.echo(f"\n[COMPLETION] from {model_name}: {completion}")
    except Exception as e:
        click.echo(f"[ERROR]: {e}")

if __name__ == "__main__":
    main()
