import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import os
from typer.testing import CliRunner

from photo_info.photo_info import (
    get_exif_data,
    get_labeled_exif,
    write_to_markdown,
    MY_TAGS,
    identify_new_images,
)
from photo_info.cli import app
from photo_info.config import Config


class TestPhotoInfo(unittest.TestCase):
    """Test cases for the photo_info module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.image_dir = Path(self.temp_dir) / "images"
        self.md_dir = Path(self.temp_dir) / "markdown"
        self.image_dir.mkdir()
        self.md_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        if self.image_dir.exists():
            self.image_dir.rmdir()
        if self.md_dir.exists():
            self.md_dir.rmdir()
        os.rmdir(self.temp_dir)

    @patch("photo_info.photo_info.Image.open")
    def test_get_exif_data(self, mock_open):
        """Test getting EXIF data from an image."""
        mock_image = MagicMock()
        mock_image._getexif.return_value = {271: "NIKON CORPORATION", 272: "NIKON D750"}
        mock_open.return_value = mock_image

        exif_data = get_exif_data(mock_image)
        self.assertEqual(exif_data[271], "NIKON CORPORATION")
        self.assertEqual(exif_data[272], "NIKON D750")

    def test_get_labeled_exif(self):
        """Test getting labeled EXIF data."""
        exif_data = {
            271: "NIKON CORPORATION",
            272: "NIKON D750",
            36867: "2021:09:01 12:00:00",
            37386: (50, 1),
            33434: (1, 125),
            34855: 100,
            37377: 0,
            42036: "NIKON",
            42037: "24-70mm f/2.8",
        }

        labeled_exif = get_labeled_exif(exif_data)
        self.assertEqual(labeled_exif["Make"], "NIKON CORPORATION")
        self.assertEqual(labeled_exif["Model"], "NIKON D750")
        self.assertEqual(labeled_exif["DateTimeOriginal"], "2021:09:01 12:00:00")

    def test_identify_new_images(self):
        """Test identifying new images."""
        with patch("os.listdir") as mock_listdir:
            mock_listdir.side_effect = [
                ["DSC_3021.jpg", "DSC_3106.jpg"],
                ["DSC_3106.md"],
            ]
            found_images = identify_new_images("test_files/", "test_files/")
            self.assertEqual(found_images, ["DSC_3021"])

    @patch("builtins.open", new_callable=mock_open)
    def test_write_to_markdown(self, mock_file):
        """Test writing EXIF data to markdown."""
        labeled_exif = {
            "Make": "NIKON CORPORATION",
            "Model": "NIKON D750",
            "DateTimeOriginal": "2021:09:01 12:00:00",
        }
        # Create a test image path that includes 'public'
        image_path = "test_files/public/images/DSC_3106.jpg"
        write_to_markdown(image_path, labeled_exif, "test_files/")
        mock_file.assert_called_once_with(
            "test_files/DSC_3106.md", "w+", encoding="utf-8"
        )
        mock_file().write.assert_any_call("---\n")
        mock_file().write.assert_any_call("title: placeholder\n")
        mock_file().write.assert_any_call("description: placeholder\n")
        mock_file().write.assert_any_call("src: images/DSC_3106.jpg\n")
        mock_file().write.assert_any_call("details:\n")
        mock_file().write.assert_any_call("  Make: NIKON CORPORATION\n")
        mock_file().write.assert_any_call("  Model: NIKON D750\n")
        mock_file().write.assert_any_call("  DateTimeOriginal: 2021:09:01 12:00:00\n")
        mock_file().write.assert_any_call("---\n")


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "photo_info.toml"
        self.runner = CliRunner()

    def tearDown(self):
        """Clean up test fixtures."""
        if self.config_path.exists():
            self.config_path.unlink()
        os.rmdir(self.temp_dir)

    @patch("photo_info.cli.Config")
    def test_process_with_config(self, mock_config):
        """Test process command with config file."""
        mock_config_instance = mock_config.return_value
        mock_config_instance.validate.return_value = True
        mock_config_instance.image_dir = Path("/test/images")
        mock_config_instance.markdown_dir = Path("/test/markdown")

        with patch("photo_info.cli.photo_info.identify_new_images") as mock_identify:
            mock_identify.return_value = []
            result = self.runner.invoke(app, ["process"])
            self.assertEqual(result.exit_code, 0)

    @patch("photo_info.cli.Config")
    def test_process_with_invalid_config(self, mock_config):
        """Test process command with invalid config."""
        mock_config_instance = mock_config.return_value
        mock_config_instance.validate.return_value = False

        result = self.runner.invoke(app, ["process"])
        self.assertEqual(result.exit_code, 1)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    def test_init_command(self, mock_write, mock_exists):
        """Test init command."""
        mock_exists.return_value = False
        result = self.runner.invoke(app, ["init"])
        self.assertEqual(result.exit_code, 0)
        mock_write.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    def test_init_command_existing_file(self, mock_write, mock_exists):
        """Test init command with existing config file."""
        mock_exists.return_value = True
        result = self.runner.invoke(app, ["init"])
        self.assertEqual(result.exit_code, 1)
        mock_write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
