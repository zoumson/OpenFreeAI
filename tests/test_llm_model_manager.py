import pytest
import json
from pathlib import Path
from managers.llm_model_manager import app, db, LLMModelManager, LLMModel

@pytest.fixture(scope="function")
def test_app():
    # Use an in-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def manager(test_app):
    return LLMModelManager()

def test_add_and_get_models(manager):
    full_model = "openai/gpt-test:free"
    assert manager.add_model(full_model) is True
    models = manager.get_models()
    assert full_model in models

    # Adding same model again should return False
    assert manager.add_model(full_model) is False

def test_remove_model(manager):
    full_model = "openai/gpt-remove:free"
    manager.add_model(full_model)
    assert manager.remove_model(full_model) is True
    assert manager.remove_model(full_model) is False
    assert full_model not in manager.get_models()

def test_get_grouped_models(manager):
    manager.add_model("google/gem-test:free")
    manager.add_model("google/gem-test2:pro")
    manager.add_model("openai/gpt-test:free")
    
    grouped = manager.get_grouped_models()
    assert "google" in grouped
    assert "openai" in grouped
    google_models = [m["model"] for m in grouped["google"]]
    assert "gem-test" in google_models
    assert "gem-test2" in google_models

def test_bulk_add_from_json(manager, tmp_path):
    data = {
        "google": [
            {"model": "gem-bulk1", "tag": "free"},
            {"model": "gem-bulk2", "tag": "pro"}
        ],
        "openai": [
            {"model": "gpt-bulk", "tag": "free"}
        ]
    }
    json_file = tmp_path / "models.json"
    json_file.write_text(json.dumps(data))

    count = manager.bulk_add_from_json(str(json_file))
    assert count == 3

    models = manager.get_models()
    assert "google/gem-bulk1:free" in models
    assert "google/gem-bulk2:pro" in models
    assert "openai/gpt-bulk:free" in models
