import tempfile
from pathlib import Path
from daily_notes.config import Config


def test_should_return_none_when_no_api_key_is_stored():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(app_dir=Path(temp_dir))
        api_key = config.get_api_key()
        assert api_key is None


def test_should_store_and_retrieve_api_key():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(app_dir=Path(temp_dir))
        test_api_key = "test-api-key-123"
        
        config.set_api_key(test_api_key)
        retrieved_key = config.get_api_key()
        
        assert retrieved_key == test_api_key


def test_should_maintain_config_behavior_after_pydantic_refactor():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(app_dir=Path(temp_dir))
        
        # Test that Config is instance-based (not just a static class)
        assert hasattr(config, 'app_dir')
        assert hasattr(config, 'config_file')
        assert hasattr(config, 'get_api_key')
        assert hasattr(config, 'set_api_key')
        
        # Test the complete workflow
        assert config.get_api_key() is None
        config.set_api_key("test-key")
        assert config.get_api_key() == "test-key"