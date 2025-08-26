import pytest
from managers.conversation_manager import ConversationManager

@pytest.fixture
def temp_conv_file(tmp_path):
    return tmp_path / "conversation.json"

def test_add_and_get_history(temp_conv_file):
    manager = ConversationManager(file_path=temp_conv_file)
    manager.add_message("user", "Hello")
    manager.add_message("assistant", "Hi there!")
    history = manager.get_history()
    
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Hello"}
    assert history[1] == {"role": "assistant", "content": "Hi there!"}

def test_reset_history(temp_conv_file):
    manager = ConversationManager(file_path=temp_conv_file)
    manager.add_message("user", "Hello")
    manager.reset()
    
    assert manager.get_history() == []

def test_persistence(tmp_path):
    conv_file = tmp_path / "conversation.json"
    
    # First manager adds messages
    manager1 = ConversationManager(file_path=conv_file)
    manager1.add_message("user", "Hello")
    manager1.add_message("assistant", "Hi there!")
    
    # Load a new manager and check history
    manager2 = ConversationManager(file_path=conv_file)
    history = manager2.get_history()
    
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Hello"}
    assert history[1] == {"role": "assistant", "content": "Hi there!"}

def test_no_file_path():
    manager = ConversationManager()
    manager.add_message("user", "Hello")
    manager.add_message("assistant", "Hi")
    assert len(manager.get_history()) == 2
    # No exceptions should be raised when file_path is None
