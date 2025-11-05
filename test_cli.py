import tempfile
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
from daily_notes.cli import app
from daily_notes.config import Config


def test_should_store_api_key_when_login_command_run():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the config to use our temp directory
        test_api_key = "test-key-123"

        result = runner.invoke(app, ["login"], input=f"{test_api_key}\n")

        assert result.exit_code == 0
        assert "API key stored successfully" in result.stdout


def test_should_show_error_when_no_api_key_is_configured():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('daily_notes.cli.Config') as mock_config:
            mock_instance = mock_config.return_value
            mock_instance.get_api_key.return_value = None

            result = runner.invoke(app, ["note"])

            assert result.exit_code == 1
            assert "API key not found" in result.stderr
            assert "daily login" in result.stderr
