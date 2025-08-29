import os
from pathlib import Path
from openai import OpenAI, InternalServerError, RateLimitError
from utils.retry_decorator import retry_request
from managers.usage_manager import UsageManager
from managers.llm_model_manager import LLMModelManager
from database.models import PromptRecord
from database import db
from app import app
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
        self.usage_manager.log_usage(model_name, len(content))
        ResourceManager.save_json(self.log_file, self.usage_manager.usage)

        # Save to DB
        with app.app_context():
            record = PromptRecord(
                prompt_text=prompt,
                completion_text=content,
                model_name=model_name,
                streamed=False
            )
            db.session.add(record)
            db.session.commit()

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
            collected = []

            for chunk in response:
                delta = chunk.choices[0].delta.get("content")
                if delta:
                    total_tokens += len(delta)
                    collected.append(delta)
                    yield delta

            self.usage_manager.log_usage(model_name, total_tokens)
            ResourceManager.save_json(self.log_file, self.usage_manager.usage)

            with app.app_context():
                record = PromptRecord(
                    prompt_text=prompt,
                    completion_text="".join(collected),
                    model_name=model_name,
                    streamed=True
                )
                db.session.add(record)
                db.session.commit()
        except (InternalServerError, RateLimitError) as err:
            yield f"[ERROR]: {err}"
        except Exception as e:
            yield f"[ERROR]: {e}"
