import click
from clients.llm_client import send_prompt, stream_prompt, model_manager

@click.command()
@click.option("--prompt", prompt="Enter your prompt", help="The prompt to send to the model.")
@click.option("--model", default=None, help="LLM model name (default: first model in list).")
@click.option("--stream", is_flag=True, help="Enable streaming output.")
def main(prompt, model, stream):
    """Interactive LLM client using Click."""
    # Show available models
    click.echo("\n[MODELS AVAILABLE]:")
    for m in model_manager.get_models():
        click.echo(f"- {m}")

    # Use default model if none provided
    model_name = model or model_manager.get_models()[0]

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
