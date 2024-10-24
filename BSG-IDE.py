#!/usr/bin/env python3
"""
BSG_Integrated_Development_Environment.py
An integrated development environment for BeamerSlideGenerator
Combines GUI editing, syntax highlighting, and presentation generation.
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
import webbrowser
import re
from typing import Optional, Dict, List, Tuple
import sys
#---------------------------------------------------------------------------------------------------------

import os
import sys
import subprocess
import shutil
from pathlib import Path
import importlib.util
from typing import List, Tuple

def check_and_install_dependencies() -> None:
    """
    Check for required dependencies and install if missing.
    """
    print("Checking and installing dependencies...")

    # Required Python packages
    python_packages = [
        ('customtkinter', 'customtkinter'),
        ('Pillow', 'PIL'),
        ('requests', 'requests'),
        ('yt_dlp', 'yt_dlp'),
        ('opencv-python', 'cv2')
    ]

    # Required system commands
    system_commands = [
        ('pdflatex', 'texlive texlive-latex-extra texlive-latex-recommended'),
        ('xdg-open', 'xdg-utils')  # For Linux
    ]

    # Check and install Python packages
    for package, import_name in python_packages:
        try:
            importlib.import_module(import_name)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing {package}: {str(e)}")
                sys.exit(1)

    # Check system commands
    is_windows = sys.platform.startswith('win')
    if is_windows:
        check_windows_dependencies()
    else:
        check_linux_dependencies(system_commands)

    # Check for BeamerSlideGenerator.py
    check_bsg_file()

    # Create required directories
    os.makedirs('media_files', exist_ok=True)

    print("\nAll dependencies are satisfied!")

def check_windows_dependencies() -> None:
    """
    Check and setup dependencies for Windows.
    """
    # Check for MiKTeX or TeX Live
    if not (shutil.which('pdflatex') or os.path.exists(r'C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe')):
        print("\nLaTeX is not installed. Please install MiKTeX:")
        print("1. Visit: https://miktex.org/download")
        print("2. Download and install MiKTeX")
        print("3. Run this script again")
        sys.exit(1)

def check_linux_dependencies(system_commands: List[Tuple[str, str]]) -> None:
    """
    Check and setup dependencies for Linux.
    """
    missing_packages = []

    for cmd, packages in system_commands:
        if not shutil.which(cmd):
            missing_packages.append(packages)

    if missing_packages:
        print("\nSome system packages are missing. Installing...")
        try:
            # Try to detect package manager
            if shutil.which('apt'):
                install_cmd = ['sudo', 'apt', 'install', '-y']
            elif shutil.which('dnf'):
                install_cmd = ['sudo', 'dnf', 'install', '-y']
            elif shutil.which('pacman'):
                install_cmd = ['sudo', 'pacman', '-S', '--noconfirm']
            else:
                print("Could not detect package manager. Please install manually:")
                print(" ".join(missing_packages))
                sys.exit(1)

            for packages in missing_packages:
                subprocess.check_call(install_cmd + packages.split())
                print(f"✓ Installed {packages}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing system packages: {str(e)}")
            sys.exit(1)

def check_bsg_file() -> None:
    """
    Check for BeamerSlideGenerator.py and download if missing.
    """
    if not os.path.exists('BeamerSlideGenerator.py'):
        print("\nBeamerSlideGenerator.py not found. Downloading...")
        try:
            import requests
            # Replace with actual URL to your BeamerSlideGenerator.py
            url = "https://raw.githubusercontent.com/yourusername/BeamerSlideGenerator/main/BeamerSlideGenerator.py"
            response = requests.get(url)
            response.raise_for_status()

            with open('BeamerSlideGenerator.py', 'w') as f:
                f.write(response.text)
            print("✓ BeamerSlideGenerator.py downloaded successfully")
        except Exception as e:
            print(f"✗ Error downloading BeamerSlideGenerator.py: {str(e)}")
            print("\nPlease manually download BeamerSlideGenerator.py and place it in the same directory.")
            sys.exit(1)

def create_footer(self) -> None:
    """Create footer with institution info and links"""
    # Footer frame with dark theme
    self.footer = ctk.CTkFrame(self)
    self.footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    # Left side - Institution name
    inst_label = ctk.CTkLabel(
        self.footer,
        text="Artificial Intelligence Research and Intelligent Systems (airis4D)",
        font=("Arial", 12, "bold"),
        text_color="#4ECDC4"  # Using the same color scheme as the editor
    )
    inst_label.pack(side="left", padx=10)

    # Right side - Contact and GitHub links
    links_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
    links_frame.pack(side="right", padx=10)

    # Contact link
    contact_button = ctk.CTkButton(
        links_frame,
        text="nsp@airis4d.com",
        command=lambda: webbrowser.open("mailto:nsp@airis4d.com"),
        fg_color="transparent",
        text_color="#FFB86C",  # Using the bracket color from syntax highlighting
        hover_color="#2F3542",
        height=20
    )
    contact_button.pack(side="left", padx=5)

    # Separator
    separator = ctk.CTkLabel(
        links_frame,
        text="|",
        text_color="#6272A4"  # Using comment color from syntax highlighting
    )
    separator.pack(side="left", padx=5)

    # GitHub link with small icon
    github_button = ctk.CTkButton(
        links_frame,
        text="GitHub",
        command=lambda: webbrowser.open("https://github.com/sajeethphilip/Beamer-Slide-Generator.git"),
        fg_color="transparent",
        text_color="#FFB86C",
        hover_color="#2F3542",
        height=20
    )
    github_button.pack(side="left", padx=5)

    # License info
    license_label = ctk.CTkLabel(
        links_frame,
        text="(Creative Commons License)",
        font=("Arial", 10),
        text_color="#6272A4"
    )
    license_label.pack(side="left", padx=5)
#-------------------------------------------------------------------------------------------------------
# Import BeamerSlideGenerator functions
try:
    from BeamerSlideGenerator import (
        get_beamer_preamble,
        process_media,
        generate_latex_code,
        download_youtube_video,
        construct_search_query,
        open_google_image_search
    )
except ImportError:
    print("Error: BeamerSlideGenerator.py must be in the same directory.")
    sys.exit(1)
#------------------------------------------------------------------------------------------
class BeamerSyntaxHighlighter:
    """Syntax highlighting for Beamer/LaTeX content"""

    def __init__(self, text_widget: ctk.CTkTextbox):
        self.ctk_text = text_widget
        self.text = text_widget._textbox
        self.active = True

        # Create fonts
        self.normal_font = tk.font.Font(family="TkFixedFont")
        self.italic_font = tk.font.Font(family="TkFixedFont", slant="italic")

        # Define syntax highlighting colors
        self.colors = {
            'command': '#FF6B6B',     # LaTeX commands
            'media': '#4ECDC4',       # Media directives
            'bullet': '#95A5A6',      # Bullet points
            'url': '#45B7D1',         # URLs
            'bracket': '#FFB86C',     # Curly brackets
            'comment': '#6272A4',     # Comments
            'rgb': '#50FA7B',         # RGB color commands
            'textcolor': '#BD93F9'    # textcolor commands
        }

        # Configure tags on the underlying Text widget
        for tag, color in self.colors.items():
            self.text.tag_configure(tag, foreground=color, font=self.normal_font)

        # Special formatting for comments with italic font
        self.text.tag_configure("comment",
                              foreground=self.colors['comment'],
                              font=self.italic_font)

        # Define syntax patterns
        self.patterns = [
            (r'\\[a-zA-Z]+', 'command'),
            (r'\\(file|play|None)\s', 'media'),
            (r'^-\s.*$', 'bullet'),
            (r'https?://\S+', 'url'),
            (r'\{.*?\}', 'bracket'),
            (r'%.*$', 'comment'),
            (r'\\textcolor\{.*?\}', 'textcolor'),
            (r'\[RGB\]\{[^\}]*\}', 'rgb')
        ]

        # Bind events to the CTkTextbox
        self.ctk_text.bind('<KeyRelease>', self.highlight)
        self.ctk_text.bind('<Control-v>', lambda e: self.after_paste())

    def toggle(self) -> None:
        """Toggle syntax highlighting on/off"""
        self.active = not self.active
        if self.active:
            self.highlight()
        else:
            self.clear_highlighting()

    def clear_highlighting(self) -> None:
        """Remove all highlighting"""
        for tag in self.colors.keys():
            self.text.tag_remove(tag, "1.0", "end")

    def highlight(self, event=None) -> None:
        """Apply syntax highlighting to the text"""
        if not self.active:
            return

        self.clear_highlighting()
        for pattern, tag in self.patterns:
            self.highlight_pattern(pattern, tag)

    def highlight_pattern(self, pattern: str, tag: str) -> None:
        """Apply highlighting for a specific pattern"""
        content = self.text.get("1.0", "end-1c")
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(pattern, line):
                start = match.start()
                end = match.end()
                start_index = f"{line_num}.{start}"
                end_index = f"{line_num}.{end}"
                self.text.tag_add(tag, start_index, end_index)

    def after_paste(self) -> None:
        """Handle highlighting after paste operation"""
        self.text.after(10, self.highlight)
#------------------------------------------------------------------------------------------
class BeamerSlideEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        AIRIS4D_ASCII_LOGO = """
        /\\
       /  \\   airis
      / /\\ \\  4D
     /_/  \\_\\ LABS
    """

        AIRIS4D_LOGO_COLORS = {
            'flame': '#FF0000',    # Red for the flame
            'box': '#008000',      # Green for the box
            'text': '#0000FF',     # Blue for 'DD'
            'labs': '#000000'      # Black for 'LABS'
        }
        # Version and info
        self.__version__ = "1.0.0"
        self.__author__ = "Ninan Sajeeth Philip"
        self.__license__ = "Creative Commons"
        self.logo_ascii = AIRIS4D_ASCII_LOGO

        # Configure window
        self.title("BeamerSlide Generator IDE")
        self.geometry("1200x800")

        try:
            # Try to load the logo image
            self.logo_image = ctk.CTkImage(
                light_image=Image.open("logo.png"),
                dark_image=Image.open("logo.png"),
                size=(50, 50)
            )
            self.has_logo = True
        except:
            self.has_logo = False
            print("Logo image not found, using ASCII version")

        # Initialize presentation metadata
        self.presentation_info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': 'Artificial Intelligence Research and Intelligent Systems (airis4D)',
            'short_institute': 'airis4D',
            'date': '\\today'
        }

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create UI components
        self.create_menu()
        self.create_sidebar()
        self.create_main_editor()
        self.create_toolbar()
        self.create_context_menu()
        self.create_footer()

        # Initialize variables
        self.current_file: Optional[str] = None
        self.slides: List[Dict] = []
        self.current_slide_index: int = -1

    def create_footer(self) -> None:
        """Create footer with institution info, logo, and links"""
        # Main footer frame with dark theme
        self.footer = ctk.CTkFrame(self)
        self.footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Left side - Logo and Institution name
        left_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        left_frame.pack(side="left", padx=10)

        # Logo (image or ASCII)
        if self.has_logo:
            logo_label = ctk.CTkLabel(
                left_frame,
                image=self.logo_image,
                text=""
            )
            logo_label.pack(side="left", padx=(0, 10))
        else:
            logo_label = ctk.CTkLabel(
                left_frame,
                text=self.logo_ascii,
                font=("Courier", 10),
                justify="left"
            )
            logo_label.pack(side="left", padx=(0, 10))

        # Institution name
        inst_label = ctk.CTkLabel(
            left_frame,
            text="Artificial Intelligence Research and Intelligent Systems (airis4D)",
            font=("Arial", 12, "bold"),
            text_color="#4ECDC4"
        )
        inst_label.pack(side="left", padx=10)

        # Right side - Contact and GitHub links
        links_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        links_frame.pack(side="right", padx=10)

        # Version info
        version_label = ctk.CTkLabel(
            links_frame,
            text=f"v{self.__version__}",
            font=("Arial", 10),
            text_color="#6272A4"
        )
        version_label.pack(side="left", padx=5)

        # Contact link
        contact_button = ctk.CTkButton(
            links_frame,
            text="nsp@airis4d.com",
            command=lambda: webbrowser.open("mailto:nsp@airis4d.com"),
            fg_color="transparent",
            text_color="#FFB86C",
            hover_color="#2F3542",
            height=20
        )
        contact_button.pack(side="left", padx=5)

        # Separator
        separator = ctk.CTkLabel(
            links_frame,
            text="|",
            text_color="#6272A4"
        )
        separator.pack(side="left", padx=5)

        # GitHub link
        github_button = ctk.CTkButton(
            links_frame,
            text="GitHub",
            command=lambda: webbrowser.open("https://github.com/sajeethphilip/Beamer-Slide-Generator.git"),
            fg_color="transparent",
            text_color="#FFB86C",
            hover_color="#2F3542",
            height=20
        )
        github_button.pack(side="left", padx=5)

        # License info
        license_label = ctk.CTkLabel(
            links_frame,
            text=f"({self.__license__})",
            font=("Arial", 10),
            text_color="#6272A4"
        )
        license_label.pack(side="left", padx=5)

    def create_about_dialog(self) -> None:
        """Create about dialog with logo and information"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("About BeamerSlide Generator")
        dialog.geometry("400x300")

        # Center the dialog on the main window
        dialog.transient(self)
        dialog.grab_set()

        # Logo
        if self.has_logo:
            logo_label = ctk.CTkLabel(
                dialog,
                image=self.logo_image,
                text=""
            )
        else:
            logo_label = ctk.CTkLabel(
                dialog,
                text=self.logo_ascii,
                font=("Courier", 10),
                justify="left"
            )
        logo_label.pack(pady=20)

        # Information
        info_text = f"""
BeamerSlide Generator IDE
Version {self.__version__}

Created by {self.__author__}
{self.presentation_info['institution']}

{self.__license__} License
        """

        info_label = ctk.CTkLabel(
            dialog,
            text=info_text,
            font=("Arial", 12),
            justify="center"
        )
        info_label.pack(pady=20)

        # Close button
        close_button = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy
        )
        close_button.pack(pady=20)
