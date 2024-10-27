#!/usr/bin/env python3
"""
BeamerSlideGenerator.py
A tool for generating Beamer presentation slides with multimedia content.
Supports local files, URL downloads, and content-only slides.
"""

import os,re
import time
import requests
import webbrowser
from PIL import Image
from urllib.parse import urlparse, unquote
from pathlib import Path
import mimetypes

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

def format_source_citation(url):
    """
    Formats source URLs for citation.
    """
    try:
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            return f"YouTube video: {url}"
        elif 'github.com' in parsed.netloc:
            return f"GitHub repository: {url}"
        else:
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            return f"Source: {base_url} \\href{{{url}}}{{[link]}}"
    except:
        return f"Source: {url}"

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
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            output_path = f"media_files/{base_name}_preview.png"

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
    Returns the correct Beamer preamble with shadow text support
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

% Set the logo to appear on all slides
\\logo{{\\includegraphics[width=1cm]{{logo.png}}}}
\\usepackage{{url}}
\\usepackage[export]{{adjustbox}}

% Add these to your preamble if not already present
\\usetikzlibrary{{shapes.geometric, positioning, arrows.meta, backgrounds, fit}}

% Redefine the frame to have smaller margins
\\setbeamersize{{text margin left=5pt,text margin right=5pt}}

% Centering frame titles
\\setbeamertemplate{{frametitle}}[default][center]

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
\\makeatletter
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
\\makeatother

\\title{{{title}}}
{f'\\subtitle{{{subtitle}}}' if subtitle else ''}
\\author{{{author}}}
\\institute{{\\textcolor{{mygreen}}{{{institution}}}}}
\\date{{{date}}}

\\begin{{document}}
\\maketitle
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
                url = f"\\file {chosen_file}"
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

def update_input_file(file_path, url_updates, is_tex_file=False):
    """
    Updates either tex or text file with appropriate directives.
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

            elif in_content_block and (line.startswith("http") or line.startswith("\\play") or line.startswith("\\file")):
                if line in url_updates:
                    # Use appropriate directive based on file type
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

        print(f"\nInput file has been updated with {'local paths' if is_tex_file else 'original URLs'}.")
        print(f"Original file backed up as: {backup_path}")
        return True

    except Exception as e:
        print(f"Error updating file: {str(e)}")
        return False


def generate_latex_code(base_name, filename, first_frame_path, content=None, title=None, playable=False, source_url=None, notes=None):
    """Enhanced version that handles notes properly"""

    escaped_base_name = base_name.replace("_", "\\_") if base_name else "Media"
    media_folder = "media_files"

    # Capitalize first letter of each word in title
    if title:
        words = title.split()
        capitalized_words = [word[0].upper() + word[1:] if word else '' for word in words]
        frame_title = " ".join(capitalized_words)
        frame_title = frame_title.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
    else:
        frame_title = f"Media: {escaped_base_name}"

    # Handle no-media case (when \None is specified)
    if not filename or filename == "\\None":
        latex_code = f"""
\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
"""
        if content:
            latex_code += """    \\vspace{0.5em}
    \\begin{itemize}
"""
            for item in content:
                item = item.strip()
                if item.startswith('-'):
                    item = item[1:].strip()
                if not item.lower().startswith(title.lower() if title else ''):
                    item = item.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
                    latex_code += f"        \\item {item}\n"
            latex_code += """    \\end{itemize}"""
            # Add notes if present
            if notes and notes.strip():
                latex_code += "\\note{\n\\begin{itemize}\n"
                for note_line in notes.split('\n'):
                    if note_line.strip():
                        # Clean up any existing bullet points
                        note_text = note_line.lstrip('•- ').strip()
                        latex_code += f"\\item {note_text}\n"
                latex_code += "\\end{itemize}\n}\n"

        latex_code += """
\\end{frame}

"""
        return latex_code

    # Regular media case with two columns
    latex_code = f"""
\\begin{{frame}}{{\\Large\\textbf{{{frame_title}}}}}
    \\vspace{{0.5em}}
    \\begin{{columns}}
        \\begin{{column}}{{0.48\\textwidth}}
            \\centering
