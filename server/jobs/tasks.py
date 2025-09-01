from flask import current_app

def process_prompt(prompt: str, model_index: int = 0, stream: bool = False):
    """
    Worker task to process a prompt from the queue.
    Runs automatically inside the Flask app context.
    """
    try:
        client_manager = current_app.client_manager

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
