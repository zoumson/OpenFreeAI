# server/managers/client_manager.py
import os
from pathlib import Path
from openai import OpenAI, InternalServerError, RateLimitError
from server.utils.retry_decorator import retry_request
from server.managers.usage_manager import UsageManager
from server.managers.llm_model_manager import LLMModelManager
from server.managers.resource_manager import ResourceManager
from server.database import db
from server.database.models import PromptRecord
from flask import current_app

class ClientManager:
    def __init__(self, base_url="https://openrouter.ai/api/v1"):
        # Initialize API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY in your environment")

        # OpenAI client
        self.client = OpenAI(base_url=base_url)

        # Managers
        self.model_manager = LLMModelManager()
        self.usage_manager = UsageManager()
        self.log_file = Path("client_logs.json")

        # Load existing usage logs if any
        if self.log_file.exists():
            self.usage_manager.usage.update(ResourceManager.load_json(self.log_file))

    def _save_to_db(self, prompt: str, completion: str, model_name: str, streamed: bool):
        """Internal helper to save prompt & completion to the database."""
        with current_app.app_context():
            record = PromptRecord(
                prompt_text=prompt,
                completion_text=completion,
                model_name=model_name,
                streamed=streamed
            )
            db.session.add(record)
            db.session.commit()

    @retry_request(retries=5, backoff_factor=2)
    def get_completion(self, model_index: int, prompt: str) -> str:
        """
        Returns completion from model and records usage + DB entry.
        """
        model_name = self.model_manager.get_models()[model_index]

        # Call OpenAI completion API
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content

        # Log usage and save locally
        self.usage_manager.log_usage(model_name, len(content))
        ResourceManager.save_json(self.log_file, self.usage_manager.usage)

        # Save to DB
        self._save_to_db(prompt, content, model_name, streamed=False)

        return content

    @retry_request(retries=5, backoff_factor=2)
    def get_reply(self, model_index: int, prompt: str):
        """
        Stream response from model while logging usage and saving full response to DB.
        """
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

            # Log usage and save locally
            self.usage_manager.log_usage(model_name, total_tokens)
            ResourceManager.save_json(self.log_file, self.usage_manager.usage)

            # Save full streamed response to DB
            self._save_to_db(prompt, "".join(collected), model_name, streamed=True)

        except (InternalServerError, RateLimitError) as err:
            yield f"[ERROR]: {err}"
        except Exception as e:
            yield f"[ERROR]: {e}"
