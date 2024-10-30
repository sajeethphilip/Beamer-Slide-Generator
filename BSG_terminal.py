# terminal_emulator.py

import os
import sys
import queue
import shlex
import signal
import threading
import subprocess
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

class InteractiveTerminal(ctk.CTkFrame):
    """Interactive terminal with proper CTkTextbox handling"""
    def __init__(self, master, initial_directory=None, **kwargs):
        super().__init__(master, **kwargs)

        # Initialize variables
        self.working_dir = initial_directory or os.getcwd()
        self.command_queue = queue.Queue()

        # Create UI
        self._create_ui()

        # Start command processor
        self.running = True
        self.process_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.process_thread.start()

    def _create_ui(self):
        """Create terminal UI"""
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=2, pady=2)

        # Directory label
        self.dir_label = ctk.CTkLabel(header, text=f"📁 {self.working_dir}")
        self.dir_label.pack(side="left", padx=5)

        # Control buttons
        ctk.CTkButton(header, text="Clear",
                     command=self.clear).pack(side="right", padx=5)

        # Terminal display
        self.display = ctk.CTkTextbox(
            self,
            wrap="none",
            font=("Courier", 10)
        )
        self.display.pack(fill="both", expand=True, padx=2, pady=2)

        # Set up text tags for colors
        self.display._textbox.tag_configure("red", foreground="red")
        self.display._textbox.tag_configure("green", foreground="green")
        self.display._textbox.tag_configure("yellow", foreground="yellow")
        self.display._textbox.tag_configure("white", foreground="white")

        # Input handling
        self.display.bind("<Return>", self._handle_input)

        # Initial prompt
        self.show_prompt()

    def write(self, text, color="white"):
        """Write text to terminal"""
        try:
            # Insert text directly with color tag
            self.display._textbox.insert("end", text, color)
            self.display.see("end")
            self.update_idletasks()
        except Exception as e:
            print(f"Write error: {e}", file=sys.__stdout__)

    def clear(self):
        """Clear terminal content"""
        # Clear text directly
        self.display._textbox.delete("1.0", "end")
        self.show_prompt()

    def _handle_input(self, event):
        """Handle user input"""
        try:
            # Get current line
            current_line = self.display._textbox.get("insert linestart", "insert lineend")
            if current_line.startswith("$ "):
                command = current_line[2:]
                if command.strip():
                    self.command_queue.put(command)

            # Add newline
            self.write("\n")

            return "break"
        except Exception as e:
            self.write(f"\nInput error: {str(e)}\n", "red")

    def _process_commands(self):
        """Process commands in background"""
        while self.running:
            try:
                # Get command with timeout
                command = self.command_queue.get(timeout=0.1)

                # Handle cd command
                if command.startswith("cd "):
                    path = command[3:].strip()
                    self._change_directory(path)
                    continue

                # Execute command
                try:
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=self.working_dir,
                        text=True
                    )

                    # Read output
                    out, err = process.communicate()

                    # Write output in main thread
                    if out:
                        self.after(0, lambda: self.write(out))
                    if err:
                        self.after(0, lambda: self.write(err, "red"))

                except Exception as e:
                    self.after(0, lambda: self.write(f"\nError: {str(e)}\n", "red"))

                # Show new prompt
                self.after(0, self.show_prompt)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command processing error: {e}", file=sys.__stdout__)

    def show_prompt(self):
        """Show command prompt"""
        self.write("\n$ ")

    def set_working_directory(self, directory):
        """Set working directory"""
        if os.path.exists(directory):
            self.working_dir = directory
            os.chdir(directory)
            self.dir_label.configure(text=f"📁 {self.working_dir}")

class SimpleRedirector:
    """Output redirector"""
    def __init__(self, terminal, color="white"):
        self.terminal = terminal
        self.color = color

    def write(self, text):
        if text.strip():
            self.terminal.write(text, self.color)

    def flush(self):
        pass
