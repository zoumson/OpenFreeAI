import pytest
from managers.prompt_manager import PromptManager

@pytest.fixture
def prompt_manager():
    pm = PromptManager()
    pm.add_prompt("greet", "Hello, {name}!")
    return pm

def test_get_prompt(prompt_manager):
    result = prompt_manager.get_prompt("greet", name="Alice")
    assert result == "Hello, Alice!"

def test_add_prompt():
    pm = PromptManager()
    pm.add_prompt("bye", "Goodbye, {name}!")
    result = pm.get_prompt("bye", name="Bob")
    assert result == "Goodbye, Bob!"

def test_export_and_load(tmp_path):
    pm = PromptManager()
    pm.add_prompt("test", "Hi {name}")
    file_path = tmp_path / "prompts.json"
    pm.export_to_file(file_path)
    
    new_pm = PromptManager()
    new_pm.load_from_file(file_path)
    result = new_pm.get_prompt("test", name="Charlie")
    assert result == "Hi Charlie"