#----------------------------------------------------------------------------------------


    def create_menu(self) -> None:
        """Create top menu bar"""
        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Left side buttons
        left_buttons = ctk.CTkFrame(self.menu_frame)
        left_buttons.pack(side="left", padx=5)

        ctk.CTkButton(left_buttons, text="Presentation Settings",
                     command=self.show_settings_dialog).pack(side="left", padx=5)

        # Right side buttons
        right_buttons = ctk.CTkFrame(self.menu_frame)
        right_buttons.pack(side="right", padx=5)

        self.highlight_var = ctk.BooleanVar(value=True)
        self.highlight_switch = ctk.CTkSwitch(
            right_buttons,
            text="Syntax Highlighting",
            variable=self.highlight_var,
            command=self.toggle_highlighting
        )
        self.highlight_switch.pack(side="right", padx=5)

    def create_sidebar(self) -> None:
        """Create sidebar with slide list and controls"""
        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

        # Slide list label
        ctk.CTkLabel(self.sidebar, text="Slides",
                    font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5, pady=5)

        # Slide list with scroll
        self.slide_list = ctk.CTkTextbox(self.sidebar, width=180, height=400)
        self.slide_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.slide_list.bind('<Button-1>', self.on_slide_select)

        # Slide control buttons
        button_data = [
            ("New Slide", self.new_slide),
            ("Delete Slide", self.delete_slide),
            ("Move Up", lambda: self.move_slide(-1)),
            ("Move Down", lambda: self.move_slide(1))
        ]

        for i, (text, command) in enumerate(button_data, start=2):
            ctk.CTkButton(self.sidebar, text=text,
                         command=command).grid(row=i, column=0, padx=5, pady=5)

    def create_main_editor(self) -> None:
        """Create main editor area"""
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Title section
        title_frame = ctk.CTkFrame(self.editor_frame)
        title_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(title_frame, text="Title:").pack(side="left", padx=5)
        self.title_entry = ctk.CTkEntry(title_frame, width=400)
        self.title_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Media section
        media_frame = ctk.CTkFrame(self.editor_frame)
        media_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(media_frame, text="Media:").pack(side="left", padx=5)
        self.media_entry = ctk.CTkEntry(media_frame, width=300)
        self.media_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Media buttons
        media_buttons = ctk.CTkFrame(media_frame)
        media_buttons.pack(side="right", padx=5)

        media_button_data = [
            ("Local File", self.browse_media),
            ("YouTube", self.youtube_dialog),
            ("Search Images", self.search_images),
            ("No Media", lambda: self.media_entry.insert(0, "\\None"))
        ]

        for text, command in media_button_data:
            ctk.CTkButton(media_buttons, text=text,
                         command=command).pack(side="left", padx=2)

        # Content editor
        content_frame = ctk.CTkFrame(self.editor_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(content_frame, text="Content:").pack(anchor="w", padx=5)
        self.content_editor = ctk.CTkTextbox(content_frame, height=400)
        self.content_editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize syntax highlighter
        self.syntax_highlighter = BeamerSyntaxHighlighter(self.content_editor)

    def create_toolbar(self) -> None:

        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # File operations
        file_buttons = [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("Preview PDF", self.preview_pdf),
            ("Generate PDF", self.generate_pdf)
        ]

        for text, command in file_buttons:
            ctk.CTkButton(self.toolbar, text=text,
                         command=command).pack(side="left", padx=5)

    def create_context_menu(self) -> None:
        """Create right-click context menu"""
        self.context_menu = ctk.CTkFrame(self)

        commands = [
            ("Add Bullet", "- "),
            ("Add textcolor", "\\textcolor[RGB]{255,165,0}{}"),
            ("Add Media Directive", "\\file media_files/"),
            ("Add Play Directive", "\\play "),
            ("Add URL", "https://"),
            ("Add Comment", "% ")
        ]

        for text, insert_text in commands:
            ctk.CTkButton(
                self.context_menu,
                text=text,
                command=lambda t=insert_text: self.insert_text(t)
            ).pack(fill="x", padx=2, pady=2)

    def show_settings_dialog(self) -> None:
        """Show presentation settings dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Presentation Settings")
        dialog.geometry("500x400")

        # Create entry fields for presentation metadata
        entries = {}
        for i, (key, value) in enumerate(self.presentation_info.items()):
            label = ctk.CTkLabel(dialog, text=key.title() + ":")
            label.grid(row=i, column=0, padx=5, pady=5)

            entry = ctk.CTkEntry(dialog, width=300)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry

        # Save button
        def save_settings():
            for key, entry in entries.items():
                self.presentation_info[key] = entry.get()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Save Settings",
                     command=save_settings).grid(row=len(entries),
                                               column=0,
                                               columnspan=2,
                                               pady=20)

    def toggle_highlighting(self) -> None:
        """Toggle syntax highlighting"""
        self.syntax_highlighter.toggle()

    def show_context_menu(self, event) -> None:
        """Show context menu at mouse position"""
        self.context_menu.place(x=event.x_root, y=event.y_root)

    def hide_context_menu(self, event) -> None:
        """Hide context menu"""
        self.context_menu.place_forget()

    def insert_text(self, text: str) -> None:
        """Insert text at cursor position"""
        self.content_editor.insert("insert", text)
        self.hide_context_menu(None)
        if self.syntax_highlighter.active:
            self.syntax_highlighter.highlight()

    # File Operations
    def new_file(self) -> None:
        """Create new presentation"""
        self.current_file = None
        self.slides = []
        self.current_slide_index = -1
        self.update_slide_list()
        self.clear_editor()

        # Reset presentation info
        self.presentation_info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': '',
            'short_institute': '',
            'date': '\\today'
        }

    def open_file(self) -> None:
        """Open existing presentation"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.load_file(filename)

    def save_file(self) -> None:
        """Save presentation"""
        if not self.current_file:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.current_file = filename

        if self.current_file:
            self.save_current_slide()
            content = self.generate_tex_content()

            # Save text file
            with open(self.current_file, 'w') as f:
                f.write(content)

            # Generate tex file
            tex_file = os.path.splitext(self.current_file)[0] + '.tex'
            with open(tex_file, 'w') as f:
                f.write(content)

            messagebox.showinfo("Success", "Files saved successfully!")

    def generate_pdf(self) -> None:
        """Generate PDF from presentation"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        self.save_file()
        tex_file = os.path.splitext(self.current_file)[0] + '.tex'

        # Run pdflatex twice to ensure all references are resolved
        os.system(f"pdflatex {tex_file}")
        os.system(f"pdflatex {tex_file}")

        messagebox.showinfo("Success", "PDF generated successfully!")

    def preview_pdf(self) -> None:
        """Preview generated PDF"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save and generate PDF first!")
            return

        pdf_file = os.path.splitext(self.current_file)[0] + '.pdf'
        if os.path.exists(pdf_file):
            os.system(f"xdg-open {pdf_file}")  # Linux
            # For Windows, use: os.startfile(pdf_file)
        else:
            messagebox.showwarning("Warning", "PDF file not found. Generate it first!")
    # Slide Management
    def new_slide(self) -> None:
        """Create new slide"""
        self.save_current_slide()

        new_slide = {
            'title': 'New Slide',
            'media': '',
            'content': []
        }

        self.slides.append(new_slide)
        self.current_slide_index = len(self.slides) - 1
        self.update_slide_list()
        self.load_slide(self.current_slide_index)

    def delete_slide(self) -> None:
        """Delete current slide"""
        if self.current_slide_index >= 0:
            del self.slides[self.current_slide_index]
            if self.slides:
                self.current_slide_index = max(0, self.current_slide_index - 1)
            else:
                self.current_slide_index = -1
            self.update_slide_list()
            if self.current_slide_index >= 0:
                self.load_slide(self.current_slide_index)
            else:
                self.clear_editor()

    def move_slide(self, direction: int) -> None:
        """Move current slide up or down"""
        if not self.slides or self.current_slide_index < 0:
            return

        new_index = self.current_slide_index + direction
        if 0 <= new_index < len(self.slides):
            self.save_current_slide()
            self.slides[self.current_slide_index], self.slides[new_index] = \
                self.slides[new_index], self.slides[self.current_slide_index]
            self.current_slide_index = new_index
            self.update_slide_list()
            self.load_slide(self.current_slide_index)

    def update_slide_list(self) -> None:
        """Update slide list in sidebar"""
        self.slide_list.delete('1.0', 'end')
        for i, slide in enumerate(self.slides):
            prefix = "→ " if i == self.current_slide_index else "  "
            self.slide_list.insert('end', f"{prefix}Slide {i+1}: {slide['title']}\n")

    def on_slide_select(self, event) -> None:
        """Handle slide selection from list"""
        index = self.slide_list.index("@%d,%d" % (event.x, event.y)).split('.')[0]
        index = int(index)
        if 0 <= index < len(self.slides):
            self.save_current_slide()
            self.current_slide_index = index
            self.load_slide(index)
            self.update_slide_list()

    def load_slide(self, index: int) -> None:
        """Load slide data into editor"""
        slide = self.slides[index]
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, slide['title'])

        self.media_entry.delete(0, 'end')
        self.media_entry.insert(0, slide['media'])

        self.content_editor.delete('1.0', 'end')
        for item in slide['content']:
            if not item.startswith('-'):
                item = f"- {item}"
            self.content_editor.insert('end', f"{item}\n")

        if self.syntax_highlighter.active:
            self.syntax_highlighter.highlight()

    def save_current_slide(self) -> None:
        """Save current slide data"""
        if self.current_slide_index >= 0:
            self.slides[self.current_slide_index] = {
                'title': self.title_entry.get(),
                'media': self.media_entry.get(),
                'content': [line for line in self.content_editor.get('1.0', 'end-1c').split('\n') if line.strip()]
            }

    def clear_editor(self) -> None:
        """Clear editor fields"""
        self.title_entry.delete(0, 'end')
        self.media_entry.delete(0, 'end')
        self.content_editor.delete('1.0', 'end')

    # Media Handling
    def browse_media(self) -> None:
        """Browse for local media file"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Media files", "*.png *.jpg *.gif *.mp4 *.avi *.mov"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Copy file to media_files directory if it's not already there
            media_dir = "media_files"
            os.makedirs(media_dir, exist_ok=True)

            base_name = os.path.basename(filename)
            new_path = os.path.join(media_dir, base_name)

            if filename != new_path:
                import shutil
                shutil.copy2(filename, new_path)

            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, f"\\file media_files/{base_name}")

    def youtube_dialog(self) -> None:
        """Handle YouTube video insertion"""
        dialog = ctk.CTkInputDialog(
            text="Enter YouTube URL:",
            title="Add YouTube Video"
        )
        url = dialog.get_input()
        if url:
            if 'youtube.com' in url or 'youtu.be' in url:
                self.media_entry.delete(0, 'end')
                self.media_entry.insert(0, f"\\play {url}")
            else:
                messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")

    def search_images(self) -> None:
        """Open image search for current slide"""
        query = construct_search_query(
            self.title_entry.get(),
            self.content_editor.get("1.0", "end").split('\n')
        )
        open_google_image_search(query)

    # Content Generation
    def generate_tex_content(self) -> str:
        """Generate complete tex file content"""
        content = get_beamer_preamble(
            self.presentation_info['title'],
            self.presentation_info['subtitle'],
            self.presentation_info['author'],
            self.presentation_info['institution'],
            self.presentation_info['short_institute'],
            self.presentation_info['date']
        )

        # Add slides
        for slide in self.slides:
            content += f"\\title {slide['title']}\n"
            content += "\\begin{Content}"
            if slide['media']:
                content += f" {slide['media']}"
            content += "\n"

            # Add content items
            for item in slide['content']:
                if item.strip():
                    content += f"{item}\n"

            content += "\\end{Content}\n\n"

        content += "\\end{document}"
        return content

    def load_file(self, filename: str) -> None:
        """Load presentation from file"""
        try:
            with open(filename, 'r') as f:
                content = f.read()

            # Parse content
            self.current_file = filename
            self.slides = []
            self.current_slide_index = -1

            # Extract presentation info
            import re
            for key in self.presentation_info:
                pattern = f"\\\\{key}{{(.*?)}}"
                match = re.search(pattern, content)
                if match:
                    self.presentation_info[key] = match.group(1)

            # Extract slides
            slide_pattern = r"\\title\s+(.*?)\n\\begin{Content}(.*?)\\end{Content}"
            slide_matches = re.finditer(slide_pattern, content, re.DOTALL)

            for match in slide_matches:
                title = match.group(1).strip()
                content_block = match.group(2).strip()

                # Extract media directive if present
                media = ""
                content_lines = []

                first_line = content_block.split('\n')[0].strip()
                if first_line.startswith('\\'):
                    media = first_line
                    content_lines = content_block.split('\n')[1:]
                else:
                    content_lines = content_block.split('\n')

                self.slides.append({
                    'title': title,
                    'media': media,
                    'content': [line for line in content_lines if line.strip()]
                })

            if self.slides:
                self.current_slide_index = 0
                self.load_slide(0)

            self.update_slide_list()

        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")

def main():
    check_and_install_dependencies()
    app = BeamerSlideEditor()
    app.mainloop()

if __name__ == "__main__":
    main()
