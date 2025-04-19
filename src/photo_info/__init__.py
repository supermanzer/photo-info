"""Source package for Photo Info project."""

# photo_info/__init__.py

from photo_info.photo_info import (
    get_exif_data,
    get_labeled_exif,
    write_to_markdown,
    identify_new_images,
    MY_TAGS,
)

__app_name__ = "Photo Info"
__version__ = "0.1.0"
