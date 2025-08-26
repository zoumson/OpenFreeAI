import pytest
from unittest.mock import MagicMock
from managers.client_manager import ClientManager
from managers.llm_model_manager import LLMModelManager
from managers.usage_manager import UsageManager

@pytest.fixture
def model_manager():
    return LLMModelManager(["test-model-1", "test-model-2"])

@pytest.fixture
def usage_manager(model_manager):
    return UsageManager(model_manager=model_manager)

@pytest.fixture
def client_manager(model_manager, usage_manager, monkeypatch):
    # Patch OpenAI client inside ClientManager
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    
    manager = ClientManager(model_manager, usage_manager)
    
    # Mock the chat.completions.create method
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="mocked completion"))]
    
    manager.client.chat.completions.create = MagicMock(return_value=mock_response)
    return manager

def test_get_completion(client_manager, model_manager, usage_manager):
    result = client_manager.get_completion(0, "Hello")
    assert result == "mocked completion"
    assert usage_manager.get_usage(model_manager.get_models()[0]) > 0

def test_get_reply_stream(client_manager, model_manager, usage_manager):
    # Simulate streaming chunks
    def fake_stream(*args, **kwargs):
        class Chunk:
            def __init__(self, content):
                self.choices = [MagicMock(delta=MagicMock(content=content))]
        return [Chunk("Hello "), Chunk("world!")]

    client_manager.client.chat.completions.create = fake_stream

    collected = "".join(list(client_manager.get_reply(0, "stream test")))
    assert collected == "Hello world!"
    assert usage_manager.get_usage(model_manager.get_models()[0]) == len("Hello world!")
