# Photo Info
_A program for extracting information from image files (JPEG, NEF, etc)._

---

## Goal
The purpose of this application is to read the metadata from an image file and save that information as front-matter in a markdown file.  

This is intended to fasciliate using Markdown based web frameworks (e.g. [Nuxt Contet](https://content.nuxt.com/)) to share and display images.

## Installation

```bash
pip install -e .
```

## Usage

Photo Info can be used either with command-line arguments or with a configuration file.

### Using the Configuration File

1. Initialize a new configuration file in your project directory:
   ```bash
   photo-info init
   ```
   This creates a `photo_info.toml` file with default settings.

2. Edit the configuration file:
   ```toml
   # Photo Info Configuration

   [paths]
   # Paths can be absolute or relative to this config file
   images = "images"     # Directory containing images to process
   markdown = "markdown" # Directory where markdown files will be saved
   ```

   The configuration file supports:
   - Absolute paths: `/full/path/to/directory`
   - Relative paths: `images` (relative to config file location)
   - Home directory expansion: `~/path/to/directory`

3. Process images using the config:
   ```bash
   photo-info process
   ```

### Command Line Usage

You can also specify directories directly via command line arguments:

```bash
photo-info process /path/to/images /path/to/markdown
```

To use a specific config file:
```bash
photo-info --config /path/to/config.toml process
```

### Configuration File Structure

The configuration file (`photo_info.toml`) uses TOML format and has the following structure:

```toml
[paths]
images = "path/to/images"     # Directory containing images to process
markdown = "path/to/markdown" # Directory where markdown files will be saved
```

#### Configuration Options:

- `paths.images`: Directory containing the images to process
  - Can be absolute or relative path
  - Must exist and be readable
  - Supports home directory expansion (`~`)

- `paths.markdown`: Directory where markdown files will be saved
  - Can be absolute or relative path
  - Must exist and be writable
  - Supports home directory expansion (`~`)

### Command Reference

- `photo-info init`: Create a new configuration file
- `photo-info process`: Process images using config file settings
- `photo-info --version`: Show version information
- `photo-info --help`: Show help message and available commands
