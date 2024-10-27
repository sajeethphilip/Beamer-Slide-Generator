#!/usr/bin/env python3
"""
BSG_Integrated_Development_Environment.py
An integrated development environment for BeamerSlideGenerator
Combines GUI editing, syntax highlighting, and presentation generation.
"""
import tkinter as tk
from PIL import Image
from tkinter import ttk
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import os
from pathlib import Path
import webbrowser
import re
from typing import Optional, Dict, List, Tuple
from PIL import Image, ImageDraw
import requests
import traceback  # Add this import at the top
#---------------------------------------------------------------------------------------------------------
import time
import shutil
import zipfile
import tempfile
from pathlib import Path
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
            url = "https://raw.githubusercontent.com/sajeethphilip/BeamerSlideGenerator/main/BeamerSlideGenerator.py"
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
class NotesToolbar(ctk.CTkFrame):
    """Toolbar for notes formatting and templates"""
    def __init__(self, parent, notes_editor, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.notes_editor = notes_editor

        # Templates
        self.templates = {
            "Key Points": "• Key points:\n  - \n  - \n  - \n",
            "Time Markers": "• Timing guide:\n  0:00 - Introduction\n  0:00 - Main points\n  0:00 - Conclusion",
            "Questions": "• Potential questions:\nQ1: \nA1: \n\nQ2: \nA2: ",
            "References": "• Additional references:\n  - Title:\n    Author:\n    Page: ",
            "Technical Details": "• Technical details:\n  - Specifications:\n  - Parameters:\n  - Requirements:",
        }

        self.create_toolbar()

    def create_toolbar(self):
        """Create the notes toolbar"""
        # Template dropdown
        template_frame = ctk.CTkFrame(self)
        template_frame.pack(side="left", padx=5, pady=2)

        ctk.CTkLabel(template_frame, text="Template:").pack(side="left", padx=2)

        self.template_var = tk.StringVar(value="Select Template")
        template_menu = ctk.CTkOptionMenu(
            template_frame,
            values=list(self.templates.keys()),
            variable=self.template_var,
            command=self.insert_template,
            width=150
        )
        template_menu.pack(side="left", padx=2)

        # Separator
        ttk.Separator(self, orient="vertical").pack(side="left", padx=5, fill="y", pady=2)

        # Formatting buttons
        formatting_frame = ctk.CTkFrame(self)
        formatting_frame.pack(side="left", padx=5, pady=2)

        formatting_buttons = [
            ("B", self.add_bold, "Bold"),
            ("I", self.add_italic, "Italic"),
            ("C", self.add_color, "Color"),
            ("⚡", self.add_highlight, "Highlight"),
            ("•", self.add_bullet, "Bullet point"),
            ("⏱", self.add_timestamp, "Timestamp"),
            ("⚠", self.add_alert, "Alert"),
            ("💡", self.add_tip, "Tip")
        ]

        for text, command, tooltip in formatting_buttons:
            btn = ctk.CTkButton(
                formatting_frame,
                text=text,
                command=command,
                width=30,
                height=30
            )
            btn.pack(side="left", padx=2)
            self.create_tooltip(btn, tooltip)

    def create_tooltip(self, widget, text):
        """Create tooltip for buttons"""
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20

            # Create tooltip window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = tk.Label(self.tooltip, text=text,
                           justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1)
            label.pack()

        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def insert_template(self, choice):
        """Insert selected template"""
        if choice in self.templates:
            self.notes_editor.insert('insert', self.templates[choice])
            self.template_var.set("Select Template")  # Reset dropdown

    def add_bold(self):
        """Add bold text"""
        self.wrap_selection(r'\textbf{', '}')

    def add_italic(self):
        """Add italic text"""
        self.wrap_selection(r'\textit{', '}')

    def add_color(self):
        """Add colored text"""
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        color = simpledialog.askstring(
            "Color",
            "Enter color name or RGB values:",
            initialvalue=colors[0]
        )
        if color:
            self.wrap_selection(f'\\textcolor{{{color}}}{{', '}')

    def add_highlight(self):
        """Add highlighted text"""
        self.wrap_selection('\\hl{', '}')

    def add_bullet(self):
        """Add bullet point"""
        self.notes_editor.insert('insert', '\n• ')

    def add_timestamp(self):
        """Add timestamp"""
        timestamp = simpledialog.askstring(
            "Timestamp",
            "Enter timestamp (MM:SS):",
            initialvalue="00:00"
        )
        if timestamp:
            self.notes_editor.insert('insert', f'[{timestamp}] ')

    def add_alert(self):
        """Add alert note"""
        self.notes_editor.insert('insert', '⚠ Important: ')

    def add_tip(self):
        """Add tip"""
        self.notes_editor.insert('insert', '💡 Tip: ')

    def wrap_selection(self, prefix, suffix):
        """Wrap selected text with prefix and suffix"""
        try:
            selection = self.notes_editor.get('sel.first', 'sel.last')
            self.notes_editor.delete('sel.first', 'sel.last')
            self.notes_editor.insert('insert', f'{prefix}{selection}{suffix}')
        except tk.TclError:  # No selection
            self.notes_editor.insert('insert', f'{prefix}{suffix}')
            # Move cursor inside braces
            current_pos = self.notes_editor.index('insert')
            self.notes_editor.mark_set('insert', f'{current_pos}-{len(suffix)}c')