"""

    # Add preview image or media
    if playable:
        if first_frame_path and os.path.exists(first_frame_path):
            latex_code += f"""            \\fbox{{\\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{{{first_frame_path}}}}}
"""
        else:
            latex_code += "            \\textbf{[Media Preview Not Available]}\n"

        latex_code += f"""
            \\vspace{{0.5em}}
            \\footnotesize{{Click to play}}
            \\movie[externalviewer]{{\\textcolor{{blue}}{{\\underline{{Play}}}}}}{{./{media_folder}/{filename}}}
"""

    else:
        # Non-playable media with frame
        image_path = first_frame_path if first_frame_path else f'{media_folder}/{filename}'
        latex_code += f"""            \\fbox{{\\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{{{image_path}}}}}
"""

    # Add content column
    latex_code += """        \\end{column}%
        \\begin{column}{0.48\\textwidth}
            \\begin{itemize}
"""
    if content:
        for item in content:
            item = item.strip()
            if item.startswith('-'):
                item = item[1:].strip()
            if not item.lower().startswith(title.lower() if title else ''):
                item = item.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
                latex_code += f"                \\item {item}\n"
    latex_code += """            \\end{itemize}"""

    # Add source citation if URL exists
    if source_url:
        latex_code += f"""
            \\vspace{{0.5em}}
            \\rule{{0.9\\textwidth}}{{0.4pt}}
            {{\\tiny Source: {source_url}}}"""

    latex_code += """
        \\end{column}
    \\end{columns}
\\end{frame}

