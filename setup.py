#!/usr/bin/env python3
"""
Setup script for BSG-IDE package
"""
from setuptools import setup, find_packages
from pathlib import Path
import os
import sys
import shutil

def copy_required_files():
    """Copy required Python files to package directory"""
    package_dir = Path('bsg_ide')
    package_dir.mkdir(exist_ok=True)

    # Create __init__.py if it doesn't exist
    init_file = package_dir / '__init__.py'
    if not init_file.exists():
        init_file.write_text("""
__version__ = '1.0.0'

# Import all functions from generator module (BeamerSlideGenerator)
from .generator import *

# Import main application
from .main import main

# Optional import for ODP conversion
try:
    from .odp import BeamerToODP
except ImportError:
    pass
""")

    # Copy and rename required files
    files_to_copy = {
        'BSG-IDE.py': 'main.py',
        'BeamerSlideGenerator.py': 'generator.py',
        'Beam2odp.py': 'odp.py'
    }

    for src, dest in files_to_copy.items():
        src_path = Path(src)
        if src_path.exists():
            shutil.copy2(src_path, package_dir / dest)
            print(f"Copied {src} to {dest}")
        else:
            print(f"Warning: {src} not found")

    # Ensure icons directory exists
    icons_dir = package_dir / 'icons'
    icons_dir.mkdir(exist_ok=True)

def create_readme():
    """Create README.md if it doesn't exist"""
    readme_content = """# BSG-IDE (Beamer Slide Generator IDE)

An integrated development environment for creating Beamer presentations with multimedia support.

## Features

- Easy-to-use GUI interface
- Support for multimedia content including videos and images
- YouTube video integration
- Notes management
- PDF preview
- Overleaf export capability
- Automatic desktop integration

## Installation

```bash
pip install bsg-ide
```

## Usage

After installation, you can launch BSG-IDE in two ways:

1. From command line:
   ```bash
   bsg-ide
   ```
   or
   ```bash
   bsg-ide-gui
   ```

2. Through your system's application menu (look under Office or Development category)

## Dependencies

- LaTeX with Beamer class
- Python 3.6 or higher
- Required Python packages (automatically installed):
  - customtkinter
  - Pillow
  - requests
  - yt_dlp
  - opencv-python

## License

Creative Commons License

## Author

Ninan Sajeeth Philip (nsp@airis4d.com)

## Support

For issues and feature requests, please visit:
https://github.com/sajeethphilip/Beamer-Slide-Generator
"""

    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_manifest():
    """Create MANIFEST.in"""
    manifest_content = """include README.md
include LICENSE
recursive-include bsg_ide *.py
recursive-include bsg_ide/icons *.png
"""
    with open("MANIFEST.in", 'w', encoding='utf-8') as f:
        f.write(manifest_content)

def main():
    """Main setup process"""
    # First copy all required files
    copy_required_files()

    # Create necessary files
    create_readme()
    create_manifest()

    # Setup configuration
    setup(
        name="bsg-ide",
        version="1.0.0",
        author="Ninan Sajeeth Philip",
        author_email="nsp@airis4d.com",
        description="Beamer Slide Generator IDE",
        long_description=Path("README.md").read_text(encoding='utf-8'),
        long_description_content_type="text/markdown",
        url="https://github.com/sajeethphilip/Beamer-Slide-Generator",

        # Package configuration
        packages=find_packages(),
        include_package_data=True,
        package_data={
            'bsg_ide': [
                'icons/*.png',
                'generator.py',
                'main.py',
                'odp.py',
            ],
        },

        # Dependencies
        install_requires=[
            'customtkinter',
            'Pillow',
            'requests',
            'yt_dlp',
            'opencv-python',
        ],

        # Entry points
        entry_points={
            'console_scripts': [
                'bsg-ide=bsg_ide.main:main',
            ],
            'gui_scripts': [
                'bsg-ide-gui=bsg_ide.main:main',
            ],
        },

        # Classifiers
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: X11 Applications",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Education",
            "Topic :: Office/Business :: Presentation",
            "Topic :: Text Processing :: Markup :: LaTeX",
        ],

        # Python version requirement
        python_requires='>=3.6',

        # Additional metadata
        keywords='beamer latex presentation slides multimedia education',
        project_urls={
            'Bug Reports': 'https://github.com/sajeethphilip/Beamer-Slide-Generator/issues',
            'Source': 'https://github.com/sajeethphilip/Beamer-Slide-Generator',
        },
    )

if __name__ == "__main__":
    main()
