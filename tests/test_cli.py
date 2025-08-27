import pytest
from click.testing import CliRunner
from cli.chat_client import cli
from managers.llm_model_manager import LLMModelManager

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def temp_model_manager(tmp_path):
    temp_file = tmp_path / "models.json"
    manager = LLMModelManager(file_path=temp_file)
    return manager

def test_list_models(runner, temp_model_manager, monkeypatch):
    # Patch CLI to use temp model manager
    monkeypatch.setattr("cli.chat_client.model_manager", temp_model_manager)
    
    result = runner.invoke(cli, ["list-models"])
    assert result.exit_code == 0
    # Check default providers are listed
    assert "google" in result.output
    assert "openai" in result.output

def test_add_model(runner, temp_model_manager, monkeypatch):
    monkeypatch.setattr("cli.chat_client.model_manager", temp_model_manager)
    
    full_model = "custom/model-1:free"
    # First add
    result = runner.invoke(cli, ["add-model"], input=f"{full_model}\n")
    assert result.exit_code == 0
    assert "[SUCCESS]: Model added successfully." in result.output
    
    # Duplicate add
    result2 = runner.invoke(cli, ["add-model"], input=f"{full_model}\n")
    assert "[INFO]: Model already exists." in result2.output

def test_run_prompt(runner, temp_model_manager, monkeypatch):
    monkeypatch.setattr("cli.chat_client.model_manager", temp_model_manager)
    
    # Patch send_prompt to dummy function
    def dummy_send(prompt, model_name):
        return f"Echo: {prompt}"
    
    monkeypatch.setattr("cli.chat_client", "send_prompt", dummy_send)
    
    result = runner.invoke(cli, ["run"], input="Hello\n\n")
    assert result.exit_code == 0
    assert "Echo: Hello" in result.output

def test_run_prompt_stream(runner, temp_model_manager, monkeypatch):
    monkeypatch.setattr("cli.chat_client.model_manager", temp_model_manager)
    
    # Dummy generator for streaming
    def dummy_stream(prompt, model_name):
        for chunk in ["Hello", " ", "World", "!"]:
            yield chunk
    
    monkeypatch.setattr("cli.chat_client", "stream_prompt", dummy_stream)
    
    result = runner.invoke(cli, ["run", "--stream"], input="Hello prompt\n\n")
    assert result.exit_code == 0
    assert "Hello World!" in result.output
