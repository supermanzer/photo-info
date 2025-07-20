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
        import shutil
        if self.image_dir.exists():
            shutil.rmtree(self.image_dir)
        if self.md_dir.exists():
            shutil.rmtree(self.md_dir)
        if os.path.exists(self.temp_dir):
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
        """Test identifying new images in root and nested directories."""
        # Create image files in root and nested directories
        img1 = self.image_dir / "DSC_3021.jpg"
        img2 = self.image_dir / "DSC_3106.jpg"
        nested_dir = self.image_dir / "2025"
        nested_dir.mkdir()
        img3 = nested_dir / "nested_img.jpg"
        img1.touch()
        img2.touch()
        img3.touch()

        # Create markdown file for img2 only (root)
        md2 = self.md_dir / "DSC_3106.md"
        md2.touch()
        # Create markdown file for img3 only (nested)
        nested_md_dir = self.md_dir / "2025"
        nested_md_dir.mkdir()
        md3 = nested_md_dir / "nested_img.md"
        md3.touch()

        found_images = identify_new_images(str(self.image_dir), str(self.md_dir))
        # Should only find img1.jpg (root, no .md)
        self.assertIn("DSC_3021.jpg", found_images)
        # Should not find img2.jpg or nested_img.jpg (they have .md files)
        self.assertNotIn("DSC_3106.jpg", found_images)
        self.assertNotIn(os.path.join("2025", "nested_img.jpg"), found_images)

    @patch("builtins.open", new_callable=mock_open)
    def test_write_to_markdown(self, mock_file):
        """Test writing EXIF data to markdown with nested structure."""
        labeled_exif = {
            "Make": "NIKON CORPORATION",
            "Model": "NIKON D750",
            "DateTimeOriginal": "2021:09:01 12:00:00",
        }
        # Test with a nested image path
        image_path = os.path.join("nested", "dir", "DSC_3106.jpg")
        md_dir = "test_files/"
        expected_md_path = os.path.join(md_dir, "nested", "dir", "DSC_3106.md")
        write_to_markdown(image_path, labeled_exif, md_dir)

        # Check that open was called for the expected markdown file
        open_calls = [call[0][0] for call in mock_file.call_args_list]
        self.assertIn(expected_md_path, open_calls)

        # Check that the markdown content was written
        handle = mock_file()
        handle.write.assert_any_call("---\n")
        handle.write.assert_any_call("title: placeholder\n")
        handle.write.assert_any_call("description: placeholder\n")
        handle.write.assert_any_call(f"src: {image_path}\n")
        handle.write.assert_any_call("details:\n")
        handle.write.assert_any_call("  Make: NIKON CORPORATION\n")
        handle.write.assert_any_call("  Model: NIKON D750\n")
        handle.write.assert_any_call("  DateTimeOriginal: 2021:09:01 12:00:00\n")
        handle.write.assert_any_call("---\n")


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
