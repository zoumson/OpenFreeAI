import pytest
import json
from pathlib import Path
from llm_model_manager import LLMModelManager, LLMModel, db, app

@pytest.fixture(scope="function")
def manager():
    # Use in-memory SQLite for testing
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        manager = LLMModelManager()
        yield manager
        db.drop_all()

def test_add_model(manager):
    full_model = "openai/gpt-test-1:free"
    added = manager.add_model(full_model)
    assert added is True
    # Duplicate add returns False
    assert manager.add_model(full_model) is False
    models = manager.get_models()
    assert full_model in models

def test_remove_model(manager):
    full_model = "openai/gpt-test-2:free"
    manager.add_model(full_model)
    # Remove existing
    model_obj = LLMModel.query.filter_by(full_model=full_model).first()
    assert model_obj is not None
    db.session.delete(model_obj)
    db.session.commit()
    # Confirm removal
    assert manager.get_models() == []

def test_bulk_add_from_json(manager, tmp_path):
    # Create temporary JSON file
    json_file = tmp_path / "models.json"
    model_list = [
        "openai/gpt-bulk-1:free",
        "google/gem-bulk-1:free",
        "qwen/qwen-bulk-1:free"
    ]
    json_file.write_text(json.dumps(model_list))

    count = manager.bulk_add_from_json(json_file)
    assert count == 3

    models_in_db = manager.get_models()
    for m in model_list:
        assert m in models_in_db

def test_get_grouped_models(manager):
    manager.add_model("openai/gpt-group-1:free")
    manager.add_model("google/gem-group-1:free")
    grouped = manager.get_grouped_models()
    assert "openai" in grouped
    assert "google" in grouped
    openai_models = [m["full_model"] for m in grouped["openai"]]
    assert "openai/gpt-group-1:free" in openai_models