class EnhancedNotesEditor(ctk.CTkFrame):
    """Enhanced notes editor with toolbar and templates"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create toolbar
        self.toolbar = NotesToolbar(self, self.notes_editor)
        self.toolbar.pack(fill="x", padx=2, pady=2)

        # Create editor
        self.notes_editor = ctk.CTkTextbox(self)
        self.notes_editor.pack(fill="both", expand=True, padx=2, pady=2)

        # Enhanced syntax highlighting
        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        """Setup enhanced syntax highlighting for notes"""
        self.highlighter = BeamerSyntaxHighlighter(self.notes_editor)

        # Add additional patterns for notes
        additional_patterns = [
            (r'⚠.*$', 'alert'),
            (r'💡.*$', 'tip'),
            (r'\[[\d:]+\]', 'timestamp'),
            (r'•.*$', 'bullet'),
            (r'\\hl\{.*?\}', 'highlight'),
        ]

        # Add additional colors
        additional_colors = {
            'alert': '#FF6B6B',
            'tip': '#4ECDC4',
            'timestamp': '#FFB86C',
            'highlight': '#BD93F9',
        }

        # Update highlighter
        self.highlighter.patterns.extend(additional_patterns)
        self.highlighter.colors.update(additional_colors)
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
class FileThumbnailBrowser(ctk.CTkToplevel):
    def __init__(self, parent, initial_dir="media_files", callback=None):
        super().__init__(parent)
        self.title("Media Browser")
        self.geometry("800x600")

        # Import required modules
        from PIL import Image, ImageDraw, ImageFont
        import mimetypes

        # Store initial directory and callback
        self.current_dir = os.path.abspath(initial_dir)
        self.callback = callback
        self.thumbnails = []
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4

        # File categories with extended video types
        self.file_categories = {
            'image': ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'),
            'video': ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.gif'),
            'audio': ('.mp3', '.wav', '.ogg', '.m4a', '.flac'),
            'document': ('.pdf', '.doc', '.docx', '.txt', '.tex'),
            'data': ('.csv', '.xlsx', '.json', '.xml')
        }

        # Create UI components with navigation
        self.create_navigation_bar()
        self.create_toolbar()
        self.create_content_area()
        self.load_files()

    def create_navigation_bar(self):
        """Create navigation bar with path and controls"""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(fill="x", padx=5, pady=5)

        # Back button
        self.back_button = ctk.CTkButton(
            nav_frame,
            text="⬅ Back",
            command=self.navigate_up,
            width=60
        )
        self.back_button.pack(side="left", padx=5)

        # Path display and navigation
        self.path_var = tk.StringVar()
        self.path_entry = ctk.CTkEntry(
            nav_frame,
            textvariable=self.path_var,
            width=400
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.path_entry.bind('<Return>', self.navigate_to_path)

        # Update current path
        self.update_path_display()

    def create_toolbar(self):
        """Create toolbar with sorting and view options"""
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=5, pady=5)

        # Sorting options
        sort_label = ctk.CTkLabel(toolbar, text="Sort by:")
        sort_label.pack(side="left", padx=5)

        self.sort_var = tk.StringVar(value="name")
        sort_options = ["name", "date", "size", "type"]

        for option in sort_options:
            rb = ctk.CTkRadioButton(
                toolbar,
                text=option.capitalize(),
                variable=self.sort_var,
                value=option,
                command=self.refresh_files
            )
            rb.pack(side="left", padx=10)

        # Sort direction
        self.reverse_var = tk.BooleanVar(value=False)
        reverse_cb = ctk.CTkCheckBox(
            toolbar,
            text="Reverse",
            variable=self.reverse_var,
            command=self.refresh_files
        )
        reverse_cb.pack(side="left", padx=10)

    def create_content_area(self):
        """Create scrollable content area with enhanced navigation"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self.main_frame, bg='black')
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical")
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal")

        # Configure scrollbars
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        self.canvas.config(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Pack scrollbars
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create frame for content
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            tags="self.scrollable_frame"
        )

        # Configure scroll bindings
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Bind scroll events
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # Touch pad/track pad scrolling
        if sys.platform == 'darwin':
            self.canvas.bind("<TouchpadScroll>", self._on_touchpad_scroll)
        else:
            self.canvas.bind("<Shift-MouseWheel>", self._on_touchpad_scroll)

    def _on_mousewheel(self, event):
        """Handle mouse wheel and touchpad scrolling"""
        if event.num == 4:  # Linux up
            delta = 120
        elif event.num == 5:  # Linux down
            delta = -120
        else:  # Windows/MacOS
            delta = event.delta

        shift_pressed = event.state & 0x1  # Check if Shift is pressed
        if shift_pressed:
            self.canvas.xview_scroll(int(-1 * delta/120), "units")
        else:
            self.canvas.yview_scroll(int(-1 * delta/120), "units")

    def _on_touchpad_scroll(self, event):
        """Handle touchpad scrolling"""
        if event.state & 0x1:  # Shift pressed - horizontal scroll
            self.canvas.xview_scroll(int(-1 * event.delta/30), "units")
        else:  # Vertical scroll
            self.canvas.yview_scroll(int(-1 * event.delta/30), "units")

    def _bind_mousewheel(self, event):
        """Bind mousewheel when mouse enters canvas"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        if sys.platform.startswith('linux'):
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")
        if sys.platform.startswith('linux'):
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def get_file_category(self, filename):
        """Determine file category and appropriate thumbnail style"""
        ext = os.path.splitext(filename)[1].lower()

        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category

        return 'other'

    def create_thumbnail(self, file_path):
        """Create thumbnail based on file type"""
        try:
            category = self.get_file_category(file_path)
            ext = os.path.splitext(file_path)[1].lower()
            thumb_size = (150, 150)

            if category == 'image':
                try:
                    with Image.open(file_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')

                        # Create thumbnail
                        img.thumbnail(thumb_size, Image.Resampling.LANCZOS)

                        # Create background
                        thumb_bg = Image.new('RGB', thumb_size, 'black')

                        # Center image on background
                        offset = ((thumb_size[0] - img.size[0]) // 2,
                                (thumb_size[1] - img.size[1]) // 2)
                        thumb_bg.paste(img, offset)

                        return ctk.CTkImage(light_image=thumb_bg,
                                          dark_image=thumb_bg,
                                          size=thumb_size)
                except Exception as e:
                    print(f"Error creating image thumbnail: {e}")
                    return self.create_generic_thumbnail("Image\nError", "darkred")

            elif category == 'video':
                return self.create_generic_thumbnail("Video", "#4a90e2")

            elif category == 'audio':
                return self.create_generic_thumbnail("Audio", "#e24a90")

            elif category == 'document':
                return self.create_generic_thumbnail("Doc", "#90e24a")

            elif category == 'data':
                return self.create_generic_thumbnail("Data", "#4ae290")

            else:
                return self.create_generic_thumbnail(ext[1:].upper() if ext else "File", "#808080")

        except Exception as e:
            print(f"Error creating thumbnail for {file_path}: {str(e)}")
            return self.create_generic_thumbnail("Error", "darkred")

    def create_generic_thumbnail(self, text, color="gray"):
        """Create a generic thumbnail with text"""
        thumb_size = (150, 150)
        img = Image.new('RGB', thumb_size, 'black')
        draw = ImageDraw.Draw(img)

        # Draw colored rectangle
        margin = 20
        draw.rectangle(
            [margin, margin, thumb_size[0]-margin, thumb_size[1]-margin],
            fill=color
        )

        # Add text
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (thumb_size[0] - text_width) // 2
        text_y = (thumb_size[1] - text_height) // 2

        draw.text((text_x, text_y), text, fill="white")

        return ctk.CTkImage(light_image=img, dark_image=img, size=thumb_size)

    def navigate_up(self):
        """Navigate to parent directory"""
        parent = os.path.dirname(self.current_dir)
        if os.path.exists(parent):
            self.current_dir = parent
            self.update_path_display()
            self.load_files()

    def navigate_to_path(self, event=None):
        """Navigate to entered path"""
        new_path = self.path_var.get()
        if os.path.exists(new_path):
            self.current_dir = os.path.abspath(new_path)
            self.update_path_display()
            self.load_files()
        else:
            messagebox.showerror("Error", "Invalid path")
            self.update_path_display()

    def update_path_display(self):
        """Update path display"""
        self.path_var.set(self.current_dir)

    def load_files(self):
        """Load files and folders with enhanced display"""
        # Clear existing display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()
        self.current_row = 0
        self.current_col = 0

        try:
            # Get directories and files
            entries = os.listdir(self.current_dir)
            folders = []
            files = []

            for entry in entries:
                full_path = os.path.join(self.current_dir, entry)
                if os.path.isdir(full_path):
                    folders.append(entry)
                else:
                    files.append(entry)

            # Sort folders and files separately
            folders.sort()
            files = self.sort_files(files)

            # Display folders first
            for folder in folders:
                self.create_folder_item(folder)

            # Then display files
            for file in files:
                self.create_file_item(file)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading directory: {str(e)}")

    def create_folder_item(self, folder_name):
        """Create folder display item"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(row=self.current_row, column=self.current_col,
                  padx=10, pady=10, sticky="nsew")

        # Create folder button with icon
        folder_button = ctk.CTkButton(
            frame,
            text="📁",
            command=lambda f=folder_name: self.enter_folder(f),
            width=150,
            height=150
        )
        folder_button.pack(pady=(5, 0))

        # Add folder name label
        label = ctk.CTkLabel(
            frame,
            text=folder_name,
            wraplength=140
        )
        label.pack(pady=(5, 5))

        # Update grid position
        self.current_col += 1
        if self.current_col >= self.max_cols:
            self.current_col = 0
            self.current_row += 1

    def create_file_item(self, file_name):
            """Create file display item with play toggle"""
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.grid(row=self.current_row, column=self.current_col,
                      padx=10, pady=10, sticky="nsew")

            file_path = os.path.join(self.current_dir, file_name)

            # Create thumbnail
            thumbnail = self.create_thumbnail(file_path)
            if thumbnail:
                # Determine if file is playable
                ext = os.path.splitext(file_path)[1].lower()
                is_playable = ext in self.file_categories['video']

                # Create buttons frame
                buttons_frame = ctk.CTkFrame(frame)
                buttons_frame.pack(fill="x", pady=(5, 0))

                # Create play toggle if file is playable
                if is_playable:
                    self.play_vars = getattr(self, 'play_vars', {})
                    self.play_vars[file_path] = tk.BooleanVar(value=True)

                    play_toggle = ctk.CTkSwitch(
                        buttons_frame,
                        text="Play Mode",
                        variable=self.play_vars[file_path],
                        width=60
                    )
                    play_toggle.pack(side="top", pady=2)

                # Create thumbnail button
                thumb_button = ctk.CTkButton(
                    frame,
                    image=thumbnail,
                    text="",
                    command=lambda path=file_path: self.on_file_click(path),
                    width=150,
                    height=150
                )
                thumb_button.pack(pady=(5, 0))

                # Add filename label
                label = ctk.CTkLabel(
                    frame,
                    text=file_name,
                    wraplength=140
                )
                label.pack(pady=(5, 5))

                # Add file size label
                size = os.path.getsize(file_path)
                size_text = self.format_file_size(size)
                size_label = ctk.CTkLabel(
                    frame,
                    text=size_text,
                    font=("Arial", 10)
                )
                size_label.pack(pady=(0, 5))

                # Store reference to thumbnail
                self.thumbnails.append(thumbnail)

            # Update grid position
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1

    def enter_folder(self, folder_name):
        """Enter selected folder"""
        new_path = os.path.join(self.current_dir, folder_name)
        if os.path.exists(new_path):
            self.current_dir = new_path
            self.update_path_display()
            self.load_files()

    def sort_files(self, files):
        """Sort files based on current criteria"""
        sort_key = self.sort_var.get()
        reverse = self.reverse_var.get()

        return sorted(
            files,
            key=lambda f: self.get_file_info(os.path.join(self.current_dir, f))[sort_key],
            reverse=reverse
        )

    def get_file_info(self, file_path):
        """Get file information for sorting"""
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path).lower(),
            'date': stat.st_mtime,
            'size': stat.st_size,
            'type': os.path.splitext(file_path)[1].lower()
        }

    def refresh_files(self):
        """Refresh file display with current sort settings"""
        self.load_files()

    def format_file_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def on_file_click(self, file_path):
        """Handle file selection with enhanced path handling and play mode"""
        if self.callback:
            # Create relative or absolute path based on selection
            relative_to_media = os.path.relpath(file_path, 'media_files')
            if relative_to_media.startswith('..'):
                # File is outside media_files - use absolute path
                final_path = file_path
            else:
                # File is inside media_files - use relative path
                final_path = os.path.join('media_files', relative_to_media)

            # Check if file is playable and play mode is enabled
            ext = os.path.splitext(file_path)[1].lower()
            is_playable = ext in self.file_categories['video']
            play_mode = is_playable and self.play_vars.get(file_path, tk.BooleanVar(value=True)).get()

            # Create appropriate directive
            if play_mode:
                self.callback(f"\\play \\file {final_path}")
            else:
                self.callback(f"\\file {final_path}")

        self.destroy()
