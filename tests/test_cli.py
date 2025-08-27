import pytest
import json
from click.testing import CliRunner
from chat_client import cli
from managers.llm_model_manager import app, db

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def clean_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

def test_model_load_command(runner, clean_db, tmp_path):
    json_file = tmp_path / "models.json"
    models_data = {
        "openai": [{"model": "gpt-test-1", "tag": "free"}],
        "google": [{"model": "gemini-test", "tag": "pro"}]
    }
    json_file.write_text(json.dumps(models_data))

    result = runner.invoke(cli, ["model", "load", str(json_file)])
    assert result.exit_code == 0
    assert "[SUCCESS]: Added 2 models" in result.output

def test_model_list_command(runner, clean_db):
    # Add models first
    runner.invoke(cli, ["model", "load", "tests/test_models.json"])

    result = runner.invoke(cli, ["model", "list"])
    assert result.exit_code == 0
    assert "Stored models:" in result.output
    assert "openai/gpt-oss-20b:free" in result.output

def test_model_grouped_command(runner, clean_db):
    # Add models first
    runner.invoke(cli, ["model", "load", "tests/test_models.json"])

    result = runner.invoke(cli, ["model", "grouped"])
    assert result.exit_code == 0
    assert "Provider: openai" in result.output
    assert "Provider: google" in result.output
    assert "gpt-oss-20b:free" in result.output
    assert "gemma-3n-e2b-it:free" in result.output

def test_run_prompt_command(runner):
    # This assumes your run command is still functional
    # We just test it can invoke without errors
    result = runner.invoke(cli, ["run", "--prompt", "Hello", "--model", "openai/gpt-oss-20b:free"])
    assert result.exit_code == 0
