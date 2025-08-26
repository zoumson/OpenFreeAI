import pytest
from managers.usage_manager import UsageManager
from managers.llm_model_manager import LLMModelManager

@pytest.fixture
def usage_manager():
    model_mgr = LLMModelManager(["test-model"])
    return UsageManager(model_manager=model_mgr)

def test_log_and_get_usage(usage_manager):
    usage_manager.log_usage("test-model", 10)
    assert usage_manager.get_usage("test-model") == 10
    usage_manager.log_usage("test-model", 5)
    assert usage_manager.get_usage("test-model") == 15

def test_reset(usage_manager):
    usage_manager.log_usage("test-model", 10)
    usage_manager.reset()
    assert usage_manager.get_usage("test-model") == 0
