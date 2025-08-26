import pytest
from managers.conversation_manager import ConversationManager

@pytest.fixture
def conv_manager():
    return ConversationManager()

def test_add_and_get_history(conv_manager):
    conv_manager.add_message("user", "Hello")
    conv_manager.add_message("assistant", "Hi there!")
    history = conv_manager.get_history()
    assert history == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

def test_reset(conv_manager):
    conv_manager.add_message("user", "Test")
    conv_manager.reset()
    assert conv_manager.get_history() == []
