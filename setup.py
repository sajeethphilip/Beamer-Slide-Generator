from setuptools import setup
import os
import glob

# Get long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from a variable (no external file needed)
version = "2.8"

setup(
    name="bsg_ide",
    version=version,
    author="Ninan Sajeeth Philip",
    author_email="nsp@airis4d.com",
    description="Beamer Slide Generator IDE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sajeethphilip/Beamer-Slide-Generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
    python_requires='>=3.7',

    # Explicitly list modules
    py_modules=["BSG_IDE", "BeamerSlideGenerator"],

    # Entry point
    entry_points={
        'console_scripts': [
            'bsg-ide=BSG_IDE:main',
        ],
    },

    # Dependencies
    install_requires=[
        "customtkinter==5.2.2",
        "Pillow",
        "requests",
        "yt_dlp",
        "opencv-python",
        "screeninfo",
        "numpy",
        "PyMuPDF==1.23.7"
    ],

    # Include data files
    include_package_data=True,
    package_data={
        '': [
            'LICENSE',
            'README.md',
            'requirements.txt',
            'icons/*.png',
            'resources/*.png',
            '*.png'
        ],
    },

    # Ensure data files are included in sdist
    data_files=[
        ('', ['LICENSE', 'README.md', 'requirements.txt']),
        ('icons', glob.glob('icons/*.png')),
        ('resources', glob.glob('resources/*.png')),
    ]
)
