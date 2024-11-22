#!/usr/bin/env python3
"""
BeamerSlideGenerator.py
A tool for generating Beamer presentation slides with multimedia content.
Supports local files, URL downloads, and content-only slides.
"""
import math
import os,re
import time
import requests
import webbrowser
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from urllib.parse import urlparse, unquote
from pathlib import Path
import mimetypes
output_dir = ""
#--------------------------------------------------------------------------------------------------------
def set_terminal_io(term_io):
    """Set the terminal I/O object and verify it's working"""
    global terminal_io
    terminal_io = term_io
    # Verify terminal_io is working
    if terminal_io:
        terminal_io.write("Terminal I/O initialized\n", "green")
#--------------------------------------------------------------------------------------------------------
def add_source_citation(content, source_note):
    """
    Adds source citation to content, either as new footnote or appending to existing one.
    """
    has_footnote = False
    for i, item in enumerate(content):
        if '\\footnote{' in item:
            # Append to existing footnote
            footnote_end = item.rindex('}')
            content[i] = f"{item[:footnote_end]}; {source_note}}}"
            has_footnote = True
            break

    if not has_footnote:
        # Add new footnote
        content.append(f"\\footnote{{\\tiny {source_note}}}")

def verify_required_packages(preamble_content: str) -> list:
    """
    Verify required packages are present in preamble.
    Returns list of missing packages.
    """
    required_packages = {
        'tikz': '\\usepackage{tikz}',
        'graphicx': '\\usepackage{graphicx}',
        'multimedia': '\\usepackage{multimedia}',
        'adjustbox': '\\usepackage[export]{adjustbox}',
        'pgfplots': '\\usepackage{pgfplots}',
        'calc': '\\usetikzlibrary{calc}',
        'overlay-beamer-styles': '\\usetikzlibrary{overlay-beamer-styles}'
    }

    missing = []
    for package, command in required_packages.items():
        if command not in preamble_content:
            missing.append(package)

    return missing

def generate_preview_frame(filepath, output_path=None):
    """
    Generates a preview frame for different media types.
    Returns the path to the preview image.
    """
    try:
        import cv2
        from PIL import Image
        import os

        # Default output path if none provided
        if output_path is None:
                global output_dir
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_path = os.path.join(output_dir, f"{base_name}_preview.png")
        # Get file extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        # Handle different media types
        if ext in ['.mp4', '.avi', '.mov', '.mkv']:
            # Video file
            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.save(output_path)
                cap.release()
                return output_path
        elif ext in ['.gif']:
            # Animated GIF - extract first frame
            with Image.open(filepath) as img:
                img.seek(0)
                img.save(output_path, 'PNG')
                return output_path
        elif ext in ['.mp3', '.wav', '.ogg']:
            # Audio file - create a simple icon
            img = Image.new('RGB', (400, 300), color='black')
            # You could draw a music note or audio symbol here
            img.save(output_path)
            return output_path
        elif ext in ['.png', '.jpg', '.jpeg']:
            # Static image - use as is
            return filepath

        return None
    except Exception as e:
        print(f"Error generating preview frame: {str(e)}")
        return None

def get_beamer_preamble(title, subtitle, author, institution, short_institute, date):
    """
    Returns the correct Beamer preamble with fixed brace matching and proper shadow text support
    """
    preamble = f"""\\documentclass[aspectratio=169]{{beamer}}
\\usepackage{{hyperref}}
\\usepackage{{graphicx}}
\\usepackage{{amsmath}}
\\usepackage{{tikz}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepackage{{animate}}
\\usepackage{{multimedia}}

% TikZ libraries for shadow effects
\\usetikzlibrary{{shadows.blur}}

% Custom command for shadowed text
\\newcommand{{\\shadowtext}}[2][2pt]{{%
    \\begin{{tikzpicture}}[baseline]
        \\node[blur shadow={{shadow blur steps=5,shadow xshift=0pt,shadow yshift=-#1,
              shadow opacity=0.75}}, text=white] {{#2}};
    \\end{{tikzpicture}}%
}}

% Glowing text effect
\\newcommand{{\\glowtext}}[2][myblue]{{%
    \\begin{{tikzpicture}}[baseline]
        \\node[circle, inner sep=1pt,
              blur shadow={{shadow blur steps=10,shadow xshift=0pt,
              shadow yshift=0pt,shadow blur radius=5pt,
              shadow opacity=0.5,shadow color=#1}},
              text=white] {{#2}};
    \\end{{tikzpicture}}%
}}

% Set up a dark theme
\\usetheme{{Madrid}}
\\usecolortheme{{owl}}

% Custom colors
\\definecolor{{myyellow}}{{RGB}}{{255,210,0}}
\\definecolor{{myorange}}{{RGB}}{{255,130,0}}
\\definecolor{{mygreen}}{{RGB}}{{0,200,100}}
\\definecolor{{myblue}}{{RGB}}{{0,130,255}}
\\definecolor{{mypink}}{{RGB}}{{255,105,180}}

% Colors for glow effects
\\definecolor{{glowblue}}{{RGB}}{{0,150,255}}
\\definecolor{{glowyellow}}{{RGB}}{{255,223,0}}
\\definecolor{{glowgreen}}{{RGB}}{{0,255,128}}

% Define new commands for highlighting
\\newcommand{{\\hlbias}}[1]{{\\textcolor{{myblue}}{{\\textbf{{#1}}}}}}
\\newcommand{{\\hlvariance}}[1]{{\\textcolor{{mypink}}{{\\textbf{{#1}}}}}}
\\newcommand{{\\hltotal}}[1]{{\\textcolor{{myyellow}}{{\\textbf{{#1}}}}}}

% Customize beamer colors
\\setbeamercolor{{normal text}}{{fg=white}}
\\setbeamercolor{{structure}}{{fg=myyellow}}
\\setbeamercolor{{alerted text}}{{fg=myorange}}
\\setbeamercolor{{example text}}{{fg=mygreen}}
\\setbeamercolor{{background canvas}}{{bg=black}}
\\setbeamercolor{{frametitle}}{{fg=white,bg=black}}

% Setup short institution name for footline if provided
\\makeatletter
\\def\\insertshortinstitute{{{short_institute if short_institute else institution}}}
\\makeatother

% Modify footline template to use short institution
\\setbeamertemplate{{footline}}{{%
  \\leavevmode%
  \\hbox{{%
    \\begin{{beamercolorbox}}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,center]{{author in head/foot}}%
      \\usebeamerfont{{author in head/foot}}\\insertshortauthor~~(\\insertshortinstitute)%
    \\end{{beamercolorbox}}%
    \\begin{{beamercolorbox}}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,center]{{title in head/foot}}%
      \\usebeamerfont{{title in head/foot}}\\insertshorttitle%
    \\end{{beamercolorbox}}%
    \\begin{{beamercolorbox}}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,right]{{date in head/foot}}%
      \\usebeamerfont{{date in head/foot}}\\insertshortdate{{}}\\hspace*{{2em}}%
      \\insertframenumber{{}} / \\inserttotalframenumber\\hspace*{{2ex}}%
    \\end{{beamercolorbox}}}}%
  \\vskip0pt%
}}

% Additional packages and settings
\\usepackage{{url}}
\\usepackage[export]{{adjustbox}}
\\usetikzlibrary{{shapes.geometric, positioning, arrows.meta, backgrounds, fit}}

% Redefine the frame to have smaller margins
\\setbeamersize{{text margin left=5pt,text margin right=5pt}}

% Centering frame titles
\\setbeamertemplate{{frametitle}}[default][center]

% Set the title
\\title{{{title}}}
{f'\\subtitle{{{subtitle}}}' if subtitle else ''}
\\author{{{author}}}
\\institute{{\\textcolor{{mygreen}}{{{institution}}}}}
\\date{{{date}}}

\\begin{{document}}

\\begin{{frame}}
\\titlepage
\\end{{frame}}

"""
    return preamble


