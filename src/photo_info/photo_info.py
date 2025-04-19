"""Business logic of the Photo Info application."""

# photo_info/photo_info.py

import os
import pdb
import sys
from PIL import Image
from PIL.ExifTags import TAGS

# Specify which EXIF tags to extract
MY_TAGS = [
    "Make",
    "Model",
    "DateTimeOriginal",
    "FocalLength",
    "FNumber",
    "ExposureTime",
    "ISOSpeedRatings",
    "ExposureBiasValue",
    "LensMake",
    "LensModel",
]


def get_exif_data(image_file: str) -> dict:
    """Get embedded EXIF data from image file.
    Args:
        image_file (str): Path to the image file.
    Returns:
        (dict) A dictionary containing the EXIF
        data extracted from the image.
    """
    image = Image.open(image_file)
    image.verify()
    return image._getexif()


def get_labeled_exif(exif_data: dict) -> dict:
    """Get human-readable labels for EXIF data.

    Args:
        exif_data (dict): EXIF data extracted from the image.
    Returns:
        (dict) A dictionary containing the labeled EXIF data.
    """
    if exif_data is None:
        print("No EXIF data found")
        return {}

    labeled_exif = {
        TAGS.get(tag): value
        for tag, value in exif_data.items()
        if TAGS.get(tag) in MY_TAGS
    }
    return labeled_exif


def write_to_markdown(image_name: str, labeled_exif: dict, md_dir: str) -> None:
    """Write EXIF data to markdown file.

    Args:
        image_name (str): Path to the image file.
        labeled_exif (dict): Labeled EXIF data.
        md_dir (str): Path to the directory where the markdown file will be saved.
    Returns:
        None - Writes the markdown file to disk.
    """
    filename = md_dir + image_name.split("/")[-1].replace(".jpg", ".md")
    local_path_sections = image_name.split("/")
    try:
        public_index = local_path_sections.index("public")
        local_path = "/".join(local_path_sections[public_index + 1:])
    except ValueError:
        # If 'public' is not in path, use the filename only
        local_path = image_name.split("/")[-1]

    with open(filename, "w+", encoding="utf-8") as f:
        f.write("---\n")
        f.write("title: placeholder\n")
        f.write("description: placeholder\n")
        f.write("src: " + local_path + "\n")
        f.write("details:\n")
        for label, value in labeled_exif.items():
            value = str(value).rstrip("\x00")  # some values have trailing null bytes
            f.write(f"  {label}: {value}\n")
        f.write("---\n")


def identify_new_images(image_dir: str, md_dir: str) -> list:
    """Identify images that do not have a correspdoning markdown file.

    Args:
        image_dir (str): Path to the directory containing images.
        md_dir (str): Path to the directory containing markdown files.
    Returns:
        (list) A list of image names that do not have a corresponding markdown file.
    """
    images = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]
    mds = [f for f in os.listdir(md_dir) if f.endswith(".md")]
    image_names = [f.split(".")[0] for f in images]
    md_names = [f.split(".")[0] for f in mds]
    new_images = [f for f in image_names if f not in md_names]
    return new_images


def main():
    image_dir = sys.argv[1]
    md_dir = sys.argv[2]
    image_dir = image_dir if image_dir.endswith("/") else image_dir + "/"
    md_dir = md_dir if md_dir.endswith("/") else md_dir + "/"
    new_images = identify_new_images(image_dir, md_dir)
    for image_name in new_images:
        image_file = image_dir + image_name + ".jpg"
        exif_data = get_exif_data(image_file)
        labeled_exif = get_labeled_exif(exif_data)
        write_to_markdown(image_file, labeled_exif, md_dir)


if __name__ == "__main__":
    main()
