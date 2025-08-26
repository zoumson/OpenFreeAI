import pytest
from managers.llm_model_manager import LLMModelManager
from managers.usage_manager import UsageManager

@pytest.fixture
def setup_usage(tmp_path):
    model_file = tmp_path / "models.json"
    usage_file = tmp_path / "usage.json"
    model_manager = LLMModelManager(file_path=model_file)
    usage_manager = UsageManager(file_path=usage_file, model_manager=model_manager)
    return model_manager, usage_manager

def test_initial_usage_zero(setup_usage):
    _, usage_manager = setup_usage
    for model in usage_manager.model_manager.get_models():
        assert usage_manager.get_usage(model) == 0

def test_log_usage(setup_usage):
    _, usage_manager = setup_usage
    model = usage_manager.model_manager.get_models()[0]
    usage_manager.log_usage(model, 50)
    usage_manager.log_usage(model, 25)
    assert usage_manager.get_usage(model) == 75

def test_total_usage(setup_usage):
    _, usage_manager = setup_usage
    models = usage_manager.model_manager.get_models()
    usage_manager.log_usage(models[0], 10)
    usage_manager.log_usage(models[1], 20)
    assert usage_manager.get_total_usage() == 30

def test_reset_usage(setup_usage):
    _, usage_manager = setup_usage
    model = usage_manager.model_manager.get_models()[0]
    usage_manager.log_usage(model, 100)
    usage_manager.reset()
    assert usage_manager.get_usage(model) == 0

def test_invalid_model_raises(setup_usage):
    _, usage_manager = setup_usage
    with pytest.raises(ValueError):
        usage_manager.log_usage("invalid/model", 10)

def test_persistence_between_instances(tmp_path):
    model_file = tmp_path / "models.json"
    usage_file = tmp_path / "usage.json"
    model_manager = LLMModelManager(file_path=model_file)
    usage_manager = UsageManager(file_path=usage_file, model_manager=model_manager)
    model = model_manager.get_models()[0]
    usage_manager.log_usage(model, 42)

    # Load again
    usage_manager2 = UsageManager(file_path=usage_file, model_manager=model_manager)
    assert usage_manager2.get_usage(model) == 42
