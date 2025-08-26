import os
from pathlib import Path
from openai import OpenAI, InternalServerError, RateLimitError
from utils.retry_decorator import retry_request
from managers.usage_manager import UsageManager
from managers.llm_model_manager import LLMModelManager
from managers.resource_manager import ResourceManager

class ClientManager:
    def __init__(self, model_manager: LLMModelManager, usage_manager: UsageManager, base_url="https://openrouter.ai/api/v1"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY in your environment")
        
        self.client = OpenAI(base_url=base_url)
        self.model_manager = model_manager
        self.usage_manager = usage_manager
        self.log_file = Path("client_logs.json")

        # Load previous usage or logs if exists
        if self.log_file.exists():
            self.usage_manager.usage.update(ResourceManager.load_json(self.log_file))

    @retry_request(retries=5, backoff_factor=2)
    def get_completion(self, model_index: int, prompt: str) -> str:
        model_name = self.model_manager.get_models()[model_index]
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        # Update usage (fake token count = len of content for demo)
        self.usage_manager.log_usage(model_name, len(content))
        ResourceManager.save_json(self.log_file, self.usage_manager.usage)
        return content

    @retry_request(retries=5, backoff_factor=2)
    def get_reply(self, model_index: int, prompt: str):
        model_name = self.model_manager.get_models()[model_index]
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            total_tokens = 0
            for chunk in response:
                if chunk.choices[0].delta.content:
                    total_tokens += len(chunk.choices[0].delta.content)
                    yield chunk.choices[0].delta.content
            self.usage_manager.log_usage(model_name, total_tokens)
            ResourceManager.save_json(self.log_file, self.usage_manager.usage)
        except (InternalServerError, RateLimitError) as err:
            yield f"error occurred\n{err}"