def get_footline_template():
    """
    Returns the correct footline template for Beamer.
    """
    return """% Setup footline template with proper short institute handling
\\makeatletter
\\defbeamertemplate*{footline}{custom}
{
  \\leavevmode%
  \\hbox{%
    \\begin{beamercolorbox}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
      \\usebeamerfont{author in head/foot}\\insertshortauthor~(\\usebeamercolor[fg]{author in head/foot}\\insertshortinstitute)
    \\end{beamercolorbox}%
    \\begin{beamercolorbox}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
      \\usebeamerfont{title in head/foot}\\insertshorttitle
    \\end{beamercolorbox}%
    \\begin{beamercolorbox}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
      \\usebeamerfont{date in head/foot}\\insertshortdate{\\,}\\hspace*{2em}
      \\insertframenumber{} / \\inserttotalframenumber\\hspace*{2ex}
    \\end{beamercolorbox}}%
  \\vskip0pt%
}
\\setbeamertemplate{footline}[custom]
\\makeatother
"""
def format_url_footnote(url):
    """
    Formats URL footnotes appropriately.
    """
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return f"{{\\tiny {base_url} \\href{{{url}}}{{[link]}} }}"
    except:
        return f"{{\\tiny {url}}}"

def create_new_input_file(file_path):
    """
    Interactively creates a new input file with slide content and proper preamble.
    """
    global output_dir
    output_dir = os.path.dirname(os.path.abspath(file_path))
    os.chdir(output_dir)
    print("\nPresentation Setup:")
    print("-----------------")
    title = input("Title: ").strip()
    subtitle = input("Subtitle (press Enter to skip): ").strip()
    author = input("Author Name: ").strip()
    institution = input("Institution: ").strip()

    # Ask for short institution name if the institution name is long
    if len(institution) > 50:  # threshold for suggesting short name
        print("\nYour institution name is quite long and might get trimmed in slides.")
        print("It's recommended to provide a shorter version for the slide footers.")
        short_institute = input("Short Institution Name (press Enter to skip): ").strip()
    else:
        short_institute = input("Short Institution Name (optional, press Enter to skip): ").strip()

    date = input("Date (press Enter for today): ").strip()
    if not date:
        date = "\\today"

    # Get the preamble using the helper function
    preamble = get_beamer_preamble(title, subtitle, author, institution, short_institute, date)

    print(f"\nCreating new input file: {file_path}")
    print("Enter empty line at Title prompt to finish.")

    slides = []
    slide_num = 1

    while True:
        print(f"\n[Slide{slide_num}] Title: ", end='')
        title = input().strip()
        if not title:
            break

        # Handle URL/Media
        print(f"[Slide{slide_num}] Media selection:")
        search_query = construct_search_query(title, [])
        print(f"Opening Google Image search for: {search_query}")
        open_google_image_search(search_query)

        print("\nPlease choose one of the following options:")
        print("1. Enter a URL")
        print("2. Use an existing file from media_files folder")
        print("3. Create slide without media")
        choice = input("Your choice (1/2/3): ").strip()

        url = None
        if choice == '1':
            url = input("Enter URL: ").strip()
        elif choice == '2':
            print("\nAvailable files in media folder:")
            media_dir = os.path.join(os.path.dirname(os.path.abspath(file_path)), 'media')
            try:
                files = os.listdir(media_dir)
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")
                file_choice = input("Enter file number or name: ").strip()
                if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                    chosen_file = files[int(file_choice) - 1]
                else:
                    chosen_file = file_choice
                url = f"\\file {{./media/{chosen_file}}}"
            except Exception as e:
                print(f"Error accessing media_files: {str(e)}")
                url = "\\None"
        else:
            url = "\\None"

        # Collect content items
        print(f"\n[Slide{slide_num}] Content (enter empty line to finish):")
        content = []
        while True:
            item = input("- ").strip()
            if not item:
                break

            # Check if the item contains a footnote
            if "\\footnote{" in item:
                content.append(item)  # Add as is, footnote is already properly formatted
            else:
                content.append(f"- {item}")

        # Optional footnote for the entire slide
        print(f"\n[Slide{slide_num}] Footnote (press Enter to skip): ", end='')
        footnote = input().strip()

        # Build slide content
        slide_content = [f"\\title {title}"]
        slide_content.append("\\begin{Content}" + (f" {url}" if url else ""))
        slide_content.extend(content)

        # Add footnote if provided and content exists
        if footnote:
            if footnote.startswith(('http://', 'https://')):
                footnote = format_url_footnote(footnote)
            else:
                footnote = f"{{\\tiny {footnote}}}"

            if content:  # Only add footnote if there's content
                last_content_line = slide_content[-1]
                if not "\\footnote{" in last_content_line:
                    slide_content[-1] = f"{last_content_line}\\footnote{footnote}"

        slide_content.append("\\end{Content}")
        slide_content.append("")  # Empty line between slides

        slides.append("\n".join(slide_content))
        slide_num += 1

    if slides:
        try:
            with open(file_path, 'w') as f:
                f.write(preamble)  # Write preamble first
                f.write("\n".join(slides))  # Write slides
                f.write("\n\\end{document}")  # End the document
            print(f"\nSuccessfully created {file_path} with {slide_num-1} slides.")
            return True
        except Exception as e:
            print(f"Error creating file: {str(e)}")
            return False
    else:
        print("\nNo slides created.")
        return False