"""
    return latex_code


def process_media(url, content=None, title=None, playable=False):
    """
    Modified to handle source URLs properly.
    """
    directive_type, media_source, is_playable, original_directive = parse_media_directive(url)
    playable = playable or is_playable

    # Track source URL
    source_url = None
    if directive_type == 'url' and media_source.startswith(('http://', 'https://')):
        source_url = media_source
        # Remove any existing source citations from content
        if content:
            content = [item for item in content if not ('\\footnote' in item and 'Source:' in item)]

    # Handle YouTube URLs
    if directive_type == 'url' and ('youtube.com' in media_source or 'youtu.be' in media_source):
        result = download_youtube_video(media_source)
        if result:
            base_name, filename, filepath = result
            first_frame_path = generate_preview_frame(filepath)
            tex_directive = f"\\play \\file media_files/{filename}"
            text_directive = f"\\play {media_source}"

            return generate_latex_code(
                base_name,
                filename,
                first_frame_path,
                content,
                title,
                True,
                source_url
            ), (tex_directive, text_directive)

    # [Rest of the function remains similar, but pass source_url to generate_latex_code]

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
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    base_path = os.path.join('media_files', base_name)
    import glob
    possible_files = glob.glob(base_path + '.*')
    if possible_files:
        return possible_files[0]

    print(f"Warning: Media file not found: {filepath}")
    return None

def process_media(url, content=None, title=None, playable=False):
    """
    Enhanced version that maintains source URLs.
    """
    directive_type, media_source, is_playable, original_directive = parse_media_directive(url)
    playable = playable or is_playable
    source_url = None

    # Extract source URL for YouTube or other URLs
    if directive_type == 'url':
        if 'youtube.com' in media_source or 'youtu.be' in media_source:
            source_url = media_source.strip()

    if directive_type == 'none':
        return generate_latex_code(None, None, None, content, title, False, None), "\\None"

    elif directive_type == 'file':
        if os.path.exists(media_source):
            base_name = os.path.splitext(os.path.basename(media_source))[0]
            first_frame_path = None
            if playable:
                first_frame_path = generate_preview_frame(media_source)
            return generate_latex_code(
                base_name,
                os.path.basename(media_source),
                first_frame_path or media_source,
                content, title, playable, None
            ), original_directive
        else:
            print(f"\nWarning: Local file not found: {media_source}")
            return handle_missing_media(url, content, title, playable)

    else:  # Regular URL case
        valid, message = validate_url(media_source)
        if not valid:
            print(f"\nWarning: Original URL failed: {message}")
            return handle_missing_media(url, content, title, playable)

        # Handle YouTube videos
        if 'youtube.com' in media_source or 'youtu.be' in media_source:
            result = download_youtube_video(media_source)
            if result:
                base_name, filename, filepath = result
                first_frame_path = generate_preview_frame(filepath)
                new_directive = f"\\play \\file media_files/{filename}"
                return generate_latex_code(
                    base_name,
                    filename,
                    first_frame_path,
                    content,
                    title,
                    True,
                    source_url
                ), new_directive

        # Handle other media
        base_name, filename, first_frame_path = download_media(media_source)
        if base_name and filename:
            if playable:
                first_frame_path = generate_preview_frame(os.path.join('media_files', filename))
            elif first_frame_path:
                first_frame_path = verify_media_file(first_frame_path)

            media_path = verify_media_file(os.path.join('media_files', filename))
            if media_path:
                new_directive = f"\\play \\file media_files/{filename}" if playable else f"\\file media_files/{filename}"
                return generate_latex_code(
                    base_name,
                    filename,
                    first_frame_path,
                    content,
                    title,
                    playable,
                    source_url
                ), new_directive

        return handle_missing_media(url, content, title, playable)

def handle_missing_media(original_url, content, title, playable):
    """
    Enhanced version that properly handles URL updates in both tex and text files.
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
                    latex_code = generate_latex_code(base_name, filename, filename, content, title, True)
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
                        playable
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

            # Use same file directive for both tex and text files
            file_directive = f"\\file media_files/{chosen_file}"
            if playable:
                file_directive = f"\\play {file_directive}"
            return generate_latex_code(
                os.path.splitext(chosen_file)[0],
                chosen_file,
                chosen_file,
                content,
                title,
                playable
            ), (file_directive, file_directive)  # Same directive for both files
        except Exception as e:
            print(f"Error accessing media_files: {str(e)}")

    # Default to no media
    return generate_latex_code(None, None, None, content, title, False), ("\\None", "\\None")


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
    """
    Enhanced parser to handle play directives with both URLs and local files.
    Returns tuple of (directive_type, media_source, playable, original_directive)
    """
    directive_string = directive_string.strip()
    playable = False
    original_directive = directive_string

    # Handle empty or None cases
    if not directive_string or directive_string == '\\None':
        return 'none', None, False, original_directive

    # Split the string to handle multiple parts
    parts = directive_string.split()

    # Initialize variables
    directive_type = 'url'  # default type
    media_source = directive_string  # default to full string

    # Process the parts
    for i, part in enumerate(parts):
        if part.startswith('\\'):
            if part == '\\play':
                playable = True
                if i < len(parts) - 1:
                    remaining_parts = parts[i + 1:]
                    if remaining_parts[0] == '\\file':
                        directive_type = 'file'
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

    return directive_type, media_source, playable, original_directive

