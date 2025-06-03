from setuptools import setup, find_packages
import os

# Read README file safely
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Beamer Slide Generator IDE"

setup(
    name="bsg-ide",
    version="2.4.4",
    packages=find_packages(),
    install_requires=[
        "customtkinter==5.2.2",
        "Pillow",
        "tk",
        "requests",
        "yt_dlp",
        "opencv-python",
        "screeninfo",
        "numpy",
        "PyMuPDF==1.23.7"
    ],
    entry_points={
        'console_scripts': [
            'bsg-ide=bsg_ide.BSG_IDE:main',
        ],
    },
    package_data={
        'bsg_ide': [
            'icons/*.png',
            'resources/*.png',
            '*.png',
            'requirements.txt',
            'BeamerSlideGenerator.py',
            'BSG_IDE.py'
        ],
    },
    include_package_data=True,
    author="Ninan Sajeeth Philip",
    author_email="nsp@airis4d.com",
    description="Beamer Slide Generator IDE",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sajeethphilip/Beamer-Slide-Generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    # Explicitly specify metadata version
    metadata_version='2.1',
)
