from server.managers.llm_model_manager import LLMModelManager
from server.database import db
from server.database.models import PromptRecord

# Initialize the model manager
model_manager = LLMModelManager()

def process_prompt(prompt: str, model_index: int = 0):
    """
    Worker task to process a prompt from the queue.
    Stores result in the database.
    """
    try:
        # Get completion from the model
        completion = model_manager.get_completion(model_index, prompt)

        # Save to DB
        with db.app.app_context():
            record = PromptRecord(
                prompt_text=prompt,
                completion_text=completion,
                model_name=model_manager.get_model_name(model_index),
                streamed=False
            )
            db.session.add(record)
            db.session.commit()

        return completion

    except IndexError:
        return "Error: No models available. Load models first."
    except Exception as e:
        return f"Error processing prompt: {e}"
