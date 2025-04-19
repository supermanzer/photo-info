"""Tests for the configuration module."""

import unittest
from pathlib import Path
from unittest.mock import patch, mock_open
import tempfile
import os

from photo_info.config import Config, DEFAULT_CONFIG_NAME


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / DEFAULT_CONFIG_NAME

    def tearDown(self):
        """Clean up test fixtures."""
        if self.config_path.exists():
            self.config_path.unlink()
        os.rmdir(self.temp_dir)

    def test_init_with_default_path(self):
        """Test initialization with default config path."""
        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            config = Config()
            self.assertEqual(config.config_path, self.config_path)

    def test_init_with_custom_path(self):
        """Test initialization with custom config path."""
        custom_path = Path(self.temp_dir) / "custom.toml"
        config = Config(custom_path)
        self.assertEqual(config.config_path, custom_path)

    def test_load_config_with_absolute_paths(self):
        """Test loading config with absolute paths."""
        config_data = """
[paths]
images = "/absolute/path/to/images"
markdown = "/absolute/path/to/markdown"
"""
        with patch("builtins.open", mock_open(read_data=config_data.encode('utf-8'))):
            config = Config(self.config_path)
            config._load_config()
            self.assertEqual(config.image_dir, Path("/absolute/path/to/images"))
            self.assertEqual(config.markdown_dir, Path("/absolute/path/to/markdown"))

    def test_load_config_with_relative_paths(self):
        """Test loading config with relative paths."""
        config_data = """
[paths]
images = "images"
markdown = "markdown"
"""
        with patch("builtins.open", mock_open(read_data=config_data.encode('utf-8'))):
            config = Config(self.config_path)
            config._load_config()
            expected_image_dir = (self.config_path.parent / "images").resolve()
            expected_markdown_dir = (self.config_path.parent / "markdown").resolve()
            self.assertEqual(config.image_dir, expected_image_dir)
            self.assertEqual(config.markdown_dir, expected_markdown_dir)

    def test_load_config_with_home_expansion(self):
        """Test loading config with home directory expansion."""
        config_data = """
[paths]
images = "~/images"
markdown = "~/markdown"
"""
        with patch("builtins.open", mock_open(read_data=config_data.encode('utf-8'))):
            config = Config(self.config_path)
            config._load_config()
            self.assertEqual(config.image_dir, Path.home() / "images")
            self.assertEqual(config.markdown_dir, Path.home() / "markdown")

    def test_validate_with_valid_config(self):
        """Test validation with valid configuration."""
        config = Config()
        config.image_dir = Path(self.temp_dir)
        config.markdown_dir = Path(self.temp_dir)
        self.assertTrue(config.validate())

    def test_validate_with_missing_dirs(self):
        """Test validation with missing directories."""
        config = Config()
        self.assertFalse(config.validate())

    def test_validate_with_nonexistent_dirs(self):
        """Test validation with nonexistent directories."""
        config = Config()
        config.image_dir = Path("/nonexistent/path")
        config.markdown_dir = Path("/nonexistent/path")
        self.assertFalse(config.validate())


if __name__ == "__main__":
    unittest.main() 