#------------------------------------------------------------------------------------------
class PreambleEditor(ctk.CTkToplevel):
    def __init__(self, parent, current_preamble=None):
        super().__init__(parent)
        self.title("Preamble Editor")
        self.geometry("800x600")

        # Store the default preamble
        self.default_preamble = get_beamer_preamble(
            "Title", "Subtitle", "Author", "Institution", "Short Inst", "\\today"
        )

        # Create UI
        self.create_editor()
        self.create_toolbar()

        # Load current preamble if provided, else load default
        if current_preamble:
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', current_preamble)
        else:
            self.reset_to_default()

    def create_editor(self):
        """Create the preamble text editor"""
        # Editor frame
        editor_frame = ctk.CTkFrame(self)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Editor with syntax highlighting
        self.editor = ctk.CTkTextbox(
            editor_frame,
            wrap="none",
            font=("Courier", 12)
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Add syntax highlighting
        self.syntax_highlighter = BeamerSyntaxHighlighter(self.editor)

    def create_toolbar(self):
        """Create toolbar with editor controls"""
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=5)

        # Create buttons
        buttons = [
            ("Reset to Default", self.reset_to_default),
            ("Save Custom", self.save_custom),
            ("Load Custom", self.load_custom),
            ("Apply", self.apply_changes),
            ("Cancel", self.cancel_changes)
        ]

        for text, command in buttons:
            ctk.CTkButton(
                toolbar,
                text=text,
                command=command,
                width=100
            ).pack(side="left", padx=5)

    def reset_to_default(self):
        """Reset preamble to default"""
        if messagebox.askyesno("Reset Preamble",
                             "Are you sure you want to reset to default preamble?"):
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', self.default_preamble)
            self.syntax_highlighter.highlight()

    def save_custom(self):
        """Save current preamble as custom template"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tex",
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Save Custom Preamble"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get('1.0', 'end-1c'))
                messagebox.showinfo("Success", "Custom preamble saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving preamble: {str(e)}")

    def load_custom(self):
        """Load custom preamble template"""
        file_path = filedialog.askopenfilename(
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Load Custom Preamble"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.editor.delete('1.0', 'end')
                    self.editor.insert('1.0', content)
                    self.syntax_highlighter.highlight()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading preamble: {str(e)}")

    def apply_changes(self):
        """Apply preamble changes and close editor"""
        self.preamble = self.editor.get('1.0', 'end-1c')
        self.destroy()

    def cancel_changes(self):
        """Cancel changes and close editor"""
        self.preamble = None
        self.destroy()

    @staticmethod
    def edit_preamble(parent, current_preamble=None):
        """Static method to handle preamble editing"""
        editor = PreambleEditor(parent, current_preamble)
        editor.wait_window()
        return editor.preamble if hasattr(editor, 'preamble') else None
#------------------------------------------------------------------------------------------
class NotesToggleFrame(ctk.CTkFrame):
    """Frame containing notes display options with tooltips"""
    def __init__(self, parent, main_editor, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Store reference to main editor
        self.main_editor = main_editor

        # Notes mode variable
        self.notes_mode = tk.StringVar(value="both")

        # Create radio buttons for different notes modes
        modes = [
            ("PDF Only", "slides", "Hide all presentation notes"),
            ("Notes Only", "notes", "Show only presentation notes"),
            ("PDF with Notes", "both", "Show PDF with notes on second screen")
        ]

        # Create label
        label = ctk.CTkLabel(self, text="Notes Display:", anchor="w")
        label.pack(side="left", padx=5)
        self.create_tooltip(label, "Select how notes should appear in the final output")

        # Create radio buttons
        for text, value, tooltip in modes:
            btn = ctk.CTkRadioButton(
                self,
                text=text,
                variable=self.notes_mode,
                value=value
            )
            btn.pack(side="left", padx=10)
            self.create_tooltip(btn, tooltip)

    def get_notes_directive(self) -> str:
        """Return the appropriate beamer directive based on current mode"""
        mode = self.notes_mode.get()
        if mode == "slides":
            return "\\setbeameroption{hide notes}"
        elif mode == "notes":
            return "\\setbeameroption{show only notes}"
        else:  # both
            return "\\setbeameroption{show notes on second screen=right}"




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

        # Add terminal after other UI elements
        self.create_terminal()

        # Adjust grid weights to accommodate terminal
        self.grid_rowconfigure(1, weight=3)  # Main editor
        self.grid_rowconfigure(4, weight=1)  # Terminal
#--------------------------------------------------------------------------------------------------------------------
    def edit_preamble(self):
            """Open preamble editor"""
            # Get current preamble if exists
            current_preamble = get_beamer_preamble(
                self.presentation_info['title'],
                self.presentation_info['subtitle'],
                self.presentation_info['author'],
                self.presentation_info['institution'],
                self.presentation_info['short_institute'],
                self.presentation_info['date']
            )

            # Open preamble editor
            new_preamble = PreambleEditor.edit_preamble(self, current_preamble)

            if new_preamble is not None:
                # Store the custom preamble
                self.custom_preamble = new_preamble
                messagebox.showinfo("Success", "Preamble updated successfully!")


#--------------------------------------------------------------------------------------------------------------------
    def create_terminal(self) -> None:
        """Create a terminal/console widget"""
        self.terminal_frame = ctk.CTkFrame(self)
        self.terminal_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(4, weight=1)  # Make terminal expandable

        # Terminal header with controls
        header_frame = ctk.CTkFrame(self.terminal_frame)
        header_frame.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(header_frame, text="Compilation Output", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        # Control buttons
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(header_frame, text="Auto-scroll", variable=self.auto_scroll_var).pack(side="right", padx=5)

        ctk.CTkButton(header_frame, text="Clear",
                     command=self.clear_terminal).pack(side="right", padx=5)

        ctk.CTkButton(header_frame, text="Stop Compilation",
                     command=self.stop_compilation,
                     fg_color="red").pack(side="right", padx=5)

        # Terminal output text widget
        self.terminal = ctk.CTkTextbox(self.terminal_frame, height=150)
        self.terminal.pack(fill="both", expand=True, padx=2, pady=2)

        # Configure terminal appearance
        self.terminal._text_color = "white"
        self.terminal._fg_color = "black"
        self.terminal.configure(font=("Courier", 10))

        # Store process reference
        self.current_process = None

    def clear_terminal(self) -> None:
        """Clear terminal content"""
        self.terminal.delete('1.0', 'end')

    def stop_compilation(self) -> None:
        """Stop the current compilation process"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.write_to_terminal("\n[Compilation process terminated by user]\n", "red")
            except Exception as e:
                self.write_to_terminal(f"\n[Error terminating process: {str(e)}]\n", "red")
            finally:
                self.current_process = None

    def write_to_terminal(self, text: str, color: str = "white") -> None:
        """Write text to terminal with color"""
        self.terminal.insert('end', text)
        if color != "white":
            # Color the last inserted line
            last_line_start = self.terminal.index("end-1c linestart")
            last_line_end = self.terminal.index("end-1c")
            self.terminal.tag_add(color, last_line_start, last_line_end)
            self.terminal.tag_config(color, foreground=color)

        if self.auto_scroll_var.get():
            self.terminal.see('end')

        # Update the GUI
        self.update_idletasks()
#--------------------------------------------------------------------------------------------------------------------
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
        """Create top menu bar with added Get Source option"""
        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Left side buttons
        left_buttons = ctk.CTkFrame(self.menu_frame)
        left_buttons.pack(side="left", padx=5)

       # Add Preamble Editor button
        ctk.CTkButton(left_buttons, text="Edit Preamble",
                     command=self.edit_preamble).pack(side="left", padx=5)

        ctk.CTkButton(left_buttons, text="Presentation Settings",
                     command=self.show_settings_dialog).pack(side="left", padx=5)

        # Add Get Source button
        ctk.CTkButton(left_buttons, text="Get Source",
                     command=self.get_source_from_tex).pack(side="left", padx=5)

        # Right side buttons (existing code)
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

    def get_source_from_tex(self) -> None:
        """Convert a tex file back to source text format"""
        tex_file = filedialog.askopenfilename(
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Select TeX File to Convert"
        )

        if not tex_file:
            return

        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract slides
            slides = self.extract_slides_from_tex(content)

            if not slides:
                messagebox.showwarning("Warning", "No slides found in the TeX file!")
                return

            # Create output text file
            output_file = os.path.splitext(tex_file)[0] + '_source.txt'

            with open(output_file, 'w', encoding='utf-8') as f:
                # Extract and write presentation info
                title_match = re.search(r'\\title{([^}]*)}', content)
                subtitle_match = re.search(r'\\subtitle{([^}]*)}', content)
                author_match = re.search(r'\\author{([^}]*)}', content)
                institute_match = re.search(r'\\institute{\\textcolor{[^}]*}{([^}]*)}', content)

                if title_match:
                    f.write(f"\\title{{{title_match.group(1)}}}\n")
                if subtitle_match:
                    f.write(f"\\subtitle{{{subtitle_match.group(1)}}}\n")
                if author_match:
                    f.write(f"\\author{{{author_match.group(1)}}}\n")
                if institute_match:
                    f.write(f"\\institute{{{institute_match.group(1)}}}\n")

                f.write("\\date{\\today}\n\n")

                # Write slides
                for slide in slides:
                    f.write(f"\\title {slide['title']}\n")
                    f.write("\\begin{Content}")
                    if slide['media']:
                        f.write(f" {slide['media']}")
                    f.write("\n")

                    for item in slide['content']:
                        f.write(f"{item}\n")

                    f.write("\\end{Content}\n\n")

                f.write("\\end{document}")

            messagebox.showinfo("Success", f"Source file created: {output_file}")

            # Ask if user wants to load the generated source file
            if messagebox.askyesno("Load File", "Would you like to load the generated source file?"):
                self.load_file(output_file)

        except Exception as e:
            messagebox.showerror("Error", f"Error converting TeX file:\n{str(e)}")
            print(f"Error details: {str(e)}")


    def extract_presentation_info(self, content: str) -> dict:
        """Extract presentation information from document body only"""
        info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': '',
            'short_institute': '',
            'date': '\\today'
        }

        import re

        # First isolate the document body
        doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
        if doc_match:
            document_content = doc_match.group(1).strip()

            # Look for title frame content
            title_frame = re.search(r'\\begin{frame}.*?\\titlepage.*?\\end{frame}',
                                  document_content,
                                  re.DOTALL)
            if title_frame:
                # Extract information from the title frame
                for key in info.keys():
                    pattern = f"\\\\{key}{{(.*?)}}"
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        # Clean up LaTeX formatting
                        value = match.group(1).strip()
                        value = re.sub(r'\\textcolor{[^}]*}{([^}]*)}', r'\1', value)
                        value = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', value)
                        info[key] = value

        return info

    def extract_slides_from_tex(self, content: str) -> list:
        """Extract slides from TeX content, with correct titles and media paths"""
        slides = []
        import re

        # First isolate the document body
        doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
        if not doc_match:
            print("Could not find document body")
            return slides

        document_content = doc_match.group(1).strip()

        # Find all frame blocks in the document body
        frame_blocks = re.finditer(
            r'\\begin{frame}\s*(?:\{\\Large\\textbf{([^}]*?)}\}|\{([^}]*)\})?(.*?)\\end{frame}',
            document_content,
            re.DOTALL
        )

        for block in frame_blocks:
            # Extract title from different possible patterns
            title = block.group(1) if block.group(1) else block.group(2) if block.group(2) else ""
            frame_content = block.group(3).strip() if block.group(3) else ""

            # If no title found in frame declaration, look for frametitle
            if not title:
                title_match = re.search(r'\\frametitle{([^}]*)}', frame_content)
                if title_match:
                    title = title_match.group(1)

            # Clean up title - remove \Large, \textbf, etc.
            if title:
                title = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', title)
            else:
                title = "Untitled Slide"

            # Skip title frame
            if "\\titlepage" in frame_content:
                continue
            # Extract note content
            notes = []
            note_match = re.search(r'\\note{(.*?)}', frame_content, re.DOTALL)
            if note_match:
                note_content = note_match.group(1)
                # Extract items from note's itemize environment
                note_items = re.finditer(r'\\item\s*(.*?)(?=\\item|\s*\\end{itemize}|$)',
                                       note_content,
                                       re.DOTALL)
                for item in note_items:
                    note_text = item.group(1).strip()
                    if note_text:
                        notes.append(f"• {note_text}")
            # Extract content and media
            content_lines = []
            media = ""

            # Look for media in columns environment
            media_match = re.search(r'\\includegraphics\[.*?\]{([^}]*)}', frame_content)
            if media_match:
                # Extract filename and ensure it has media_files prefix
                filename = media_match.group(1)
                if not filename.startswith('media_files/'):
                    filename = os.path.basename(filename)  # Remove any existing path
                    filename = f"media_files/{filename}"  # Add media_files prefix
                media = f"\\file {filename}"

            # Look for movie elements
            movie_match = re.search(r'\\movie(?:\[[^\]]*\])?{[^}]*}{([^}]*)}', frame_content)
            if movie_match:
                filename = movie_match.group(1)
                if not filename.startswith('media_files/'):
                    filename = os.path.basename(filename)
                    filename = f"media_files/{filename}"
                media = f"\\play {filename}"

            # Extract itemize content
            itemize_blocks = re.finditer(r'\\begin{itemize}(.*?)\\end{itemize}', frame_content, re.DOTALL)
            for itemize in itemize_blocks:
                items = re.finditer(r'\\item\s*(.*?)(?=\\item|\s*\\end{itemize}|$)',
                                  itemize.group(1),
                                  re.DOTALL)
                for item in items:
                    content_line = item.group(1).strip()
                    if content_line:
                        # Clean up the content line
                        content_line = content_line.replace('\\&', '&')
                        content_line = re.sub(r'\\textcolor{[^}]*}{([^}]*)}', r'\1', content_line)
                        content_line = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', content_line)
                        if not content_line.startswith('-'):
                            content_line = f"- {content_line}"
                        content_lines.append(content_line)

            # Only add non-empty slides
            if content_lines or media:
                     # Add both content and notes to slide data
                    slides.append({
                        'title': title.strip(),
                        'media': media,
                        'content': content_lines,
                        'notes': notes
                    })

        return slides
