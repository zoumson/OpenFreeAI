import pytest
import json
from pathlib import Path
from managers.llm_model_manager import LLMModelManager
from managers.usage_manager import UsageManager


@pytest.fixture
def temp_files(tmp_path):
    """Fixture to create temporary model and usage files."""
    model_file = tmp_path / "models.json"
    usage_file = tmp_path / "usage.json"
    return model_file, usage_file


@pytest.fixture
def setup_managers(temp_files):
    model_file, usage_file = temp_files
    model_manager = LLMModelManager(file_path=model_file)
    usage_manager = UsageManager(file_path=usage_file, model_manager=model_manager)
    return model_manager, usage_manager


def test_initial_usage_zero(setup_managers):
    _, usage_manager = setup_managers
    for model in usage_manager.model_manager.get_models():
        assert usage_manager.get_usage(model) == 0


def test_log_usage_updates(setup_managers):
    _, usage_manager = setup_managers
    model = usage_manager.model_manager.get_models()[0]

    usage_manager.log_usage(model, 100)
    assert usage_manager.get_usage(model) == 100

    usage_manager.log_usage(model, 50)
    assert usage_manager.get_usage(model) == 150


def test_total_usage(setup_managers):
    _, usage_manager = setup_managers
    models = usage_manager.model_manager.get_models()

    usage_manager.log_usage(models[0], 200)
    usage_manager.log_usage(models[1], 300)

    assert usage_manager.get_total_usage() == 500


def test_invalid_model_raises(setup_managers):
    _, usage_manager = setup_managers
    with pytest.raises(ValueError):
        usage_manager.log_usage("invalid/model", 100)


def test_reset_usage(setup_managers):
    _, usage_manager = setup_managers
    model = usage_manager.model_manager.get_models()[0]

    usage_manager.log_usage(model, 120)
    assert usage_manager.get_usage(model) == 120

    usage_manager.reset()
    assert usage_manager.get_usage(model) == 0


def test_persistence_between_instances(temp_files):
    model_file, usage_file = temp_files
    model_manager = LLMModelManager(file_path=model_file)
    usage_manager = UsageManager(file_path=usage_file, model_manager=model_manager)

    model = model_manager.get_models()[0]
    usage_manager.log_usage(model, 42)

    # Reload from file
    usage_manager2 = UsageManager(file_path=usage_file, model_manager=model_manager)
    assert usage_manager2.get_usage(model) == 42