def detect_preamble(lines):
    """
    Detects if the input file has a complete preamble by checking for key commands.
    Now also checks for short institution name.
    """
    has_author = False
    has_institute = False
    has_title = False
    has_begin_document = False
    has_titlepage = False
    has_maketitle = False
    has_short_institute = False
    preamble_end_idx = -1

    for i, line in enumerate(lines):
        line = line.strip()
        if '\\author{' in line:
            has_author = True
        if '\\institute{' in line:
            has_institute = True
        if '\\instituteShort{' in line or '\\def\\insertshortinstitute{' in line:
            has_short_institute = True
        if '\\title{' in line and not line.startswith('\\title '):
            has_title = True
        if '\\begin{document}' in line:
            has_begin_document = True
            preamble_end_idx = i
            break

    # If we have a long institution name but no short version, suggest adding one
    if has_institute and not has_short_institute:
        # Find the institution line to check its length
        for line in lines[:preamble_end_idx] if preamble_end_idx >= 0 else lines:
            if '\\institute{' in line:
                inst_text = line[line.find('{')+1:line.rfind('}')]
                if len(inst_text) > 50:  # threshold for suggesting short name
                    print("\nWarning: Long institution name detected.")
                    print("Consider adding a short version using \\instituteShort{} or modifying the footline template.")
                break

    # Check for titlepage and maketitle after \begin{document}
    if preamble_end_idx >= 0:
        for i in range(preamble_end_idx + 1, min(preamble_end_idx + 10, len(lines))):
            if '\\titlepage' in lines[i]:
                has_titlepage = True
            if '\\maketitle' in lines[i]:
                has_maketitle = True

    has_preamble = has_author and has_institute and has_title and has_begin_document

    if has_preamble:
        preamble_lines = lines[:preamble_end_idx + 1]
        content_lines = lines[preamble_end_idx + 1:]
    else:
        preamble_lines = []
        content_lines = lines

    return has_preamble, preamble_lines, content_lines, has_titlepage, has_maketitle
#---------------------------------------------------------------------------------------------------------

def sanitize_filename(filename, max_length=50):
    """
    Sanitizes a filename for safe use in file systems.
    """
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    filename = ''.join(c if c not in unsafe_chars else '_' for c in filename)

    # Keep only alphanumeric characters, spaces, dots, and underscores
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._-')
    filename = ''.join(c if c in safe_chars else '_' for c in filename)

    # Replace multiple spaces/underscores with single ones
    while '__' in filename:
        filename = filename.replace('__', '_')

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Remove dots from the beginning
    filename = filename.lstrip('.')

    # Limit length while preserving extension
    name, ext = os.path.splitext(filename)
    if len(name) > max_length:
        name = name[:max_length]
    filename = name + ext

    # If filename is empty after sanitization, use a default name
    if not filename or filename == '.':
        filename = 'video.mp4'

    return filename

def validate_url(url):
    """
    Validates a URL and provides specific error messages.
    Now handles file and None directives.
    """
    if url.startswith(('\\file', '\\None', '\\play')):
        return True, "Local file or directive reference"

    try:
        # Remove any leading/trailing whitespace and directives
        cleaned_url = url.split()[-1] if url.split() else url

        # Check if URL is accessible
        response = requests.head(cleaned_url, timeout=5)
        if response.status_code == 403:
            return False, "Access Forbidden - This URL requires authentication or is not publicly accessible"
        elif response.status_code == 404:
            return False, "Resource Not Found - The URL may be incorrect or the content may have been moved"
        elif response.status_code != 200:
            return False, f"URL returned status code {response.status_code}"
        return True, "URL is valid"
    except requests.exceptions.Timeout:
        return False, "URL request timed out"
    except requests.exceptions.RequestException as e:
        return False, f"Error accessing URL: {str(e)}"

def construct_search_query(title, content):
    """
    Constructs a Google search query from title and content.
    """
    search_terms = [title] if title else []
    if isinstance(content, list) and content:
        # Add first non-empty content item to search terms
        search_terms.extend([item.strip('- ') for item in content[:1] if item.strip('- ')])

    # Add relevant keywords based on context
    search_terms.append("scientific diagram")
    if "hopfield" in ' '.join(search_terms).lower():
        search_terms.append("neural network")
    elif "quantum" in ' '.join(search_terms).lower():
        search_terms.append("computing")

    return ' '.join(search_terms)

def open_google_image_search(query):
    """
    Opens Google Image search in default browser.
    """
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    webbrowser.open(search_url)

def download_giphy_gif(url, output_folder='media_files'):
    """
    Special handling for Giphy URLs to get the actual GIF.
    """
    try:
        # Extract the GIF ID from the URL
        gif_id = url.split('/')[-1].split('-')[-1]
        # Construct direct gif URL
        direct_url = f"https://media.giphy.com/media/{gif_id}/giphy.gif"
        return download_media(direct_url, output_folder)
    except Exception as e:
        print(f"Error processing Giphy URL: {str(e)}")
        return None, None, None

