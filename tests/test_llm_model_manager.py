import pytest
from managers.llm_model_manager import LLMModelManager, LLMModelsEnum

@pytest.fixture
def temp_model_file(tmp_path):
    return tmp_path / "models.json"

def test_initial_models_load(temp_model_file):
    manager = LLMModelManager(file_path=temp_model_file)
    expected = [model.value for model in LLMModelsEnum]
    assert manager.get_models() == expected

def test_add_and_remove_model(temp_model_file):
    manager = LLMModelManager(file_path=temp_model_file)
    new_model = "custom/model-1"
    assert manager.add_model(new_model) is True
    assert new_model in manager.get_models()
    # Adding again should return False
    assert manager.add_model(new_model) is False
    # Remove
    assert manager.remove_model(new_model) is True
    assert new_model not in manager.get_models()
    # Removing again should return False
    assert manager.remove_model(new_model) is False

def test_export_and_load(temp_model_file):
    manager = LLMModelManager(file_path=temp_model_file)
    manager.add_model("custom/model-2")
    # Create a new manager to load
    manager2 = LLMModelManager(file_path=temp_model_file)
    assert "custom/model-2" in manager2.get_models()
