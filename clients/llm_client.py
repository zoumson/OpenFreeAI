from managers.client_manager import ClientManager
from managers.llm_model_manager import LLMModelManager
from managers.usage_manager import UsageManager

# ----------------------------
# Initialize managers
# ----------------------------
model_manager = LLMModelManager([
    "qwen/qwen3-coder:free",
    "gpt-3.5-turbo",
    "gpt-4"
])
usage_manager = UsageManager(model_manager=model_manager)
client_manager = ClientManager(model_manager=model_manager, usage_manager=usage_manager)

# ----------------------------
# High-level API
# ----------------------------
def send_prompt(prompt: str, model_name: str = None) -> str:
    """Send prompt to a model (default: first in list)."""
    if model_name is None:
        model_name = model_manager.get_models()[0]
    return client_manager.get_completion(model_manager.get_models().index(model_name), prompt)

def stream_prompt(prompt: str, model_name: str = None):
    """Stream prompt response."""
    if model_name is None:
        model_name = model_manager.get_models()[0]
    return client_manager.get_reply(model_manager.get_models().index(model_name), prompt)

def get_usage(model_name: str):
    """Get usage for a specific model."""
    return usage_manager.get_usage(model_name)

def reset_usage(model_name: str = None):
    """Reset usage for a model or all models if None."""
    if model_name:
        usage_manager.reset_model(model_name)
    else:
        usage_manager.reset()
