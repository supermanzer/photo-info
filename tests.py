import unittest
from unittest.mock import patch, mock_open, MagicMock
from photo_info import (
    get_exif_data,
    get_labeled_exif,
    write_to_markdown,
    MY_TAGS,
    identify_new_images,
)
from PIL import Image


class TestPhotoInfo(unittest.TestCase):

    @patch("photo_info.Image.open")
    def test_get_exif_data(self, mock_open):
        mock_image = MagicMock()
        mock_image._getexif.return_value = {271: "NIKON CORPORATION", 272: "NIKON D750"}
        mock_open.return_value = mock_image

        exif_data = get_exif_data("test_files/DSC_3106.jpg")
        self.assertEqual(exif_data[271], "NIKON CORPORATION")
        self.assertEqual(exif_data[272], "NIKON D750")

    def test_get_labeled_exif(self):
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
        image_dir = "test_files/"
        md_dir = "test_files/"
        new_images = ["DSC_3021"]
        with patch("os.listdir") as mock_listdir:
            mock_listdir.side_effect = [
                ["DSC_3021.jpg", "DSC_3106.jpg"],
                ["DSC_3106.md"],
            ]
            found_images = identify_new_images(image_dir, md_dir)
            self.assertEqual(found_images, new_images)

    @patch("builtins.open", new_callable=mock_open)
    def test_write_to_markdown(self, mock_file):
        labeled_exif = {
            "Make": "NIKON CORPORATION",
            "Model": "NIKON D750",
            "DateTimeOriginal": "2021:09:01 12:00:00",
        }
        write_to_markdown("test_files/DSC_3106.jpg", labeled_exif, "test_files/")
        mock_file.assert_called_once_with(
            "test_files/DSC_3106.md", "w+", encoding="utf-8"
        )
        mock_file().write.assert_any_call("---\n")
        mock_file().write.assert_any_call("title: placeholder\n")
        mock_file().write.assert_any_call("description: placeholder\n")
        mock_file().write.assert_any_call("details:\n")
        mock_file().write.assert_any_call("\tMake: NIKON CORPORATION\n")
        mock_file().write.assert_any_call("\tModel: NIKON D750\n")
        mock_file().write.assert_any_call("\tDateTimeOriginal: 2021:09:01 12:00:00\n")
        mock_file().write.assert_any_call("---\n")


if __name__ == "__main__":
    unittest.main()