#--------------------------------------------------------------------------------------
    def create_sidebar(self) -> None:
        """Create sidebar with slide list and controls with enhanced navigation"""
        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

        # Slide list label
        ctk.CTkLabel(self.sidebar, text="Slides",
                    font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5, pady=5)

        # Slide list with scroll
        self.slide_list = ctk.CTkTextbox(self.sidebar, width=180, height=400)
        self.slide_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Enhanced bindings for navigation
        self.slide_list.bind('<Button-1>', self.on_slide_select)
        self.slide_list.bind('<Up>', self.navigate_slides)
        self.slide_list.bind('<Down>', self.navigate_slides)
        self.slide_list.bind('<Left>', self.navigate_slides)
        self.slide_list.bind('<Right>', self.navigate_slides)
        self.bind('<Control-Up>', lambda e: self.move_slide(-1))
        self.bind('<Control-Down>', lambda e: self.move_slide(1))

        # Focus binding to enable keyboard navigation
        self.slide_list.bind('<FocusIn>', self.on_list_focus)
        self.slide_list.bind('<FocusOut>', self.on_list_unfocus)

        # Slide control buttons (keeping existing functionality)
        button_data = [
            ("New Slide", self.new_slide),
            ("Duplicate Slide", self.duplicate_slide),
            ("Delete Slide", self.delete_slide),
            ("Move Up", lambda: self.move_slide(-1)),
            ("Move Down", lambda: self.move_slide(1))
        ]

        for i, (text, command) in enumerate(button_data, start=2):
            ctk.CTkButton(self.sidebar, text=text,
                         command=command).grid(row=i, column=0, padx=5, pady=5)

    def navigate_slides(self, event) -> None:
        """Handle keyboard navigation between slides"""
        if not self.slides:
            return "break"

        # Save current slide
        self.save_current_slide()

        # Calculate new index based on key
        new_index = self.current_slide_index
        if event.keysym in ['Up', 'Left']:
            new_index = max(0, self.current_slide_index - 1)
        elif event.keysym in ['Down', 'Right']:
            new_index = min(len(self.slides) - 1, self.current_slide_index + 1)

        # Update if changed
        if new_index != self.current_slide_index:
            self.current_slide_index = new_index
            self.load_slide(new_index)
            self.update_slide_list()

            # Ensure selected slide is visible
            self.slide_list.see(f"{new_index + 1}.0")

            # Highlight current line
            self.highlight_current_slide()

        return "break"  # Prevent default handling

    def highlight_current_slide(self) -> None:
        """Highlight the currently selected slide in the list"""
        # Remove previous highlighting
        self.slide_list.tag_remove('selected', '1.0', 'end')

        # Add new highlighting
        if self.current_slide_index >= 0:
            start = f"{self.current_slide_index + 1}.0"
            end = f"{self.current_slide_index + 1}.end"
            self.slide_list.tag_add('selected', start, end)
            self.slide_list.tag_config('selected', background='#2F3542')

    def on_list_focus(self, event) -> None:
        """Handle slide list focus"""
        self.highlight_current_slide()
        # Visual feedback that list is focused
        self.slide_list.configure(border_color="#4ECDC4")

    def on_list_unfocus(self, event) -> None:
        """Handle slide list losing focus"""
        # Remove focus visual feedback
        self.slide_list.configure(border_color="")

    def update_slide_list(self) -> None:
        """Update slide list with improved visual feedback"""
        self.slide_list.delete('1.0', 'end')
        for i, slide in enumerate(self.slides):
            prefix = "→ " if i == self.current_slide_index else "  "
            self.slide_list.insert('end', f"{prefix}Slide {i+1}: {slide['title']}\n")

        # Refresh highlighting
        self.highlight_current_slide()

    def duplicate_slide(self) -> None:
            """Duplicate the current slide"""
            if self.current_slide_index >= 0:
                # Save the current slide first to ensure we have the latest changes
                self.save_current_slide()

                # Create a deep copy of the current slide
                current_slide = self.slides[self.current_slide_index]
                new_slide = {
                    'title': f"{current_slide['title']} (Copy)",
                    'media': current_slide['media'],
                    'content': current_slide['content'].copy()  # Create a new list with the same content
                }

                # Insert the new slide after the current slide
                insert_position = self.current_slide_index + 1
                self.slides.insert(insert_position, new_slide)

                # Update the current slide index to point to the new slide
                self.current_slide_index = insert_position

                # Update the UI
                self.update_slide_list()
                self.load_slide(self.current_slide_index)

                # Show confirmation message
                messagebox.showinfo("Success", "Slide duplicated successfully!")
            else:
                messagebox.showwarning("Warning", "No slide to duplicate!")
