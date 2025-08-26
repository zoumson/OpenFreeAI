import pytest
from unittest.mock import MagicMock, patch
from managers import llm_client

@pytest.fixture
def mock_client_manager():
    with patch("managers.llm_client.client_manager") as mock:
        # Mock get_completion
        mock.get_completion = MagicMock(return_value="mocked completion")
        # Mock get_reply
        def fake_reply(model_index, prompt):
            yield "chunk1 "
            yield "chunk2"
        mock.get_reply = MagicMock(side_effect=fake_reply)
        yield mock

def test_send_prompt_default_model(mock_client_manager):
    result = llm_client.send_prompt("Hello")
    # Should call the mocked get_completion
    mock_client_manager.get_completion.assert_called_once()
    assert result == "mocked completion"

def test_send_prompt_specific_model(mock_client_manager):
    result = llm_client.send_prompt("Hello", model_name="gpt-3.5-turbo")
    mock_client_manager.get_completion.assert_called_once()
    assert result == "mocked completion"

def test_stream_prompt(mock_client_manager):
    chunks = list(llm_client.stream_prompt("Stream this"))
    mock_client_manager.get_reply.assert_called_once()
    assert "".join(chunks) == "chunk1 chunk2"
