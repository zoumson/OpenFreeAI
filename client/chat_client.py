import requests
import click
from client.config import SERVER_URL, API_PREFIX

def api_url(path: str) -> str:
    return f"{SERVER_URL}{API_PREFIX}{path}"

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

@job.command("submit", help="Submit a prompt as a job.")
@click.option("--prompt", required=True, help="The input text prompt to send to the LLM.")
@click.option("--model-index", default=0, help="Index of the model to use.")
def submit(prompt, model_index):
    payload = {"prompt": prompt, "model_index": model_index}
    try:
        r = requests.post(api_url("/prompt"), json=payload)
        r.raise_for_status()
        job_info = r.json()
        click.echo(f"[INFO]: Job submitted. ID: {job_info.get('job_id')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

@job.command("result", help="Get the result of a job (if finished).")
@click.argument("job_id")
def result(job_id):
    try:
        r = requests.get(api_url(f"/job/{job_id}"))
        r.raise_for_status()
        job_info = r.json()
        if job_info.get("status") == "finished":
            click.echo(f"[RESULT]: {job_info.get('result')}")
        else:
            click.echo(f"[INFO]: Job not finished yet. Status: {job_info.get('status')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

@job.command("status", help="Get the status of a job.")
@click.argument("job_id")
def status(job_id):
    try:
        r = requests.get(api_url(f"/job/{job_id}"))
        r.raise_for_status()
        job_info = r.json()
        click.echo(f"[INFO]: Job status: {job_info.get('status')}")
    except requests.RequestException as e:
        click.echo(f"[ERROR]: {e}")

# ---------------------------
# Entry point
# ---------------------------
if __name__ == "__main__":
    cli()