#---------------------------------------------------------------------------------------------------
    def create_main_editor(self) -> None:
        """Create main editor area with content and notes sections"""
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

        button_data = [
            ("Local File", self.browse_media, "Browse local media files"),
            ("YouTube", self.youtube_dialog, "Add YouTube video"),
            ("Search Images", self.search_images, "Search for images online"),
            ("No Media", lambda: self.media_entry.insert(0, "\\None"), "Create slide without media")
        ]

        for text, command, tooltip in button_data:
            btn = ctk.CTkButton(media_buttons, text=text, command=command)
            btn.pack(side="left", padx=2)
            self.create_tooltip(btn, tooltip)

        # Create editors container
        editors_frame = ctk.CTkFrame(self.editor_frame)
        editors_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Content editor section
        content_frame = ctk.CTkFrame(editors_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        content_label_frame = ctk.CTkFrame(content_frame)
        content_label_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(content_label_frame, text="Content:").pack(side="left", padx=5)

        self.content_editor = ctk.CTkTextbox(content_frame, height=200)
        self.content_editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Notes section
        notes_frame = ctk.CTkFrame(self.editor_frame)
        notes_frame.pack(fill="both", expand=True, padx=5, pady=5)

        notes_header = ctk.CTkFrame(notes_frame)
        notes_header.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(notes_header, text="Presentation Notes:").pack(side="left", padx=5)

        # Notes control buttons on the right
        notes_buttons = ctk.CTkFrame(notes_header)
        notes_buttons.pack(side="right", padx=5)

        # Initialize notes mode
        self.notes_mode = tk.StringVar(value="both")
        self.notes_buttons = {}

        # Define button configurations
        buttons_config = [
            ("slides", "Slides Only", "Generate slides without notes", "#2B87BB", "#1B5577"),
            ("notes", "Notes Only", "Generate notes only", "#27AE60", "#1A7340"),
            ("both", "Slides + Notes", "Generate slides with notes", "#8E44AD", "#5E2D73")
        ]

        # Create the three buttons for notes control
        for mode, text, tooltip, active_color, hover_color in buttons_config:
            btn = ctk.CTkButton(
                notes_buttons,
                text=text,
                command=lambda m=mode: self.set_notes_mode(m),
                width=100,
                fg_color=active_color if self.notes_mode.get() == mode else "gray",
                hover_color=hover_color
            )
            btn.pack(side="left", padx=2)
            self.create_tooltip(btn, tooltip)

            # Store button reference with its colors
            self.notes_buttons[mode] = {
                'button': btn,
                'active_color': active_color,
                'hover_color': hover_color
            }

        self.notes_editor = ctk.CTkTextbox(notes_frame, height=150)
        self.notes_editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize syntax highlighters
        self.syntax_highlighter = BeamerSyntaxHighlighter(self.content_editor)
        self.notes_highlighter = BeamerSyntaxHighlighter(self.notes_editor)

        # Set initial button colors
        self.update_notes_buttons(self.notes_mode.get())

    def set_notes_mode(self, mode: str) -> None:
        """Set notes mode and update UI"""
        self.notes_mode.set(mode)
        self.update_notes_buttons(mode)

        # Update notes editor state
        if mode == "slides":
            self.notes_editor.configure(state="disabled")
        else:
            self.notes_editor.configure(state="normal")

    def update_notes_buttons(self, active_mode: str) -> None:
        """Update button colors based on active mode"""
        for mode, btn_info in self.notes_buttons.items():
            if mode == active_mode:
                btn_info['button'].configure(
                    fg_color=btn_info['active_color'],
                    hover_color=btn_info['hover_color']
                )
            else:
                btn_info['button'].configure(
                    fg_color="gray",
                    hover_color="#4A4A4A"
                )

    def create_toolbar(self) -> None:
        """Create main editor toolbar without notes controls"""
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Basic file operations buttons
        buttons = [
            ("New", self.new_file, "Create new presentation"),
            ("Open", self.open_file, "Open existing presentation"),
            ("Save", self.save_file, "Save current presentation"),
            ("Convert to TeX", self.convert_to_tex, "Convert to LaTeX format"),
            ("Generate PDF", self.generate_pdf, "Generate PDF file"),
            ("Preview PDF", self.preview_pdf, "View generated PDF"),
            ("Export to Overleaf", self.create_overleaf_zip, "Create Overleaf-compatible zip")
        ]

        for text, command, tooltip in buttons:
            if text == "Export to Overleaf":
                btn = ctk.CTkButton(
                    self.toolbar,
                    text=text,
                    command=command,
                    width=120,
                    fg_color="#47A141",
                    hover_color="#2E8B57"
                )
            else:
                btn = ctk.CTkButton(
                    self.toolbar,
                    text=text,
                    command=command,
                    width=100
                )
            btn.pack(side="left", padx=5)
            self.create_tooltip(btn, tooltip)
#------------------------------------------------------------------------------------------------------



    def on_notes_mode_change(self, mode: str) -> None:
        """Handle notes mode change"""
        self.notes_mode.set(mode)

        # Update button colors
        for btn in self.mode_buttons:
            if btn.mode == mode:
                btn.configure(fg_color=btn.active_color)
            else:
                btn.configure(fg_color="gray")

        # Configure editor state
        if mode == "slides":
            self.notes_editor.configure(state="disabled")
        else:
            self.notes_editor.configure(state="normal")



    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1,
                           font=("Arial", 10))
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.tooltip_timer = self.after(2000, hide_tooltip)

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                if hasattr(widget, 'tooltip_timer'):
                    self.after_cancel(widget.tooltip_timer)

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def generate_odp(self) -> None:
        """Generate ODP presentation with automatic TEX generation if needed"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            #self.save_file()  # Save current state to ensure latest content

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Clear terminal
            self.clear_terminal()
            self.write_to_terminal("Starting ODP generation process...\n")

            # Check if TEX file exists and generate if needed
            if not os.path.exists(tex_file):
                self.write_to_terminal("TEX file not found. Generating from source...\n")
                try:
                    from BeamerSlideGenerator import process_input_file
                    process_input_file(self.current_file, tex_file)
                    self.write_to_terminal("✓ TEX file generated successfully\n", "green")
                except Exception as e:
                    self.write_to_terminal(f"✗ Error generating TEX file: {str(e)}\n", "red")
                    raise Exception("TEX generation failed")

            # Convert TEX to ODP
            self.write_to_terminal("Converting TEX to ODP...\n")
            try:
                #from Beam2odp import BeamerToODP
                converter = BeamerToODP(tex_file)
                self.write_to_terminal("Parsing TEX content...\n")
                converter.parse_input()

                self.write_to_terminal("Generating ODP file...\n")
                odp_file = converter.generate_odp()

                if odp_file and os.path.exists(odp_file):
                    self.write_to_terminal("✓ ODP file generated successfully!\n", "green")

                    # Ask to open the generated file
                    if messagebox.askyesno("Success",
                                         "ODP presentation generated successfully! Would you like to open it?"):
                        if sys.platform.startswith('win'):
                            os.startfile(odp_file)
                        elif sys.platform.startswith('darwin'):
                            subprocess.run(['open', odp_file])
                        else:
                            subprocess.run(['xdg-open', odp_file])
                else:
                    self.write_to_terminal("✗ Error: No output file was generated\n", "red")

            except Exception as e:
                error_text = f"✗ Error in ODP conversion: {str(e)}\n"
                error_text += "Detailed error information:\n"
                error_text += traceback.format_exc()
                self.write_to_terminal(error_text, "red")
                raise Exception("ODP conversion failed")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating ODP presentation:\n{str(e)}")
            print(f"Error details: {str(e)}")
            traceback.print_exc()

    def get_required_media_files(self, tex_content: str) -> set:
        """Parse TEX file to identify all required media files including multimedia content and previews"""
        required_files = set()

        # Regular expressions for different media references
        patterns = {
            'images': [
                r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}',    # Standard images
                r'\\pgfimage(?:\[.*?\])?\{([^}]+)\}',          # PGF images
                r'media_files/([^}]+_preview\.png)'             # Preview images
            ],
            'video': [
                r'\\movie(?:\[.*?\])?\{.*?\}\{\.?/?media_files/([^}]+)\}',  # Movie elements (handle ./ prefix)
                r'\\href\{run:([^}]+)\}',                       # Runnable media links
                r'\\movie\[.*?\]\{.*?\}\{([^}]+)\}'            # Movie with options
            ],
            'animations': [
                r'\\animategraphics(?:\[.*?\])?\{[^}]*\}\{([^}]+)\}',  # Animated graphics
                r'\\animate(?:\[.*?\])?\{[^}]*\}\{([^}]+)\}'           # General animations
            ],
            'audio': [
                r'\\sound(?:\[.*?\])?\{.*?\}\{([^}]+)\}',      # Sound elements
                r'\\audiofile\{([^}]+)\}'                       # Audio files
            ],
            'general_media': [
                r'\\file\s+media_files/([^\s}]+)',             # General media files
                r'\\play\s+\\file\s+media_files/([^\s}]+)',    # Playable media
                r'\\mediapath\{([^}]+)\}'                       # Media path references
            ]
        }

        self.write_to_terminal("\nAnalyzing required media files:\n")

        # Find all media references
        for media_type, pattern_list in patterns.items():
            self.write_to_terminal(f"\nChecking {media_type} references:\n")
            for pattern in pattern_list:
                matches = re.finditer(pattern, tex_content)
                for match in matches:
                    filepath = match.group(1)
                    # Clean up the path
                    filepath = filepath.replace('media_files/', '')
                    filepath = filepath.replace('./', '')  # Remove any ./ prefix
                    filepath = filepath.strip()

                    # Add the file to required files
                    required_files.add(filepath)
                    self.write_to_terminal(f"  ✓ Found: {filepath}\n", "green")

                    # If this is a preview image, also add the corresponding video
                    if filepath.endswith('_preview.png'):
                        base_video_name = filepath.replace('_preview.png', '.mp4')
                        required_files.add(base_video_name)
                        self.write_to_terminal(f"  ✓ Added corresponding video: {base_video_name}\n", "green")

                    # If this is a video, check for its preview image
                    if filepath.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        preview_name = filepath.rsplit('.', 1)[0] + '_preview.png'
                        if preview_name not in required_files:
                            required_files.add(preview_name)
                            self.write_to_terminal(f"  ✓ Added corresponding preview: {preview_name}\n", "green")

        return required_files

    def verify_media_files(self, required_files: set) -> tuple:
        """Verify existence of required media files and classify them"""
        verified_files = set()
        missing_files = set()
        media_types = {
            'images': [],
            'videos': [],
            'audio': [],
            'animations': [],
            'other': []
        }

        for filepath in required_files:
            full_path = os.path.join('media_files', filepath)
            if os.path.exists(full_path):
                verified_files.add(filepath)
                # Classify file by extension
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.pdf', '.eps']:
                    media_types['images'].append(filepath)
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
                    media_types['videos'].append(filepath)
                elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                    media_types['audio'].append(filepath)
                elif ext in ['.gif', '.webp']:
                    media_types['animations'].append(filepath)
                else:
                    media_types['other'].append(filepath)
            else:
                missing_files.add(filepath)

        return verified_files, missing_files, media_types

    def create_manifest(self, tex_file: str, verified_files: set, missing_files: set, media_types: dict) -> str:
        """Create detailed manifest content"""
        manifest_content = [
            "# Project Media Files Manifest",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Project Files:",
            f"- {os.path.basename(tex_file)} (Main TeX file)",
            "\n## Media Files by Type:"
        ]

        # Add categorized media files
        for media_type, files in media_types.items():
            if files:
                manifest_content.extend([
                    f"\n### {media_type.title()}:",
                    *[f"- media_files/{file}" for file in sorted(files)]
                ])

        # Add missing files section if any
        if missing_files:
            manifest_content.extend([
                "\n## Missing Files (Please Check):",
                *[f"- {file}" for file in sorted(missing_files)]
            ])

        manifest_content.extend([
            "\n## File Statistics:",
            f"Total Files: {len(verified_files) + len(missing_files)}",
            f"Successfully Included: {len(verified_files)}",
            f"Missing: {len(missing_files)}"
        ])

        return '\n'.join(manifest_content)

    def create_overleaf_zip(self) -> None:
        """Create a zip file compatible with Overleaf containing tex and all required media files"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # First ensure current state is saved and tex is generated
            #self.save_file()

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Clear terminal and show progress
            self.clear_terminal()
            self.write_to_terminal("Creating Overleaf-compatible zip file...\n")

            # Convert to tex if not already done
            if not os.path.exists(tex_file):
                self.write_to_terminal("Generating TeX file...\n")
                from BeamerSlideGenerator import process_input_file
                process_input_file(self.current_file, tex_file)
                self.write_to_terminal("✓ TeX file generated successfully\n", "green")

            # Read TEX content and identify required files
            with open(tex_file, 'r', encoding='utf-8') as f:
                tex_content = f.read()

            # Create the progress dialog
            self.update_idletasks()  # Ensure main window is updated
            progress = self.create_progress_dialog(
                "Creating Zip File",
                "Analyzing required files..."
            )

            try:
                # Analyze and verify media files
                required_files = self.get_required_media_files(tex_content)
                verified_files, missing_files, media_types = self.verify_media_files(required_files)

                # Create zip file
                zip_filename = base_filename + '_overleaf.zip'
                total_files = len(verified_files) + 1  # +1 for tex file
                processed_files = 0

                progress.update_progress(0, "Creating zip file...")

                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add the tex file
                    progress.update_progress(
                        (processed_files / total_files) * 100,
                        "Adding TeX file..."
                    )
                    zipf.write(tex_file, os.path.basename(tex_file))
                    processed_files += 1
                    self.write_to_terminal(f"✓ Added: {os.path.basename(tex_file)}\n", "green")

                    # Add verified media files
                    self.write_to_terminal("\nAdding media files:\n")
                    for filename in verified_files:
                        file_path = os.path.join('media_files', filename)
                        progress.update_progress(
                            (processed_files / total_files) * 100,
                            f"Adding {filename}..."
                        )

                        # Ensure the media_files directory exists in the zip
                        if processed_files == 1:  # First media file
                            zipf.writestr('media_files/.keep', '')  # Create empty file to ensure directory exists

                        zipf.write(file_path, os.path.join('media_files', filename))
                        self.write_to_terminal(f"✓ Added: {filename}\n", "green")
                        processed_files += 1

                    # Create detailed manifest
                    manifest_content = self.create_manifest(
                        tex_file, verified_files, missing_files, media_types
                    )
                    zipf.writestr('manifest.txt', manifest_content)

                progress.update_progress(100, "Complete!")
                time.sleep(0.5)  # Brief pause to show completion

                # Show completion message with details
                message = [f"Zip file created successfully!"]

                # Add statistics
                stats = []
                total_files = sum(len(files) for files in media_types.values())
                if total_files > 0:
                    stats.extend([
                        "",
                        "Media files included:",
                        *[f"- {media_type.title()}: {len(files)} files"
                          for media_type, files in media_types.items() if files]
                    ])

                # Add warnings for missing files
                if missing_files:
                    stats.extend([
                        "",
                        f"Warning: {len(missing_files)} required files were missing.",
                        "Check manifest.txt in the zip file for details."
                    ])

                # Add total size
                try:
                    zip_size = os.path.getsize(zip_filename)
                    stats.append("")
                    stats.append(f"Total zip size: {self.format_file_size(zip_size)}")
                except OSError:
                    pass

                message.extend(stats)
                message.append("\nWould you like to open the containing folder?")

                # Close progress dialog before showing message
                progress.close()

                if messagebox.askyesno("Success", "\n".join(message)):
                    # Open the folder containing the zip file
                    if sys.platform.startswith('win'):
                        os.system(f'explorer /select,"{zip_filename}"')
                    elif sys.platform.startswith('darwin'):
                        subprocess.run(['open', '-R', zip_filename])
                    else:
                        subprocess.run(['xdg-open', os.path.dirname(zip_filename)])

            except Exception as e:
                if 'progress' in locals():
                    progress.close()
                raise

        except Exception as e:
            error_msg = f"Error creating zip file: {str(e)}\n"
            self.write_to_terminal(f"✗ {error_msg}", "red")
            traceback.print_exc()  # Print full traceback to help with debugging
            messagebox.showerror("Error", f"Error creating zip file:\n{str(e)}")

    def format_file_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def create_progress_dialog(self, title: str, message: str) -> 'ProgressDialog':
        """Create a progress dialog window"""
        class ProgressDialog:
            def __init__(self, parent, title, message):
                self.window = ctk.CTkToplevel(parent)
                self.window.title(title)
                self.window.geometry("300x150")
                self.window.transient(parent)

                # Center the window
                self.window.update_idletasks()
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                x = (self.window.winfo_screenwidth() // 2) - (width // 2)
                y = (self.window.winfo_screenheight() // 2) - (height // 2)
                self.window.geometry(f'+{x}+{y}')

                self.message = ctk.CTkLabel(self.window, text=message)
                self.message.pack(pady=10)

                self.progress = ctk.CTkProgressBar(self.window)
                self.progress.pack(pady=10, padx=20, fill="x")
                self.progress.set(0)

                self.progress_text = ctk.CTkLabel(self.window, text="0%")
                self.progress_text.pack(pady=5)

                # Wait for window to be visible before grabbing
                self.window.wait_visibility()
                self.window.grab_set()

                # Keep dialog on top
                self.window.lift()
                self.window.focus_force()

            def update_progress(self, value: float, message: str = None) -> None:
                """Update progress bar and message"""
                try:
                    if self.window.winfo_exists():
                        self.progress.set(value / 100)
                        self.progress_text.configure(text=f"{value:.1f}%")
                        if message:
                            self.message.configure(text=message)
                        self.window.update()
                except tk.TclError:
                    pass  # Window might have been closed

            def close(self) -> None:
                """Close the progress dialog"""
                try:
                    if self.window.winfo_exists():
                        self.window.grab_release()
                        self.window.destroy()
                except tk.TclError:
                    pass  # Window might have been closed

        return ProgressDialog(self, title, message)



    def open_presentation(self, file_path):
        """Open the generated presentation with appropriate application"""
        try:
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            self.write_to_terminal(f"Error opening presentation: {str(e)}\n", "red")
            messagebox.showerror("Error",
                               f"Error opening presentation:\n{str(e)}")

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
        """Save presentation in BeamerSlideGenerator-compatible format"""
        if not self.current_file:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.current_file = filename
            else:
                return

        # Save current slide before generating content
        self.save_current_slide()

        try:
            # Get preamble from BeamerSlideGenerator
            from BeamerSlideGenerator import get_beamer_preamble
            content = get_beamer_preamble(
                self.presentation_info['title'],
                self.presentation_info['subtitle'],
                self.presentation_info['author'],
                self.presentation_info['institution'],
                self.presentation_info['short_institute'],
                self.presentation_info['date']
            )

            # Add slides in BeamerSlideGenerator's expected format
            for slide in self.slides:
                content += f"\\title {slide['title']}\n"
                content += "\\begin{Content}"
                if slide['media']:
                    content += f" {slide['media']}"
                content += "\n"

                # Format content items
                for item in slide['content']:
                    if item.strip():
                        # Ensure proper bullet point format
                        if not item.startswith('-'):
                            item = f"- {item}"
                        content += f"{item}\n"

                content += "\\end{Content}\n\n"
                # Add notes if present
                if 'notes' in slide and slide['notes']:
                    content += "\\begin{Notes}\n"
                    for note in slide['notes']:
                        content += f"{note}\n"
                    content += "\\end{Notes}\n"

            content += "\\end{document}"

            # Save to text file
            with open(self.current_file, 'w') as f:
                f.write(content)

            print(f"File saved successfully: {self.current_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Error saving file:\n{str(e)}")
            print(f"Error details: {str(e)}")

    def generate_pdf(self) -> None:
        """Generate PDF with text to TeX conversion and compilation"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Clear terminal
            self.clear_terminal()

            # Step 1: Convert text to TeX using our proper conversion function
            self.write_to_terminal("Step 1: Converting text to TeX...\n")
            self.convert_to_tex()  # This will handle notes mode correctly

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Step 2: First pdflatex pass
            self.write_to_terminal("\nStep 2: First pdflatex pass...\n")
            success = self.run_pdflatex(tex_file)

            if success:
                # Step 3: Second pdflatex pass for references
                self.write_to_terminal("\nStep 3: Second pdflatex pass...\n")
                success = self.run_pdflatex(tex_file)

                if success:
                    self.write_to_terminal("\n✓ PDF generated successfully!\n", "green")

                    # Ask if user wants to view the PDF
                    if messagebox.askyesno("Open PDF", "Would you like to view the generated PDF?"):
                        self.preview_pdf()
                else:
                    self.write_to_terminal("\n✗ Error in second pdflatex pass\n", "red")
            else:
                self.write_to_terminal("\n✗ Error in first pdflatex pass\n", "red")

        except Exception as e:
            self.write_to_terminal(f"\n✗ Error: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error generating PDF:\n{str(e)}")


    def run_pdflatex(self, tex_file: str) -> bool:
        """Run pdflatex process with interactive output"""
        try:
            # Prepare command
            cmd = ['pdflatex', '-interaction=nonstopmode', tex_file]

            # Start process with pipe for output
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.path.dirname(tex_file) or '.'
            )

            # Read output in real-time
            while True:
                line = self.current_process.stdout.readline()
                if not line and self.current_process.poll() is not None:
                    break

                if line:
                    # Color error messages in red
                    if any(err in line for err in ['Error:', '!', 'Fatal error']):
                        self.write_to_terminal(line, "red")
                    # Color warnings in yellow
                    elif 'Warning' in line:
                        self.write_to_terminal(line, "yellow")
                    else:
                        self.write_to_terminal(line)

            # Get return code and cleanup
            return_code = self.current_process.wait()
            self.current_process = None

            return return_code == 0

        except Exception as e:
            self.write_to_terminal(f"\nProcess error: {str(e)}\n", "red")
            if self.current_process:
                self.current_process = None
            return False

    def preview_pdf(self) -> None:
        """Preview generated PDF using system default PDF viewer"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save and generate PDF first!")
            return

        pdf_file = os.path.splitext(self.current_file)[0] + '.pdf'
        if os.path.exists(pdf_file):
            if sys.platform.startswith('win'):
                os.startfile(pdf_file)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', pdf_file])
            else:
                subprocess.run(['xdg-open', pdf_file])
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
        """Load slide data including notes"""
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

        self.notes_editor.delete('1.0', 'end')
        if 'notes' in slide:
            for note in slide['notes']:
                self.notes_editor.insert('end', f"{note}\n")

        if self.syntax_highlighter.active:
            self.syntax_highlighter.highlight()
            self.notes_highlighter.highlight()

    def save_current_slide(self) -> None:
        """Save current slide data including notes"""
        if self.current_slide_index >= 0:
            self.slides[self.current_slide_index] = {
                'title': self.title_entry.get(),
                'media': self.media_entry.get(),
                'content': [line for line in self.content_editor.get('1.0', 'end-1c').split('\n') if line.strip()],
                'notes': [line for line in self.notes_editor.get('1.0', 'end-1c').split('\n') if line.strip()]
            }

    def clear_editor(self) -> None:
        """Clear editor fields"""
        self.title_entry.delete(0, 'end')
        self.media_entry.delete(0, 'end')
        self.content_editor.delete('1.0', 'end')

    # Media Handling
    def browse_media(self) -> None:
        """Browse media files with thumbnail preview"""
        def on_file_selected(media_path):
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, media_path)

        browser = FileThumbnailBrowser(self, callback=on_file_selected)
        browser.transient(self)
        browser.grab_set()
        self.wait_window(browser)

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

    def generate_tex_content(self) -> str:
        """Generate complete tex file content with proper notes handling"""
        # Get base content
        if hasattr(self, 'custom_preamble'):
            content = self.custom_preamble
        else:
            content = get_beamer_preamble(
                self.presentation_info['title'],
                self.presentation_info['subtitle'],
                self.presentation_info['author'],
                self.presentation_info['institution'],
                self.presentation_info['short_institute'],
                self.presentation_info['date']
            )

        # Modify preamble for notes configuration
        content = self.modify_preamble_for_notes(content)
        print(content)
        # Add slides with appropriate notes handling
        for slide in self.slides:
            content += f"\\begin{frame}\n"
            content += f"\\frametitle{{{slide['title']}}}\n"

            if slide['media']:
                content += f"{slide['media']}\n"

            for item in slide['content']:
                if item.strip():
                    content += f"{item}\n"

            content += "\\end{frame}\n"

            # Add notes if not in slides_only mode
            if self.notes_mode.get() != "slides_only" and 'notes' in slide and slide['notes']:
                content += "\\note{\n\\begin{itemize}\n"
                for note in slide['notes']:
                    if note.strip():
                        note = note.lstrip('•- ').strip()
                        content += f"\\item {note}\n"
                content += "\\end{itemize}\n}\n"

            content += "\n"

        content += "\\end{document}\n"
        return content

    def modify_preamble_for_notes(self, tex_content: str) -> str:
        """Modify the preamble based on current notes mode"""
        mode = self.notes_mode.get()
        print(mode)
        # Define the notes configuration based on mode
        notes_configs = {
            "slides": "\\setbeameroption{hide notes}",
            "notes": "\\setbeameroption{show only notes}",
            "both": "\\setbeameroption{show notes on second screen=right}"
        }

        # First, remove any existing notes configurations
        tex_content = re.sub(r'%.*\\setbeameroption{[^}]*}.*\n', '', tex_content)
        tex_content = re.sub(r'\\setbeameroption{[^}]*}', '', tex_content)

        # Ensure pgfpages package is present
        if "\\usepackage{pgfpages}" not in tex_content:
            package_line = "\\usepackage{pgfpages}\n"
        else:
            package_line = ""

        # Get the appropriate notes configuration
        notes_config = notes_configs[mode]

        # Add the configuration just before \begin{document}
        doc_pos = tex_content.find("\\begin{document}")
        if doc_pos != -1:
            insert_text = f"{package_line}% Notes configuration\n{notes_config}\n\\setbeamertemplate{{note page}}{{\\pagecolor{{yellow!5}}\\insertnote}}\n\n"
            tex_content = tex_content[:doc_pos] + insert_text + tex_content[doc_pos:]

        return tex_content

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

            # Extract slides with notes
            slide_pattern = r"\\title\s+(.*?)\n\\begin{Content}(.*?)\\end{Content}(?:\s*\\begin{Notes}(.*?)\\end{Notes})?"
            slide_matches = re.finditer(slide_pattern, content, re.DOTALL)

            for match in slide_matches:
                title = match.group(1).strip()
                content_block = match.group(2).strip()
                notes_block = match.group(3).strip() if match.group(3) else ""

                # Extract media directive if present
                media = ""
                content_lines = []
                notes_lines = []

                first_line = content_block.split('\n')[0].strip()
                if first_line.startswith('\\'):
                    media = first_line
                    content_lines = content_block.split('\n')[1:]
                else:
                    content_lines = content_block.split('\n')

                # Process notes block if present
                if notes_block:
                    notes_lines = [line.strip() for line in notes_block.split('\n') if line.strip()]

                self.slides.append({
                    'title': title,
                    'media': media,
                    'content': [line for line in content_lines if line.strip()],
                    'notes': notes_lines
                })

            if self.slides:
                self.current_slide_index = 0
                self.load_slide(0)

            self.update_slide_list()

        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
