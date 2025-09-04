from server.infrastructure.celery_app import celery_app
from server.app import create_app  # Flask factory

# create a global Flask app instance for Celery
app = create_app()

@celery_app.task(name="process_prompt")
def process_prompt(prompt: str, model_index: int = 0, stream: bool = False):
    """
    Process a prompt using the ClientManager inside Flask app context.
    """
    with app.app_context():
        try:
            client_manager = app.client_manager

            # Ensure models are loaded from DB/JSON before processing
            client_manager.model_manager.bulk_add_from_json()

            if stream:
                collected = []
                for chunk in client_manager.get_reply(model_index, prompt):
                    collected.append(chunk)
                return "".join(collected)
            else:
                return client_manager.get_completion(model_index, prompt)

        except IndexError:
            return "Error: No models available. Load models first."
        except Exception as e:
            return f"Error processing prompt: {e}"