def process_input_file(file_path, output_filename='movie.tex'):
    """Process input file to convert to TeX format"""
    url_updates = {}
    errors = []
    processed = 0
    failed = 0

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return

    # Get preamble information first
    has_preamble, preamble_lines, content_lines, has_titlepage, has_maketitle = detect_preamble(lines)

    # Initialize the output .tex file
    try:
        with open(output_filename, 'w') as f:
            if has_preamble:
                # Just copy the preamble as is
                f.writelines(preamble_lines)

                if not has_maketitle:
                    f.write("\\maketitle\n")
                if not has_titlepage:
                    f.write("\\begin{frame}\n\\titlepage\n\\end{frame}\n\n")
            else:
                # Basic preamble without notes configuration
                f.write("""\\documentclass[12pt]{beamer}
\\usepackage{graphicx}
\\usepackage{multimedia}

\\begin{document}

""")
    except Exception as e:
        print(f"Error creating output file: {str(e)}")
        return

    i = 0
    title = None
    content = []
    current_url = None
    latex_code = ""
    current_notes = []

    # Process content lines
    while i < len(content_lines):
        try:
            line = content_lines[i].strip()

            if not line:
                i += 1
                continue

            if line.startswith("\\title"):
                title = line.split(None, 1)[1] if len(line.split(None, 1)) > 1 else "Slide"
                i += 1
                continue

            if line.startswith("\\begin{Content}"):
                content = []
                current_notes = []  # Reset notes for new slide
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
                if not current_url:
                    print(f"\nNo URL provided for slide with title: {title}")
                    search_query = construct_search_query(title, content)
                    print(f"Opening Google Image search for: {search_query}")
                    open_google_image_search(search_query)

                    print("\nPlease choose one of the following options:")
                    print("1. Enter a new URL")
                    print("2. Use an existing file from media_files folder")
                    print("3. Create slide without media")
                    choice = input("Your choice (1/2/3): ").strip()

                    if choice == '1':
                        current_url = input("Enter URL: ").strip()
                    elif choice == '2':
                        print("\nAvailable files in media_files folder:")
                        files = os.listdir('media_files')
                        for idx, file in enumerate(files, 1):
                            print(f"{idx}. {file}")
                        file_choice = input("Enter file number or name: ").strip()
                        if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                            chosen_file = files[int(file_choice) - 1]
                        else:
                            chosen_file = file_choice
                        current_url = f"\\file media_files/{chosen_file}"
                    else:
                        current_url = "\\None"

                # Look ahead for Notes block
                j = i + 1
                while j < len(content_lines):
                    next_line = content_lines[j].strip()
                    if next_line.startswith("\\begin{Notes}"):
                        j += 1  # Skip the begin Notes line
                        while j < len(content_lines):
                            note_line = content_lines[j].strip()
                            if note_line.startswith("\\end{Notes}"):
                                break
                            if note_line:
                                current_notes.append(note_line)
                            j += 1
                    elif next_line.startswith("\\title") or next_line.startswith("\\begin{Content}"):
                        break
                    j += 1

                # Generate slide content
                latex_code, new_directive = process_media(
                    current_url if current_url else "\\None",
                    content,
                    title,
                    False
                )

                if latex_code:
                    # Remove frame end if present
                    frame_end = latex_code.rfind('\\end{frame}')
                    if frame_end != -1:
                        latex_code = latex_code[:frame_end]

                    # Add notes if present
                    if current_notes:
                        for note in current_notes:
                            latex_code += f"\\note[item]{{{note.strip()}}}\n"

                    # Add frame end
                    latex_code += "\\end{frame}\n\n"

                    with open(output_filename, 'a') as f:
                        f.write(latex_code)
                    processed += 1

                    if new_directive and current_url and new_directive != current_url:
                        if current_url.startswith("\\play "):
                            url_updates[current_url.replace("\\play ", "").strip()] = new_directive
                        else:
                            url_updates[current_url] = new_directive
                else:
                    failed += 1

                content = []
                current_notes = []
                title = None
                current_url = None
                i += 1
                continue

            elif not line.startswith(("\\begin{Notes}", "\\end{Notes}")):
                content.append(line)

            i += 1

        except Exception as e:
            failed += 1
            error_msg = f"Error processing slide {processed + failed}:\n"
            error_msg += f"Title: {title}\n"
            if content:
                error_msg += f"Content:\n{''.join(['  ' + l + '\n' for l in content])}"
            error_msg += f"Error: {str(e)}\n"
            errors.append(error_msg)
            print(f"\nWarning: Error in slide processing: {str(e)}")
            i += 1

    # Write document end
    with open(output_filename, 'a') as f:
        f.write("\\end{document}")

    if url_updates:
        update_input_file(file_path, url_updates, is_tex_file=False)
        update_input_file(output_filename, url_updates, is_tex_file=True)

    print(f"\nProcessing complete:")
    print(f"Successfully processed slides: {processed}")
    print(f"Failed slides: {failed}")

    if errors:
        print("\nError Report:")
        for i, error in enumerate(errors, 1):
            print(f"\nError {i}:")
            print(error)

    if processed > 0:
        print(f"\nOutput written to: {output_filename}")
        if url_updates:
            print("Both source file and output file have been updated with new media paths.")


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