#------------------------------------------------------------------------------
    def convert_to_tex(self) -> None:
        """Convert text to TeX with appropriate notes mode"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Clear terminal
            self.clear_terminal()
            self.write_to_terminal("Converting text to TeX...\n")

            # First let BeamerSlideGenerator create the tex file
            from BeamerSlideGenerator import process_input_file
            process_input_file(self.current_file, tex_file)

            # Now read the generated tex file
            with open(tex_file, 'r') as f:
                content = f.read()

            # Debug print
            self.write_to_terminal("\nOriginal content:\n")
            self.write_to_terminal(content[:500] + "...\n")  # Print first 500 chars

            # Get current mode and corresponding beamer option
            mode = self.notes_mode.get()
            self.write_to_terminal(f"\nCurrent mode: {mode}\n")

            notes_config = {
                "slides": "\\setbeameroption{hide notes} % Only slides",
                "notes": "\\setbeameroption{show only notes} % Only notes",
                "both": "\\setbeameroption{show notes on second screen=right} % Both"
            }[mode]

            # Remove any existing notes configuration
            content = re.sub(r'\\usepackage{pgfpages}.*\n', '', content)
            content = re.sub(r'\\setbeameroption{[^}]*}.*\n', '', content)
            content = re.sub(r'\\setbeamertemplate{note page}.*\n', '', content)

            # Check if \begin{document} exists in the content
            if '\\begin{document}' not in content:
                self.write_to_terminal("\nWarning: \\begin{document} not found in content!\n", "red")
                return

            # Insert the new configuration before \begin{document}
            modified_content = content.replace(
                '\\begin{document}',
                f'\\usepackage{{pgfpages}}\n{notes_config}\n\\setbeamertemplate{{note page}}{{\\pagecolor{{yellow!5}}\\insertnote}}\n\\begin{{document}}'
            )

            # Debug print
            self.write_to_terminal("\nModified content:\n")
            self.write_to_terminal(modified_content[:500] + "...\n")  # Print first 500 chars

            # Write the modified content back to the tex file
            with open(tex_file, 'w') as f:
                f.write(modified_content)

            self.write_to_terminal("✓ Text to TeX conversion successful\n", "green")
            messagebox.showinfo("Success", "TeX file generated successfully!")

        except Exception as e:
            self.write_to_terminal(f"✗ Error in conversion: {str(e)}\n", "red")
            self.write_to_terminal(f"Error details: {traceback.format_exc()}\n", "red")
            messagebox.showerror("Error", f"Error converting to TeX:\n{str(e)}")

#-----------------------------------------------------------------------------


def get_installation_paths():
    """Get platform-specific installation paths"""
    import platform
    import os
    from pathlib import Path
    import site
    import sys

    system = platform.system()
    paths = {}

    if os.geteuid() == 0:  # Running as root/sudo
        if system == "Linux":
            paths.update({
                'bin': Path('/usr/local/bin'),
                'share': Path('/usr/local/share'),
                'icons': Path('/usr/share/icons/hicolor'),
                'apps': Path('/usr/share/applications')
            })
        else:
            # For other systems when running as root/admin
            paths.update({
                'bin': Path(sys.prefix) / 'bin',
                'share': Path(sys.prefix) / 'share'
            })
    else:  # Running as normal user
        if system == "Linux":
            # Get user's local bin from PATH or create in ~/.local/bin
            user_bin = None
            for path in os.environ.get('PATH', '').split(os.pathsep):
                if '/.local/bin' in path and os.access(path, os.W_OK):
                    user_bin = Path(path)
                    break
            if not user_bin:
                user_bin = Path.home() / '.local' / 'bin'

            paths.update({
                'bin': user_bin,
                'share': Path.home() / '.local' / 'share',
                'icons': Path.home() / '.local' / 'share' / 'icons' / 'hicolor',
                'apps': Path.home() / '.local' / 'share' / 'applications'
            })

        elif system == "Windows":
            appdata = Path(os.getenv('APPDATA'))
            paths.update({
                'bin': appdata / 'BSG-IDE',
                'shortcut': appdata / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'BSG-IDE'
            })

        elif system == "Darwin":  # macOS
            paths.update({
                'app': Path.home() / 'Applications' / 'BSG-IDE.app',
                'contents': Path.home() / 'Applications' / 'BSG-IDE.app' / 'Contents',
                'bin': Path.home() / 'Applications' / 'BSG-IDE.app' / 'Contents' / 'MacOS',
                'resources': Path.home() / 'Applications' / 'BSG-IDE.app' / 'Contents' / 'Resources'
            })

    return system, paths

def check_installation():
    """Check if BSG-IDE is installed in the system"""
    system, paths = get_installation_paths()

    if system == "Linux":
        return (paths['bin'] / 'bsg-ide').exists()
    elif system == "Windows":
        return (paths['bin'] / 'bsg-ide.pyw').exists()
    elif system == "Darwin":
        return paths['app'].exists()
    return False
def make_executable(file_path):
    """Make file executable on Unix systems or create launcher on Windows"""
    import stat
    import platform

    system = platform.system()
    if system != "Windows":
        # Add executable permission for owner
        current = stat.S_IMODE(os.lstat(file_path).st_mode)
        os.chmod(file_path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    else:
        # For Windows, create a .bat launcher
        bat_path = file_path.parent / 'bsg-ide.bat'
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\n"{sys.executable}" "{file_path}" %*')

def check_bsg_file():
    """
    Check for BeamerSlideGenerator.py and install if missing.
    """
    # Get the correct installation path based on platform
    import platform
    system = platform.system()

    if system == "Linux":
        install_lib = Path.home() / '.local' / 'lib' / 'bsg-ide'
    elif system == "Windows":
        install_lib = Path(os.getenv('APPDATA')) / 'BSG-IDE'
    else:  # macOS
        install_lib = Path.home() / 'Library' / 'Application Support' / 'BSG-IDE'

    install_lib.mkdir(parents=True, exist_ok=True)
    bsg_file = install_lib / 'BeamerSlideGenerator.py'

    if not bsg_file.exists():
        print("\nBeamerSlideGenerator.py not found in installation directory. Installing...")
        try:
            # First check if it exists in current directory
            current_bsg = Path('BeamerSlideGenerator.py')
            if current_bsg.exists():
                # Copy the file to installation directory
                shutil.copy2(current_bsg, bsg_file)
                print(f"✓ BeamerSlideGenerator.py installed to {bsg_file}")
            else:
                # Look in script's directory
                script_dir = Path(__file__).parent.resolve()
                script_bsg = script_dir / 'BeamerSlideGenerator.py'
                if script_dir.exists():
                    shutil.copy2(script_bsg, bsg_file)
                    print(f"✓ BeamerSlideGenerator.py installed to {bsg_file}")
                else:
                    print("✗ Error: BeamerSlideGenerator.py not found in current or script directory.")
                    print("Please ensure BeamerSlideGenerator.py is in the same directory as BSG-IDE.py")
                    sys.exit(1)
        except Exception as e:
            print(f"✗ Error installing BeamerSlideGenerator.py: {str(e)}")
            print("\nPlease manually copy BeamerSlideGenerator.py to:", bsg_file)
            sys.exit(1)
    else:
        print("✓ BeamerSlideGenerator.py is installed")

    # Also ensure the file is in the current working directory for direct script mode
    if not Path('BeamerSlideGenerator.py').exists():
        try:
            shutil.copy2(bsg_file, 'BeamerSlideGenerator.py')
        except Exception as e:
            print(f"Warning: Could not copy BeamerSlideGenerator.py to current directory: {e}")

def setup_system_installation():
    """Set up system-wide installation with all required files"""
    try:
        system, paths = get_installation_paths()

        # Create installation directories
        if system == "Linux":
            # Main installation directory in user's home
            install_dir = Path.home() / '.local' / 'lib' / 'bsg-ide'
            bin_dir = Path.home() / '.local' / 'bin'
        elif system == "Windows":
            install_dir = Path(os.getenv('APPDATA')) / 'BSG-IDE'
            bin_dir = install_dir / 'bin'
        else:  # macOS
            install_dir = Path.home() / 'Library' / 'Application Support' / 'BSG-IDE'
            bin_dir = Path.home() / '.local' / 'bin'

        # Create directories
        install_dir.mkdir(parents=True, exist_ok=True)
        bin_dir.mkdir(parents=True, exist_ok=True)

        # Get current script directory
        script_dir = Path(__file__).parent.resolve()

        # Copy required Python files
        required_files = {
            'BSG-IDE.py': 'BSG_IDE.py',  # Rename to valid module name
            'BeamerSlideGenerator.py': 'BeamerSlideGenerator.py',
            'Beam2odp.py': 'Beam2odp.py'  # if you have this file
        }

        # Copy all required files to installation directory
        for src_name, dest_name in required_files.items():
            src_file = script_dir / src_name
            if src_file.exists():
                shutil.copy2(src_file, install_dir / dest_name)
                print(f"✓ Copied {src_name} to {install_dir / dest_name}")

        # Create __init__.py in installation directory
        (install_dir / '__init__.py').touch()

        # Create launcher script based on platform
        if system == "Linux":
            launcher_script = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add installation directory to Python path
install_dir = Path('{install_dir}')
sys.path.insert(0, str(install_dir))

# Import and run main program
from BSG_IDE import main

if __name__ == '__main__':
    main()
"""
            # Create launcher in bin directory
            launcher_path = bin_dir / 'bsg-ide'
            launcher_path.write_text(launcher_script)
            make_executable(launcher_path)
            print(f"✓ Created launcher at {launcher_path}")

            # Create desktop entry
            apps_dir = Path.home() / '.local' / 'share' / 'applications'
            apps_dir.mkdir(parents=True, exist_ok=True)

            desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec={launcher_path}
