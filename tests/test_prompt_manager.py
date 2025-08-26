import pytest
from pathlib import Path
from managers.prompt_manager import PromptManager

@pytest.fixture
def temp_prompt_file(tmp_path):
    return tmp_path / "prompts.json"

def test_add_and_get_prompt(temp_prompt_file):
    manager = PromptManager()
    manager.add_prompt("greet", "Hello, {name}!")
    assert manager.get_prompt("greet", name="Alice") == "Hello, Alice!"
    # Test missing kwargs
    with pytest.raises(ValueError):
        manager.get_prompt("greet")  # missing 'name'

def test_export_and_load(temp_prompt_file):
    manager = PromptManager()
    manager.add_prompt("farewell", "Goodbye, {name}!")
    manager.export_to_file(temp_prompt_file)

    # Load into a new manager
    manager2 = PromptManager(temp_prompt_file)
    assert manager2.get_prompt("farewell", name="Bob") == "Goodbye, Bob!"

def test_get_nonexistent_prompt_returns_empty():
    manager = PromptManager()
    assert manager.get_prompt("unknown") == ""