def download_media(url, output_folder='media_files'):
    """
    Enhanced version with source tracking.
    """
    try:
        if url.startswith('local:'):
            local_file = url.split('local:')[1].strip()
            if os.path.exists(os.path.join(output_folder, local_file)):
                base_name = os.path.splitext(local_file)[0]
                return base_name, local_file, local_file
            return None, None, None

        if 'giphy.com' in url:
            return download_giphy_gif(url, output_folder)

        response = requests.get(url, timeout=10)
        response.raise_for_status()


        # Store source URL in a metadata file
        if base_name and filename:
            metadata_path = os.path.join(output_folder, f"{base_name}_metadata.txt")
            with open(metadata_path, 'w') as f:
                f.write(f"Source: {url}\n")
                f.write(f"Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        return base_name, filename, first_frame_path
    except Exception as e:
        print(f"Error downloading media from {url}: {str(e)}")
        return None, None, None


def process_latex_content(content_line: str) -> str:
    """
    Process content line to properly handle LaTeX math expressions,
    ensuring underscores work correctly as subscripts in math mode.
    Also handles other LaTeX commands and special characters.
    """
    if not content_line:
        return content_line

    result = []
    in_math = False
    in_command = False
    brace_level = 0
    i = 0

    while i < len(content_line):
        char = content_line[i]

        # Handle math mode transitions
        if char == '$':
            in_math = not in_math
            result.append(char)
            i += 1
            continue

        # Handle LaTeX commands
        if char == '\\' and i + 1 < len(content_line):
            next_char = content_line[i + 1]
            if next_char.isalpha() or next_char in ['[', ']', '$', '{', '}', '_', '^', '%', '&', '#', ' ']:
                result.extend(['\\', next_char])
                i += 2
                continue

        # Handle braces
        if char == '{':
            brace_level += 1
            result.append(char)
            i += 1
            continue
        elif char == '}':
            brace_level -= 1
            result.append(char)
            i += 1
            continue

        # Process characters based on context
        if in_math or brace_level > 0:
            # In math mode or within braces, preserve everything
            result.append(char)
        else:
            # Outside math mode, escape special characters
            if char == '_':
                result.append('\\_')
            elif char == '&':
                result.append('\\&')
            elif char == '#':
                result.append('\\#')
            elif char == '%':
                result.append('\\%')
            elif char == '~':
                result.append('\\textasciitilde{}')
            elif char == '^':
                result.append('\\textasciicircum{}')
            else:
                result.append(char)
        i += 1

    return ''.join(result)

def generate_latex_code(base_name, filename, first_frame_path, content=None, title=None, playable=False, source_url=None, layout=None):
    """Generate LaTeX code with support for all media layouts."""

    # Process title
    if title:
        frame_title = process_latex_content(title)
    else:
        base_name_escaped = process_latex_content(base_name if base_name else 'Untitled')
        frame_title = f"Media: {base_name_escaped}"

    # Handle no media case first
    if not filename or filename == "\\None":
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\vspace{{0.5em}}
    \\begin{{itemize}}
        {generate_content_items(content)}
    \\end{{itemize}}
\\end{{frame}}\n"""
        return latex_code

    # Generate layout based on directive
    latex_code = ""

    if layout == 'watermark':
        latex_code = f"""\\begin{{frame}}{{{frame_title if title else ''}}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[opacity=0.15] at (current page.center) {{%
            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{filename}}}%
        }};
    \\end{{tikzpicture}}
    \\begin{{itemize}}
        {generate_content_items(content)}
    \\end{{itemize}}"""

    elif layout == 'fullframe':
        latex_code = f"""\\begin{{frame}}[plain]
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node at (current page.center) {{%
            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{filename}}}%
        }};
        \\node[text width=0.8\\paperwidth,align=center,text=white] at (current page.center) {{
            \\Large\\textbf{{{frame_title}}}\\\\[1em]
            \\begin{{itemize}}
                {generate_content_items(content, color='white')}
            \\end{{itemize}}
        }};
    \\end{{tikzpicture}}"""

    elif layout == 'pip':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{columns}}[T]
        \\begin{{column}}{{0.7\\textwidth}}
            \\begin{{itemize}}
                {generate_content_items(content)}
            \\end{{itemize}}
        \\end{{column}}
        \\begin{{column}}{{0.28\\textwidth}}
            \\vspace{{1em}}
            \\includegraphics[width=\\textwidth,keepaspectratio]{{{filename}}}
        \\end{{column}}
    \\end{{columns}}"""

    elif layout == 'split':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{columns}}[T]
        \\begin{{column}}{{0.48\\textwidth}}
            \\includegraphics[width=\\textwidth,keepaspectratio]{{{filename}}}
        \\end{{column}}
        \\begin{{column}}{{0.48\\textwidth}}
            \\begin{{itemize}}
                {generate_content_items(content)}
            \\end{{itemize}}
        \\end{{column}}
    \\end{{columns}}"""

    elif layout == 'highlight':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{center}}
        \\includegraphics[width=0.8\\textwidth,height=0.6\\textheight,keepaspectratio]{{{filename}}}
    \\end{{center}}
    \\vspace{{0.5em}}
    \\begin{{itemize}}
        {generate_content_items(content)}
    \\end{{itemize}}"""

    elif layout == 'background':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[opacity=0.1] at (current page.center) {{%
            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{filename}}}%
        }};
    \\end{{tikzpicture}}
    \\begin{{itemize}}
        {generate_content_items(content)}
    \\end{{itemize}}"""

    elif layout == 'topbottom':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\vspace{{-0.5em}}
    \\begin{{center}}
        \\includegraphics[width=0.8\\textwidth,height=0.45\\textheight,keepaspectratio]{{{filename}}}
    \\end{{center}}
    \\vspace{{0.5em}}
    \\begin{{itemize}}
        {generate_content_items(content)}
    \\end{{itemize}}"""

    elif layout == 'overlay':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[opacity=0.3] at (current page.center) {{%
            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{filename}}}%
        }};
        \\node[text width=0.8\\paperwidth,align=center,text=white] at (current page.center) {{
            \\begin{{itemize}}
                {generate_content_items(content, color='white')}
            \\end{{itemize}}
        }};
    \\end{{tikzpicture}}"""

    elif layout == 'corner':
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{itemize}}
        {generate_content_items(content)}
    \\end{{itemize}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[anchor=south east] at (current page.south east) {{%
            \\includegraphics[width=0.2\\textwidth,keepaspectratio]{{{filename}}}%
        }};
    \\end{{tikzpicture}}"""

    elif layout == 'mosaic':
        images = [img.strip() for img in filename.split(',')]
        # Calculate grid dimensions based on number of images
        grid_size = int(math.ceil(math.sqrt(len(images))))  # Square root rounded up
        rows = grid_size+1
        cols = grid_size+1
        print(rows,cols)
        latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
        \\begin{{center}}
        \\begin{{tikzpicture}}
           \\matrix [column sep=0.2cm, row sep=0.2cm] {{"""

        for i in range(rows):
           for j in range(cols):
               idx = i * cols + j
               if idx < len(images):
                   latex_code += f"""
               \\node {{ \\includegraphics[width={0.8/grid_size}\\textwidth,height={0.7/grid_size}\\textheight,keepaspectratio]{{{images[idx]}}} }}; """
                   if j < cols - 1:
                       latex_code += "&"
           latex_code += "\\\\"

        latex_code += """
        };
    \\end{tikzpicture}
    \\end{center}"""
        if content:
            latex_code += """
    \\vspace{0.5em}
    \\begin{itemize}
        """ + generate_content_items(content) + """
    \\end{itemize}"""

    else:
        # Default side-by-side layout for standard media
        if playable and first_frame_path:
            latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{columns}}[T]
        \\begin{{column}}{{0.48\\textwidth}}
            \\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{{{first_frame_path}}}
            \\begin{{center}}
                \\vspace{{0.3em}}
                \\footnotesize{{Click to play}}\\\\
                \\movie[externalviewer]{{\\textcolor{{blue}}{{\\underline{{Play}}}}}}{{{filename}}}
            \\end{{center}}
        \\end{{column}}
        \\begin{{column}}{{0.48\\textwidth}}
            \\begin{{itemize}}
                {generate_content_items(content)}
            \\end{{itemize}}
        \\end{{column}}
    \\end{{columns}}"""
        else:
            latex_code = f"""\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\begin{{columns}}[T]
        \\begin{{column}}{{0.48\\textwidth}}
            \\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{{{filename}}}
        \\end{{column}}
        \\begin{{column}}{{0.48\\textwidth}}
            \\begin{{itemize}}
                {generate_content_items(content)}
            \\end{{itemize}}
        \\end{{column}}
    \\end{{columns}}"""

    # Add source citation if available
    if source_url:
        latex_code += generate_source_citation(source_url)

    latex_code += "\n\\end{frame}\n"
    return latex_code

def generate_source_citation(source_url):
    """Generate LaTeX code for source citation"""
    return f"""
    \\vspace{{0.3em}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[anchor=south,font=\\tiny] at (current page.south) {{
            Source: \\url{{{source_url}}}
        }};
    \\end{{tikzpicture}}"""

def generate_content_items(content, color=None):
    """Generate formatted content items with optional color"""
    if not content:
        return ""

    items = []
    for item in content:
        if item.strip():
            item = str(item).strip()
            if item.startswith('-'):
                item = item[1:].strip()
            processed_item = process_latex_content(item)
            if color:
                processed_item = f"{{\\color{{{color}}}{processed_item}}}"
            items.append(f"\\item {processed_item}")

    return '\n        '.join(items)

def format_source_citation(url):
    """
    Format source URLs for citation with proper LaTeX escaping.
    """
    try:
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            return f"YouTube video: \\url{{{url}}}"
        elif 'github.com' in parsed.netloc:
            return f"GitHub repository: \\url{{{url}}}"
        else:
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            return f"Source: {base_url} \\url{{{url}}}"
    except:
        return f"Source: {url}"

def process_content_items(content_items):
    """Process content items with proper None handling"""
    processed_items = []
    if content_items:
        for item in content_items:
            if item:  # Check if item is not None and not empty
                # Ensure item starts with bullet point if needed
                if not str(item).strip().startswith('-'):
                    item = f"- {str(item).strip()}"
                # Process the content
                processed_item = process_latex_content(item)
                processed_items.append(processed_item)
    return processed_items


def add_source_citation(content, source_note):
    """
    Modified to handle only non-media citations.
    """
    # Only add citations that aren't media sources
    if not source_note.startswith('Source: http'):
        has_footnote = False
        for i, item in enumerate(content):
            if '\\footnote{' in item:
                footnote_end = item.rindex('}')
                content[i] = f"{item[:footnote_end]}; {source_note}}}"
                has_footnote = True
                break

        if not has_footnote:
            content.append(f"\\footnote{{\\tiny {source_note}}}")

def verify_media_file(filepath):
    """
    Verifies that a media file exists and returns its proper path.
    """
    if os.path.exists(filepath):
        return filepath

    base_filepath = os.path.join('media_files', os.path.basename(filepath))
    if os.path.exists(base_filepath):
        return base_filepath

    # Try to find the file with any extension
    global output_dir
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_dir = os.path.dirname(os.path.abspath(file_path))  # Get the directory of the input file
    base_path = os.path.join(output_dir,'media_files', base_name)
    import glob
    possible_files = glob.glob(base_path + '.*')
    if possible_files:
        return possible_files[0]

    print(f"Warning: Media file not found: {filepath}")
    return None

def process_media(url, content=None, title=None, playable=False, slide_index=None, callback=None):
    """Process media with graceful handling of missing files"""
    try:
        directive_type, media_source, is_playable, original_directive = parse_media_directive(url)
        playable = playable or is_playable
        source_url = None

        # Handle empty/None case
        if not url or not directive_type:
            return handle_missing_media(url, content, title, playable)

        # Handle explicit \None directive
        if url.strip() == "\\None":
            return generate_latex_code(None, "\\None", None, content, title, False), "\\None"

        # Check if media file exists for file directives
        if directive_type == 'file':
            media_path = media_source
            if not os.path.exists(media_path):
                media_path = os.path.join('media_files', os.path.basename(media_path))
                if not os.path.exists(media_path):
                    # Skip web search and prompts in GUI mode
                    return handle_missing_media(url, content, title, playable)

            media_source = media_path

        # For URL type, skip web search if in GUI mode
        if directive_type == 'url' and terminal_io and hasattr(terminal_io, 'editor'):
            if not media_source or not media_source.startswith(('http://', 'https://')):
                return handle_missing_media(url, content, title, playable)

        # Generate LaTeX code
        latex_code = generate_latex_code(
            os.path.splitext(os.path.basename(media_source))[0] if media_source else None,
            media_source,
            None,
            content,
            title,
            playable,
            source_url,
            directive_type
        )

        return latex_code, original_directive

    except Exception as e:
        print(f"Error processing media: {str(e)}")
        return handle_missing_media(url, content, title, playable)


def update_text_file(file_path, line_number, new_directive):
    """Update the text file with new directive"""
    if not file_path or not line_number:
        return

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Find the correct position to insert the directive
        if line_number - 1 < len(lines):
            current_line = lines[line_number - 1].strip()

            # Check if the line starts with \begin{Content}
            if current_line.startswith("\\begin{Content}"):
                # Replace everything after \begin{Content} or add new directive
                lines[line_number - 1] = f"\\begin{{Content}} {new_directive}\n"
            else:
                # Replace the entire line
                lines[line_number - 1] = f"{new_directive}\n"

            # Write the updated content back to file
            with open(file_path, 'w') as f:
                f.writelines(lines)

            if terminal_io:
                terminal_io.write(f"✓ File updated successfully at line {line_number}\n", "green")

    except Exception as e:
        if terminal_io:
            terminal_io.write(f"Error updating file: {str(e)}\n", "red")


def handle_missing_media(original_url, content, title, playable):
    """Handle missing media gracefully in GUI mode by defaulting to \\None"""
    try:
        # Check if we're in GUI mode (IDE)
        in_gui_mode = terminal_io and hasattr(terminal_io, 'editor')

        if in_gui_mode:
            # In GUI mode, silently default to \None
            latex_code = generate_latex_code(None, "\\None", None, content, title, False)
            return latex_code, ("\\None", "\\None")
        else:
            # In terminal mode, use the original interactive behavior
            return handle_missing_media_fallback(original_url, content, title, playable)

    except Exception as e:
        print(f"Error handling missing media: {str(e)}")
        # Default to \None in case of any error
        latex_code = generate_latex_code(None, "\\None", None, content, title, False)
        return latex_code, ("\\None", "\\None")




def handle_missing_media_fallback(original_url, content, title, playable):
    """
    Original implementation using standard I/O for fallback.
    Returns tuple of (latex_code, directives) where directives can be a single string or tuple of (tex_directive, text_directive)
    """
    search_query = construct_search_query(title, content)
    print(f"\nOpening Google Image search for: {search_query}")
    open_google_image_search(search_query)

    print("\nPlease choose one of the following options:")
    print("1. Enter a new URL")
    print("2. Use an existing file from media_files folder")
    print("3. Create slide without media")
    choice = input("Your choice (1/2/3): ").strip()

    if choice == '1':
        new_url = input("Enter URL: ").strip()
        if new_url:
            if 'youtube.com' in new_url or 'youtu.be' in new_url:
                result = download_youtube_video(new_url)
                if result:
                    base_name, filename, filepath = result
                    # For tex file - use local path
                    tex_directive = f"\\play \\file media_files/{filename}"
                    # For text file - use new URL with play directive if original had it
                    text_directive = f"\\play {new_url}" if playable else new_url
                    latex_code = generate_latex_code(
                        base_name,
                        filename,
                        filepath,
                        content,
                        title,
                        True,
                        new_url  # Pass URL for citation
                    )
                    return latex_code, (tex_directive, text_directive)

            # Process other URLs
            valid, message = validate_url(new_url)
            if valid:
                base_name, filename, first_frame_path = download_media(new_url)
                if base_name and filename:
                    # For tex file - use local path
                    tex_directive = f"\\file media_files/{filename}"
                    # For text file - use new URL
                    text_directive = new_url
                    if playable:
                        tex_directive = f"\\play {tex_directive}"
                        text_directive = f"\\play {text_directive}"
                    return generate_latex_code(
                        base_name,
                        filename,
                        first_frame_path,
                        content,
                        title,
                        playable,
                        new_url  # Pass URL for citation
                    ), (tex_directive, text_directive)

    elif choice == '2':
        print("\nAvailable files in media_files folder:")
        try:
            files = os.listdir('media_files')
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
            file_choice = input("Enter file number or name: ").strip()
            if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                chosen_file = files[int(file_choice) - 1]
            else:
                chosen_file = file_choice

            # Verify file exists
            if not os.path.exists(os.path.join('media_files', chosen_file)):
                print(f"Error: File {chosen_file} not found in media_files directory")
                return generate_latex_code(None, None, None, content, title, False), ("\\None", "\\None")

            # Use same file directive for both tex and text files
            file_directive = f"\\file media_files/{chosen_file}"
            if playable:
                file_directive = f"\\play {file_directive}"

            # Generate preview for video files if needed
            first_frame_path = None
            if playable:
                first_frame_path = generate_preview_frame(os.path.join('media_files', chosen_file))

            return generate_latex_code(
                os.path.splitext(chosen_file)[0],
                chosen_file,
                first_frame_path or chosen_file,
                content,
                title,
                playable
            ), (file_directive, file_directive)  # Same directive for both files
        except Exception as e:
            print(f"Error accessing media_files: {str(e)}")
            return generate_latex_code(None, None, None, content, title, False), ("\\None", "\\None")

    # Default to no media (choice 3 or any invalid input)
    latex_code = generate_latex_code(None, None, None, content, title, False)
    return latex_code, ("\\None", "\\None")




# Initialize terminal_io as None - will be set by IDE
terminal_io = None



def update_text_file_with_video(file_path, old_url, new_filepath):
    """
    Immediately updates the text file with the new video path.
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        updated_lines = []
        for line in lines:
            if '\\begin{Content}\\play' in line and 'nothing.something' in line:
                # Replace the old URL with the new file directive
                new_line = f"\\begin{{Content}}\\play \\file {new_filepath}\n"
                updated_lines.append(new_line)
            else:
                updated_lines.append(line)

        with open(file_path, 'w') as f:
            f.writelines(updated_lines)

        print(f"Text file updated with new video path: {new_filepath}")
        return True
    except Exception as e:
        print(f"Error updating text file: {str(e)}")
        return False

def download_youtube_video(url, file_path=None):
    """
    Downloads YouTube video and returns file information.
    Returns (base_name, filename, filepath) or None if download fails.
    """
    try:
        import yt_dlp
    except ImportError:
        print("\nInstalling yt-dlp for YouTube video download...")
        os.system('pip install yt-dlp')
        import yt_dlp

    print("\nDownloading YouTube video...")

    os.makedirs('media_files', exist_ok=True)
    clean_url = url.replace('\\play', '').strip()

    # First, get the video info without downloading
    info_opts = {
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            if info is None:
                print("Error: Could not extract video information")
                return None

            # Create safe filename
            video_title = info.get('title', 'video')
            safe_filename = sanitize_filename(video_title + '.mp4')
            output_path = os.path.join('media_files', safe_filename)

        # Now download with specific options
        download_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
        }

        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([clean_url])

            if os.path.exists(output_path):
                base_name = os.path.splitext(safe_filename)[0]
                print(f"Video downloaded successfully to: {output_path}")
                return base_name, safe_filename, output_path

            print(f"Error: Downloaded file not found at {output_path}")
            return None

    except Exception as e:
        print(f"Error downloading YouTube video: {str(e)}")
        return None

def update_input_file(file_path, url_updates, is_tex_file=False):
    """
    Enhanced version that properly handles URL updates.
    """
    backup_path = file_path + '.backup'
    try:
        # Create backup
        with open(file_path, 'r') as f:
            original_content = f.readlines()
        with open(backup_path, 'w') as f:
            f.writelines(original_content)

        # Process updates
        updated_lines = []
        in_content_block = False

        for line in original_content:
            line = line.rstrip('\n')

            if line.startswith("\\begin{Content}"):
                in_content_block = True
                content_parts = line.split("\\begin{Content}", 1)
                if len(content_parts) > 1 and content_parts[1].strip():
                    url_part = content_parts[1].strip()
                    if url_part in url_updates:
                        # Use appropriate directive based on file type
                        new_directive = url_updates[url_part][0] if is_tex_file else url_updates[url_part][1]
                        line = f"\\begin{{Content}} {new_directive}"
                updated_lines.append(line)
                continue

            elif in_content_block and (line.startswith(("http", "\\play", "\\file"))):
                # Handle cases where the line itself is a URL or directive
                if line in url_updates:
                    new_directive = url_updates[line][0] if is_tex_file else url_updates[line][1]
                    updated_lines.append(new_directive)
                else:
                    updated_lines.append(line)
                continue

            elif line.startswith("\\end{Content}"):
                in_content_block = False
                updated_lines.append(line)
                continue

            else:
                updated_lines.append(line)

        # Write updated content
        with open(file_path, 'w') as f:
            for line in updated_lines:
                f.write(line + '\n')

        print(f"\nInput file has been updated with {'local paths' if is_tex_file else 'new URLs'}.")
        print(f"Original file backed up as: {backup_path}")
        return True

    except Exception as e:
        print(f"Error updating file: {str(e)}")
        return False


def parse_media_directive(directive_string):
    """Parse media directive string into components.
    Returns: (directive_type, media_source, playable, original_directive)"""
    try:
        directive_string = directive_string.strip()
        playable = False
        original_directive = directive_string

        # Handle empty or None cases
        if not directive_string or directive_string == '\\None':
            return 'none', None, False, original_directive

        # Define directive mappings
        directives = {
            '\\wm': 'watermark',
            '\\ff': 'fullframe',
            '\\pip': 'pip',
            '\\split': 'split',
            '\\hl': 'highlight',
            '\\bg': 'background',
            '\\tb': 'topbottom',
            '\\ol': 'overlay',
            '\\corner': 'corner',
            '\\mosaic': 'mosaic'
        }

        # Split the string to handle multiple parts
        parts = directive_string.split()

        # Check for layout directives first
        if parts and parts[0] in directives:
            return directives[parts[0]], ' '.join(parts[1:]), False, original_directive

        # Initialize variables for other directives
        directive_type = 'url'  # default type
        media_source = directive_string  # default to full string

        # Process standard directives
        for i, part in enumerate(parts):
            if part.startswith('\\'):
                if part == '\\play':
                    playable = True
                    if i < len(parts) - 1:
                        remaining_parts = parts[i + 1:]
                        if remaining_parts[0] == '\\file':
                            directive_type = 'file'
                            media_source = ' '.join(remaining_parts[1:])
                        elif remaining_parts[0] == '\\url':
                            directive_type = 'url'
                            media_source = ' '.join(remaining_parts[1:])
                        else:
                            media_source = ' '.join(remaining_parts)
                    break
                elif part == '\\file':
                    directive_type = 'file'
                    if i < len(parts) - 1:
                        media_source = ' '.join(parts[i + 1:])
                    break
                elif part == '\\None':
                    return 'none', None, False, original_directive
                elif part == '\\url':
                    directive_type = 'url'
                    if i < len(parts) - 1:
                        media_source = ' '.join(parts[i + 1:])
                    break

        # Clean up media source
        if media_source and media_source.startswith('\\'):
            # Remove any leading \ and command name
            parts = media_source.split(maxsplit=1)
            if len(parts) > 1:
                media_source = parts[1]

        # Handle special URLs
        if directive_type == 'url' and media_source.startswith(('http://', 'https://')):
            # Special handling for known video platforms
            if any(domain in media_source.lower() for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
                playable = True

        # Handle local file paths
        if directive_type == 'file':
            # Check if it's a video file
            if media_source.lower().endswith(('.mp4', '.avi', '.mov', '.webm', '.mkv')):
                playable = True
            # Ensure proper path format
            media_source = media_source.replace('\\', '/')
            if not media_source.startswith('media_files/') and not media_source.startswith('./'):
                media_source = f"media_files/{media_source}"

        # Special handling for mosaic directive
        if directive_type == 'mosaic':
            # Ensure all image paths are properly formatted
            images = [img.strip() for img in media_source.split(',')]
            media_source = ','.join(
                f"media_files/{img}" if not img.startswith(('media_files/', './')) else img
                for img in images
            )

        return directive_type, media_source, playable, original_directive

    except Exception as e:
        print(f"Error parsing media directive: {str(e)}")
        return 'none', None, False, directive_string


def process_input_file(file_path, output_filename='movie.tex', ide_callback=None):
    """Process input file to convert to TeX format with proper handling of all elements"""
    url_updates = {}
    errors = []
    processed = 0
    failed = 0

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Get preamble information first
        has_preamble, preamble_lines, content_lines, has_titlepage, has_maketitle = detect_preamble(lines)

        # Initialize the output .tex file
        with open(output_filename, 'w') as f:
            if has_preamble:
                f.writelines(preamble_lines)
                if not has_maketitle:
                    f.write("\\maketitle\n")
                if not has_titlepage:
                    f.write("\\begin{frame}\n\\titlepage\n\\end{frame}\n\n")
            else:
                f.write("\\documentclass[12pt]{beamer}\n\\usepackage{graphicx}\n\\usepackage{multimedia}\n\n\\begin{document}\n\n")

        i = 0
        title = None
        content = []
        current_url = None
        current_notes = []
        latex_code = ""
        current_slide_index = 0

        while i < len(content_lines):
            line = content_lines[i].strip()

            if '\\end{document}' in line:
                i += 1
                continue

            if not line:
                i += 1
                continue

            if line.startswith("\\title"):
                title = line.split(None, 1)[1] if len(line.split(None, 1)) > 1 else "Slide"
                if ide_callback:
                    ide_callback("update_current_slide", {'index': current_slide_index, 'title': title})
                i += 1
                continue

            if line.startswith("\\begin{Content}"):
                content = []
                current_notes = []
                if len(line) > len("\\begin{Content}"):
                    current_url = line[len("\\begin{Content}"):].strip()
                else:
                    i += 1
                    if i < len(content_lines):
                        current_url = content_lines[i].strip()
                    else:
                        current_url = None
                i += 1
                continue

            if line.startswith("\\end{Content}"):
                if ide_callback:
                    ide_callback("update_content", {'index': current_slide_index, 'content': content})

                latex_code, new_directive = process_media(
                    current_url if current_url else "\\None",
                    content,
                    title,
                    False,
                    slide_index=current_slide_index,
                    callback=ide_callback
                )

                if latex_code:
                    # Remove frame end if present for notes addition
                    frame_end = latex_code.rfind('\\end{frame}')
                    if frame_end != -1:
                        latex_code = latex_code[:frame_end]

                    # Add notes if present
                    if current_notes:
                        latex_code += "\n    % Presentation notes\n"
                        for note in current_notes:
                            latex_code += f"    \\note{{{note}}}\n"

                    # Add frame end
                    latex_code += "\\end{frame}\n\n"

                    with open(output_filename, 'a') as f:
                        f.write(latex_code)
                    processed += 1

                    if new_directive and current_url and new_directive != current_url:
                        if isinstance(new_directive, tuple):
                            url_updates[current_url] = new_directive
                        else:
                            url_updates[current_url] = (new_directive, new_directive)
                else:
                    failed += 1
                    if ide_callback:
                        ide_callback("error", {'message': f"Failed to process slide {current_slide_index + 1}"})

                content = []
                current_notes = []
                current_slide_index += 1
                i += 1
                continue

            if not line.startswith(("\\begin{Notes}", "\\end{Notes}")):
                content.append(line)

            i += 1

        # Write document end after all slides are processed
        with open(output_filename, 'a') as f:
            f.write("\\end{document}\n")

        if url_updates:
            update_input_file(file_path, url_updates, is_tex_file=False)
            update_input_file(output_filename, url_updates, is_tex_file=True)

        return processed, failed, errors

    except Exception as e:
        error_msg = f"Error processing slide {processed + failed}:\n"
        error_msg += f"Title: {title}\n"
        if content:
            error_msg += f"Content:\n{''.join(['  ' + l + '\n' for l in content])}"
        error_msg += f"Error: {str(e)}\n"
        errors.append(error_msg)
        if ide_callback:
            ide_callback("error", {'message': error_msg})
        return processed, failed, errors

def main():
    """
    Main execution function with enhanced file creation capability.
    """
    print("BeamerSlideGenerator: Creating slides for presentations")
    print("Choose an option:")
    print("1. Process a single media URL (appends to movie.tex)")
    print("2. Process multiple media files from an input file (creates new .tex file)")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        url = input("Enter the media URL or local file (local:filename): ").strip()
        title = input("Enter slide title (optional, press Enter to skip): ").strip()
        content = input("Enter content for the right column (optional, press Enter to skip): ").strip()
        playable = input("Is this media playable? (y/n): ").lower().startswith('y')

        latex_code = process_media(url, content if content else None, title if title else None, playable)
        if latex_code:
            with open('movie.tex', 'a') as f:
                if not os.path.exists('movie.tex'):
                    f.write("""\\documentclass{beamer}
\\usepackage{graphicx}
\\usepackage{multimedia}

\\begin{document}

""")
                f.write(latex_code)
                f.write("\\end{document}")
            print("Slide has been added to 'movie.tex'.")
    elif choice == '2':
        file_path = input("Enter the path to the input file: ")

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"\nFile {file_path} does not exist.")
            create_new = input("Would you like to create a new presentation? (y/n): ").lower().strip()

            if create_new.startswith('y'):
                if create_new_input_file(file_path):
                    print("\nNew presentation file created. Processing the file...")
                else:
                    print("\nFailed to create new presentation file.")
                    return
            else:
                print("\nOperation cancelled.")
                return

        output_file = os.path.splitext(os.path.basename(file_path))[0] + '.tex'
        process_input_file(file_path, output_file)
        print(f"All slides have been written to '{output_file}'.")
    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.")


if __name__ == "__main__":
    main()