Icon=bsg-ide
Terminal=false
Categories=Office;Documentation;
Keywords=presentation;slides;beamer;latex;
"""
            desktop_file = apps_dir / 'bsg-ide.desktop'
            desktop_file.write_text(desktop_entry)
            make_executable(desktop_file)

        elif system == "Windows":
            launcher_script = f"""@echo off
set PYTHONPATH={install_dir};%PYTHONPATH%
python -c "from BSG_IDE import main; main()" %*
"""
            # Create batch file in bin directory
            launcher_path = bin_dir / 'bsg-ide.bat'
            launcher_path.write_text(launcher_script)
            print(f"✓ Created launcher at {launcher_path}")

            # Create Start Menu shortcut
            try:
                import winshell
                from win32com.client import Dispatch
                programs_path = Path(winshell.folder("CSIDL_PROGRAMS")) / "BSG-IDE"
                programs_path.mkdir(parents=True, exist_ok=True)

                shortcut_path = programs_path / "BSG-IDE.lnk"
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(launcher_path)
                shortcut.save()
            except ImportError:
                print("Warning: Could not create Windows shortcut")

        else:  # macOS
            launcher_script = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add installation directory to Python path
install_dir = Path('{install_dir}')
sys.path.insert(0, str(install_dir))

# Ensure BeamerSlideGenerator.py is available
bsg_file = install_dir / 'BeamerSlideGenerator.py'
if not bsg_file.exists():
    print("Error: BeamerSlideGenerator.py not found")
    sys.exit(1)

# Import and run main program
from BSG_IDE import main

if __name__ == '__main__':
    main()
"""
            # Create launcher in bin directory
            launcher_path = bin_dir / 'bsg-ide'
            launcher_path.write_text(launcher_script)
            make_executable(launcher_path)
            print(f"✓ Created launcher at {launcher_path}")

        # Add installation directory to PYTHONPATH in shell rc file
        if system != "Windows":
            shell_rc = Path.home() / ('.zshrc' if os.path.exists(Path.home() / '.zshrc') else '.bashrc')
            pythonpath_line = f'\nexport PYTHONPATH="{install_dir}:$PYTHONPATH"\n'
            path_line = f'\nexport PATH="{bin_dir}:$PATH"\n'

            if shell_rc.exists():
                content = shell_rc.read_text()
                if pythonpath_line not in content:
                    shell_rc.write_text(content + pythonpath_line + path_line)
            else:
                shell_rc.write_text(pythonpath_line + path_line)

        print(f"""
Installation completed successfully:
- Files installed to: {install_dir}
- Launcher created at: {launcher_path}
- Python path updated to include installation directory
""")

        return True

    except Exception as e:
        print(f"Installation error: {str(e)}")
        traceback.print_exc()
        return False
def main():
    # First check dependencies
    check_and_install_dependencies()

    # Get system information
    system, paths = get_installation_paths()

    # Check if running as script or installed version
    current_script = Path(__file__).resolve()

    if system == "Linux":
        installed_path = paths['bin'] / 'bsg-ide'
    elif system == "Windows":
        installed_path = paths['bin'] / 'bsg-ide.pyw'
    elif system == "Darwin":
        installed_path = paths['bin'] / 'bsg-ide'
    else:
        installed_path = None

    # If script version and not installed, set up installation
    if installed_path and current_script != installed_path and not check_installation():
        print("First-time run detected. Setting up BSG-IDE...")
        try:
            if setup_system_installation():
                print("Installation successful! Launching installed version...")

                # Launch installed version with proper permissions
                if system == "Windows":
                    os.startfile(str(installed_path))
                else:
                    os.execv(sys.executable, [sys.executable, str(installed_path)] + sys.argv[1:])
                sys.exit(0)
            else:
                print("Installation incomplete. Running from current location.")
        except Exception as e:
            print(f"Installation failed: {str(e)}")
            print("Running from current location.")

    # Launch the IDE
    try:
        app = BeamerSlideEditor()
        app.mainloop()
    except Exception as e:
        print(f"Error launching IDE: {str(e)}")
        if system != "Windows":  # Show terminal output on Unix systems
            input("Press Enter to exit...")
#----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
