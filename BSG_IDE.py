#!/usr/bin/env python3
"""
BSG_Integrated_Development_Environment.py
An integrated development environment for BeamerSlideGenerator
Combines GUI editing, syntax highlighting, and presentation generation.

"""
#------------------------------Check and install ----------------------------------------------
import os,re
import sys
import tempfile
import subprocess
#------------------------------------------------------------------------------------------------------
import venv
import platform
from pathlib import Path
import site
import socket
from importlib import util
global working_folder

def launch_ide():
    """Entry point for command-line launcher"""
    try:
        # Ensure working directory is script directory
        import os
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Import required modules
        import sys
        from pathlib import Path

        # Add current directory to Python path
        current_dir = Path(__file__).parent.resolve()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))



        # Create and run the IDE
        app = BeamerSlideEditor()
        app.mainloop()

    except Exception as e:
        print(f"Error launching BSG-IDE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def check_internet_connection():
    """Check internet connection without external dependencies"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def setup_virtual_env():
    """Setup and activate virtual environment with improved error handling"""
    try:
        home_dir = Path.home()
        venv_path = home_dir / 'my_python'

        # Create venv if it doesn't exist
        if not venv_path.exists():
            print(f"Creating virtual environment at {venv_path}")
            venv.create(venv_path, with_pip=True, clear=True)

        # Get paths based on platform
        if platform.system() == "Windows":
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"

        # Verify the virtual environment is working
        if not venv_python.exists() or not venv_pip.exists():
            print("Virtual environment files not found, recreating...")
            shutil.rmtree(venv_path, ignore_errors=True)
            venv.create(venv_path, with_pip=True, clear=True)

        # Test virtual environment
        try:
            subprocess.run(
                [str(venv_python), "-c", "import sys; print(sys.prefix)"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError:
            print("Virtual environment test failed, falling back to system Python")
            return sys.executable, "pip", False

        return str(venv_python), str(venv_pip), True

    except Exception as e:
        print(f"Error setting up virtual environment: {str(e)}")
        return sys.executable, "pip", False

def install_base_packages(pip_path):
    """Install essential packages without GUI dependencies"""
    base_packages = [
        "customtkinter",
        "Pillow",
        "tk",  # Basic tkinter
        "latexcodec",    # For LaTeX code handling
        "latex",         # Python LaTeX tools

    ]

    for package in base_packages:
        try:
            subprocess.run(
                [pip_path, "install", "--no-cache-dir", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError:
            continue


def get_requirements_path():
    """Get path to requirements.txt with exhaustive search"""
    possible_paths = [
        # Current directory
        Path.cwd() / 'requirements.txt',
        # Script directory
        Path(__file__).parent / 'requirements.txt',
        # User local installation
        Path.home() / '.local' / 'lib' / 'bsg-ide' / 'requirements.txt',
        # Windows AppData
        Path(os.getenv('APPDATA', '')) / 'BSG-IDE' / 'requirements.txt',
        # System-wide installation
        Path('/usr/local/share/bsg-ide/requirements.txt'),
        # Virtual environment
        Path(os.getenv('VIRTUAL_ENV', '')) / 'requirements.txt',
    ]

    # Add additional search paths for macOS
    if sys.platform == 'darwin':
        possible_paths.extend([
            Path.home() / 'Library' / 'Application Support' / 'BSG-IDE' / 'requirements.txt',
            Path('/Applications/BSG-IDE.app/Contents/Resources/requirements.txt')
        ])

    print("\nSearching for requirements.txt in:")
    for path in possible_paths:
        print(f"Checking {path}...")
        if path.exists():
            print(f"✓ Found requirements.txt at: {path}")
            return path

    print("Could not find requirements.txt in standard locations")
    return generate_default_requirements()

def generate_default_requirements():
    """Generate a default requirements.txt if none found"""
    try:
        default_requirements = """customtkinter==5.2.2
Pillow
tk
requests
yt_dlp
opencv-python
screeninfo
numpy
PyMuPDF==1.23.7
pyautogui
"""
        # Try to write to user's local directory first
        save_paths = [
            Path.home() / '.local' / 'lib' / 'bsg-ide',
            Path.cwd(),
            Path(os.getenv('APPDATA', '')) / 'BSG-IDE'
        ]

        for path in save_paths:
            try:
                os.makedirs(path, exist_ok=True)
                req_file = path / 'requirements.txt'
                req_file.write_text(default_requirements)
                print(f"\nCreated default requirements.txt at: {req_file}")
                return req_file
            except:
                continue

        # If all save attempts fail, create in current directory
        print("\nWarning: Could not save to preferred locations")
        with open('requirements.txt', 'w') as f:
            f.write(default_requirements)
        return Path('requirements.txt')

    except Exception as e:
        print(f"Error generating requirements.txt: {str(e)}")
        return None

def install_system_dependencies():
    """Install system dependencies based on detected OS and package manager"""
    try:
        # Detect operating system
        if sys.platform.startswith('linux'):
            # Detect Linux distribution and package manager
            if shutil.which('apt'):  # Debian/Ubuntu
                mgr = 'apt'
                cmd = ['sudo', 'apt', 'install', '-y']
                deps = [
                    'python3-gi',
                    'python3-gi-cairo',
                    'gir1.2-gtk-3.0',
                    'python3-cairo',
                    'libgtk-3-0',
                    'librsvg2-common',
                    'poppler-utils',
                    'libgirepository1.0-dev',
                    'gcc',
                    'python3-dev',
                    'pkg-config',
                    'libcairo2-dev',
                    'pyautogui',
                    'gobject-introspection'
                ]
            elif shutil.which('dnf'):  # Fedora/RHEL
                mgr = 'dnf'
                cmd = ['sudo', 'dnf', 'install', '-y']
                deps = [
                    'python3-gobject',
                    'python3-cairo',
                    'gtk3',
                    'python3-devel',
                    'gcc',
                    'pkg-config',
                    'cairo-devel',
                    'pyautogui',
                    'gobject-introspection-devel',
                    'cairo-gobject-devel'
                ]
            elif shutil.which('pacman'):  # Arch Linux
                mgr = 'pacman'
                cmd = ['sudo', 'pacman', '-S', '--noconfirm']
                deps = [
                    'python-gobject',
                    'python-cairo',
                    'gtk3',
                    'python-pip',
                    'gcc',
                    'pkg-config',
                    'cairo',
                    'pyautogui',
                    'gobject-introspection'
                ]
            elif shutil.which('zypper'):  # openSUSE
                mgr = 'zypper'
                cmd = ['sudo', 'zypper', 'install', '-y']
                deps = [
                    'python3-gobject',
                    'python3-cairo',
                    'gtk3',
                    'python3-devel',
                    'gcc',
                    'pkg-config',
                    'cairo-devel',
                    'pyautogui',
                    'gobject-introspection-devel'
                ]
            else:
                print("Could not detect package manager. Please install dependencies manually:")
                print("Required: GTK3, Python-GObject, Cairo, and development tools")
                return False

            print(f"\nInstalling system dependencies using {mgr}...")
            try:
                subprocess.check_call(cmd + deps)
                print("✓ System dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing system dependencies: {e}")
                return False

        elif sys.platform.startswith('darwin'):  # macOS
            try:
                # Check if Homebrew is installed
                if not shutil.which('brew'):
                    print("Homebrew not found. Installing...")
                    brew_install = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                    subprocess.check_call(brew_install, shell=True)

                # Install dependencies using Homebrew
                deps = [
                    'gtk+3',
                    'pygobject3',
                    'cairo',
                    'py3cairo',
                    'pyautogui',
                    'gobject-introspection'
                ]

                for dep in deps:
                    subprocess.check_call(['brew', 'install', dep])
                print("✓ System dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing macOS dependencies: {e}")
                return False

        elif sys.platform.startswith('win'):  # Windows
            try:
                # For Windows, we'll use MSYS2 to install GTK and dependencies
                if not os.path.exists(r'C:\msys64'):
                    print("MSYS2 not found. Please install MSYS2 from: https://www.msys2.org/")
                    print("After installing, run: pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python-gobject")
                    return False

                # Update MSYS2 and install dependencies
                msys2_path = r'C:\msys64\usr\bin\bash.exe'
                deps = [
                    'mingw-w64-x86_64-gtk3',
                    'mingw-w64-x86_64-python-gobject',
                    'mingw-w64-x86_64-python-cairo',
                    'mingw-w64-x86_64-gcc'
                ]

                for dep in deps:
                    subprocess.check_call([msys2_path, '-lc', f'pacman -S --noconfirm {dep}'])
                print("✓ System dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing Windows dependencies: {e}")
                return False

        return True

    except Exception as e:
        print(f"Error installing system dependencies: {str(e)}")
        return False
#------------------------------------------------------------
def install_bsg_ide(fix_mode=False):
    """Main installation function"""
    try:
        # Create a temporary root window if no parent is available
        temp_root = None
        try:
            # Try to get existing Tk root
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
        except:
            pass

        installer = InstallationManager(temp_root)
        install_type = "system-wide" if installer.is_admin else "user"

        print(f"\nStarting BSG-IDE {'fix' if fix_mode else 'installation'} ({install_type})")
        print(f"Detected OS: {installer.system}")

        # Create directory structure
        installer.create_directory_structure()

        # Copy resources
        package_root = Path(__file__).resolve().parent
        installer.copy_resources(package_root)

        # Create launcher
        installer.create_launcher()

        # Setup OS integration
        #installer.setup_os_integration()


        print(f"\nBSG-IDE {'fix' if fix_mode else 'installation'} completed successfully!")
        print("\nYou can now run BSG-IDE by:")
        if installer.system == "Windows":
            print("1. Using the Start Menu shortcut")
            print("2. Running 'bsg-ide' from Command Prompt")
        elif installer.system == "Darwin":
            print("1. Opening BSG-IDE from Applications")
            print("2. Running 'bsg-ide' from Terminal")
        else:
            print("1. Using the application menu")
            print("2. Running 'bsg-ide' from terminal")

        return True

    except Exception as e:
        print(f"\n✗ Error during {'fix' if fix_mode else 'installation'}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary root window if we created one
        if temp_root is not None:
            try:
                temp_root.destroy()
            except:
                pass

def verify_installation():
    import site
    import sys
    from pathlib import Path

    """Verify BSG-IDE whether running from source or installed"""
    try:
        package_root, resources_dir = setup_paths()
        all_ok = True

        print("\nChecking installation...")
        print(f"Package root: {package_root}")
        print(f"Resources directory: {resources_dir}")

        # 1. Check core files
        required_files = {
            'BSG_IDE.py': package_root,
            'BeamerSlideGenerator.py': package_root,
            'requirements.txt': package_root,
            'airis4d_logo.png': resources_dir,
            'bsg-ide.png': resources_dir
        }

        print("\nChecking required files:")
        for filename, directory in required_files.items():
            path = directory / filename
            if path.exists():
                print(f"✓ Found {filename} in {directory}")
            else:
                print(f"✗ Missing {filename}")
                all_ok = False

        # 2. Check Python paths
        print("\nChecking Python paths:")
        if str(package_root) in sys.path:
            print("✓ Package root in Python path")
        else:
            print("✗ Package root not in Python path")
            all_ok = False

        try:

            # Get all possible site-packages locations
            site_packages_paths = {
                'user': Path(site.getusersitepackages()),
                'venv': Path(sys.prefix) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages',
                'system': Path(site.getsitepackages()[0]) if site.getsitepackages() else None
            }

            found = False
            for location, path in site_packages_paths.items():
                if path and str(path) in sys.path:
                    print(f"✓ Found {location} site-packages in Python path: {path}")
                    found = True

            if not found:
                print("✗ No site-packages directories found in Python path")
                all_ok = False

            # Also check if BSG-IDE is importable
            try:
                import BeamerSlideGenerator
                print("✓ BSG-IDE package is importable")
            except ImportError as e:
                print(f"✗ Cannot import BSG-IDE package: {e}")
                all_ok = False

        except Exception as e:
            print(f"! Warning: Could not check site-packages: {e}")

        # 3. Check launcher script
        print("\nChecking launcher script:")
        if sys.platform == "win32":
            launcher_name = 'bsg-ide.bat'
        else:
            launcher_name = 'bsg-ide'

        launcher_locations = [
            Path.home() / '.local/bin',
            Path('/usr/local/bin'),
            package_root / 'bin'
        ]

        launcher_found = False
        for loc in launcher_locations:
            launcher_path = loc / launcher_name
            if launcher_path.exists():
                print(f"✓ Found launcher at: {launcher_path}")
                launcher_found = True
                # Check permissions on Unix-like systems
                if sys.platform != "win32":
                    if os.access(launcher_path, os.X_OK):
                        print("✓ Launcher has correct permissions")
                    else:
                        print("✗ Launcher missing executable permission")
                        all_ok = False
                break

        if not launcher_found:
            print("✗ Launcher script not found")
            all_ok = False

        # 4. Check desktop integration
        print("\nChecking desktop integration:")
        if sys.platform.startswith('linux'):
            # Check desktop entry
            desktop_locations = [
                Path.home() / '.local/share/applications',
                Path('/usr/share/applications')
            ]
            desktop_found = False
            for loc in desktop_locations:
                desktop_path = loc / 'bsg-ide.desktop'
                if desktop_path.exists():
                    print(f"✓ Found desktop entry at: {desktop_path}")
                    desktop_found = True
                    break

            if not desktop_found:
                print("✗ Desktop entry not found")
                all_ok = False

            # Check icons
            icon_found = False
            icon_sizes = ['16x16', '32x32', '48x48', '64x64', '128x128', '256x256']
            for size in icon_sizes:
                icon_locations = [
                    Path.home() / f'.local/share/icons/hicolor/{size}/apps',
                    Path(f'/usr/share/icons/hicolor/{size}/apps')
                ]
                for loc in icon_locations:
                    icon_path = loc / 'bsg-ide.png'
                    if icon_path.exists():
                        if not icon_found:  # Only print first found
                            print(f"✓ Found application icon at: {icon_path.parent.parent.parent}")
                        icon_found = True

            if not icon_found:
                print("✗ Application icon not found")
                all_ok = False

        elif sys.platform == "darwin":  # macOS
            app_locations = [
                Path.home() / 'Applications/BSG-IDE.app',
                Path('/Applications/BSG-IDE.app')
            ]
            app_found = False
            for loc in app_locations:
                if loc.exists():
                    print(f"✓ Found application bundle at: {loc}")
                    app_found = True
                    # Check Info.plist
                    if (loc / 'Contents/Info.plist').exists():
                        print("✓ Found Info.plist")
                    else:
                        print("✗ Missing Info.plist")
                        all_ok = False
                    break

            if not app_found:
                print("✗ Application bundle not found")
                all_ok = False

        elif sys.platform == "win32":  # Windows
            # Check Start Menu shortcut
            start_menu_locations = [
                Path(os.environ['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs',
                Path(os.environ['PROGRAMDATA']) / 'Microsoft/Windows/Start Menu/Programs'
            ]
            shortcut_found = False
            for loc in start_menu_locations:
                shortcut_path = loc / 'BSG-IDE/BSG-IDE.lnk'
                if shortcut_path.exists():
                    print(f"✓ Found Start Menu shortcut at: {shortcut_path}")
                    shortcut_found = True
                    break

            if not shortcut_found:
                print("✗ Start Menu shortcut not found")
                all_ok = False

        # 5. Check imports
        print("\nChecking imports:")
        try:
            import BeamerSlideGenerator
            print("✓ Can import BeamerSlideGenerator")
        except ImportError as e:
            print(f"✗ Cannot import BeamerSlideGenerator: {e}")
            all_ok = False



        # Final status
        print("\nVerification result:")
        if all_ok:
            print("✓ All checks passed successfully!")
        else:
            print("✗ Some checks failed. Please run 'bsg-ide --fix' to repair the installation")

        return all_ok

    except Exception as e:
        print(f"\n✗ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False




def get_package_root():
    """Get the package root directory whether installed or running from source"""
    try:
        # First check if we're running from source
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent

        # Check if we're in source directory (look for key files)
        if all((current_dir / f).exists() for f in ['BeamerSlideGenerator.py', 'BSG_IDE.py']):
            return current_dir

        # If not in source, check if we're pip installed
        try:
            import bsg_ide
            return Path(bsg_ide.__file__).parent
        except ImportError:
            pass

        # Finally check standard installation locations
        standard_locations = [
            Path.home() / '.local/lib/bsg-ide',
            Path.home() / '.local/share/bsg-ide',
            Path('/usr/local/share/bsg-ide')
        ]

        for loc in standard_locations:
            if (loc / 'BSG_IDE.py').exists():
                return loc

        # If we get here, return current directory as fallback
        return current_dir

    except Exception as e:
        print(f"Warning: Could not determine package root: {e}")
        return Path(__file__).parent

def setup_paths():
    """Setup Python paths for both source and installed runs"""
    package_root = get_package_root()

    # Add package root to Python path if not already there
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    # Find resources directory
    resources_dir = package_root / 'resources'
    if not resources_dir.exists():
        resources_dir = package_root  # Fallback to package root

    return package_root, resources_dir
#-----------------------------------------------------------


def create_desktop_entry():
    """Create desktop entry for pympress launcher"""
    if sys.platform.startswith('linux'):
        desktop_entry = """[Desktop Entry]
Type=Application
Name=pympress
Comment=PDF Presentation Tool
Exec=pympress %f
Icon=pympress
Terminal=false
Categories=Office;Presentation;
MimeType=application/pdf;
"""
        desktop_path = Path.home() / '.local' / 'share' / 'applications' / 'pympress.desktop'
        os.makedirs(desktop_path.parent, exist_ok=True)
        desktop_path.write_text(desktop_entry)
        desktop_path.chmod(0o755)
        print("✓ Desktop entry created")



def verify_existing_packages():
    """Verify existing packages when offline"""
    try:
        import customtkinter
        import PIL
        import tkinter
        print("✓ Required packages found in existing installation")
        return True
    except ImportError:
        print("Error: Required packages not found and cannot install offline")
        return False
#-----------------------------------------Check dependencies -------------------

def check_and_install_dependencies():
    """
    Two-phase dependency installation with improved virtual environment handling
    """
    # Suppress standard output during initial installation
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    try:
        # Check internet connection
        if not check_internet_connection():
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            print("No internet connection. Continuing with available packages.")
            return True

        # Get requirements.txt path
        requirements_path = get_requirements_path()
        if not requirements_path:
            print("Error: Could not locate or create requirements.txt")
            return False

        # Setup virtual environment
        python_path, pip_path, venv_created = setup_virtual_env()

        # Phase 1: Install base packages (no GUI feedback)
        base_packages = {
            "customtkinter": "5.2.2",
            "Pillow": None,
            "tk": None
        }

        # First, upgrade pip in the virtual environment
        try:
            subprocess.run(
                [pip_path, "install", "--upgrade", "pip"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except Exception as e:
            print(f"Error upgrading pip: {e}")

        # Install base packages in virtual environment
        for package, version in base_packages.items():
            try:
                package_spec = f"{package}=={version}" if version else package
                # Do not use --user flag in virtual environment
                subprocess.run(
                    [pip_path, "install", "--no-cache-dir", package_spec],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                print(f"✓ Installed {package_spec}")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                # Try alternative installation without version constraint
                try:
                    subprocess.run(
                        [pip_path, "install", "--no-cache-dir", package.split('==')[0]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                    print(f"✓ Installed {package} (latest version)")
                except subprocess.CalledProcessError as e2:
                    print(f"Alternative installation failed for {package}: {e2}")
                    continue

        # Create media_files directory
        os.makedirs('media_files', exist_ok=True)

        # Restore output for verification
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        # Verify customtkinter installation
        try:
            # Add virtual environment site-packages to Python path
            if venv_created:
                import site
                venv_site_packages = os.path.join(os.path.dirname(pip_path), '..', 'lib',
                                                f'python{sys.version_info.major}.{sys.version_info.minor}',
                                                'site-packages')
                sys.path.insert(0, venv_site_packages)

            import customtkinter
            print("✓ customtkinter installed successfully")

            # Phase 2: Install remaining packages with GUI feedback
            try:
                import tkinter as tk
                from tkinter import ttk
                install_remaining_packages(pip_path)
            except ImportError as e:
                print(f"Error importing GUI packages for phase 2: {e}")
                # Fall back to silent installation of remaining packages
                packages = {
                    'requests': 'requests',
                    'yt_dlp': 'yt-dlp',
                    'cv2': 'opencv-python',
                    'screeninfo': 'screeninfo',
                    'numpy': 'numpy',
                    'pyautogui':'pyautogui',
                    'fitz': 'PyMuPDF==1.23.7'

                }

                for import_name, install_name in packages.items():
                    try:
                        if not util.find_spec(import_name):
                            subprocess.run(
                                [pip_path, "install", "--no-cache-dir", install_name],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True
                            )
                            print(f"✓ Installed {install_name}")
                    except:
                        continue

            return verify_installation()

        except ImportError:
            print("! Warning: customtkinter not found after installation")
            # Print the current sys.path for debugging
            print("\nCurrent Python path:")
            for p in sys.path:
                print(f"  {p}")
            return False

        return True

    except Exception as e:
        # Restore output
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        print(f"Warning: Some dependencies may be missing. Continuing with available packages.")
        print(f"Error details: {str(e)}")
        return True

    finally:
        # Ensure output is restored
        sys.stdout = original_stdout
        sys.stderr = original_stderr

def install_remaining_packages(pip_path):
    """Install all remaining packages from requirements.txt with progress feedback"""
    try:
        # Now we can safely import GUI packages
        import tkinter as tk
        from tkinter import ttk
        import customtkinter as ctk

        class ProgressDialog:
            def __init__(self):
                self.root = ctk.CTk()
                self.root.title("Installing Dependencies")
                self.root.geometry("300x150")

                # Center window
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width - 300) // 2
                y = (screen_height - 150) // 2
                self.root.geometry(f"+{x}+{y}")

                self.label = ctk.CTkLabel(
                    self.root,
                    text="Installing dependencies...",
                    font=("Arial", 12)
                )
                self.label.pack(pady=20)

                self.progress = ctk.CTkProgressBar(self.root)
                self.progress.pack(pady=10, padx=20, fill="x")
                self.progress.set(0)

                self.status = ctk.CTkLabel(
                    self.root,
                    text="",
                    font=("Arial", 10)
                )
                self.status.pack(pady=5)

                self.root.update()

            def update(self, progress, text=None):
                self.progress.set(progress)
                if text:
                    self.label.configure(text=text)
                    # Also update status with package name
                    if "Installing" in text:
                        package = text.split("Installing ")[-1].strip('...')
                        self.status.configure(text=f"Package: {package}")
                self.root.update()

            def close(self):
                self.root.destroy()

        try:
            # Get requirements.txt path
            requirements_path = get_requirements_path()

            # Read requirements.txt
            with open(requirements_path, 'r') as f:
                requirements = [line.strip() for line in f
                              if line.strip() and not line.startswith('#')]

            # Create progress dialog
            dialog = ProgressDialog()

            # Install packages with progress updates
            total = len(requirements)
            successful = 0
            failed = []

            for i, requirement in enumerate(requirements, 1):
                progress = i / total
                package_name = requirement.split('>=')[0].split('==')[0].strip()
                dialog.update(progress, f"Installing {package_name}...")

                try:
                    # First try to import to check if already installed
                    try:
                        if ';' in requirement:  # Skip platform-specific requirements check
                            raise ImportError
                        module_name = package_name.replace('-', '_')
                        __import__(module_name)
                        successful += 1
                        dialog.status.configure(text=f"✓ {package_name} already installed")
                        dialog.root.update()
                        continue
                    except ImportError:
                        pass

                    # If not installed, install it
                    result = subprocess.run(
                        [pip_path, "install", "--no-cache-dir", requirement],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=True
                    )
                    successful += 1
                    dialog.status.configure(text=f"✓ {package_name} installed successfully")
                except Exception as e:
                    print(f"Warning: Failed to install {requirement}: {str(e)}")
                    failed.append(package_name)
                    dialog.status.configure(text=f"✗ Failed to install {package_name}")

                dialog.root.update()

            # Show completion status
            dialog.update(1.0, "Installation complete!")
            final_status = f"Installed {successful} of {total} packages"
            if failed:
                final_status += f"\nFailed: {', '.join(failed)}"
            dialog.status.configure(text=final_status)
            dialog.root.after(2000, dialog.close)  # Close after 2 seconds
            dialog.root.mainloop()

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            print(f"Error in GUI installation: {str(e)}")
            # Fall back to silent installation
            subprocess.run(
                [pip_path, "install", "-r", str(requirements_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

    except ImportError as e:
        print(f"GUI packages not available for progress dialog: {str(e)}")
        print("Falling back to silent installation...")
        # Fall back to silent installation
        subprocess.run(
            [pip_path, "install", "-r", str(requirements_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"Error installing packages: {str(e)}")




#------------------------------------------------------------------------------------------

check_and_install_dependencies()


import atexit
import shutil
import threading
import queue
import socket
import json
import time
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter as ctk
from typing import Optional, Dict, List, Tuple,Any
from pathlib import Path
from PIL import Image
import traceback
import webbrowser
#from BSE import BeamerSlideEditor,BeamerSyntaxHighlighter

#-------------------------------------BSE-----------------------------------------------

import customtkinter as ctk
import tkinter as tk
import os,sys
import threading
from pathlib import Path
from PIL import Image
#from BSE_ITR import InteractiveTerminal
#------------------------------------------------------------------------------------------
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
        # Initialize presentation metadata
        self.presentation_info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': 'Artificial Intelligence Research and Intelligent Systems (airis4D)',
            'short_institute': 'airis4D',
            'date': '\\today'
        }


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
        # Initialize logo before creating widgets
        self.setup_logo()

        # Initialize paths
        self.package_root, self.resources_dir = setup_paths()

        # Initialize logo before creating widgets
        self.has_logo = False
        self.logo_image = None

        # Try to find logo
        possible_paths = [
            self.resources_dir / 'airis4d_logo.png',
            self.package_root / 'airis4d_logo.png',
            self.package_root / 'resources' / 'airis4d_logo.png'
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    self.logo_image = ctk.CTkImage(
                        light_image=Image.open(path),
                        dark_image=Image.open(path),
                        size=(50, 50)
                    )
                    self.has_logo = True
                    print(f"✓ Loaded logo from {path}")
                    break
                except Exception as e:
                    print(f"Warning: Could not load logo from {path}: {e}")
                    continue

        # Rest of initialization...
        self.create_widgets()
        # Create terminal I/O interface
        self.terminal_io = TerminalIO(self)
        #-----------------------------------------------
        # Initialize session manager with error handling
        try:
            self.session_manager = SessionManager()
            self.session_data = self.session_manager.load_session()
        except Exception as e:
            print(f"Warning: Session management unavailable: {str(e)}")
            self.session_manager = None

            documents_dir = None
            try:
                possible_docs = [
                    Path.home() / 'Documents',
                    Path.home() / 'documents',
                    Path(os.path.expandvars('%USERPROFILE%\\Documents'))
                ]
                for doc_path in possible_docs:
                    if doc_path.exists() and doc_path.is_dir():
                        documents_dir = doc_path
                        break
            except:
                pass


            self.session_data = {
                'last_file': None,
                'working_directory': str(Path.cwd()),
                'recent_files': [],
                'window_size': {'width': 1200, 'height': 800},
                'window_position': {'x': None, 'y': None}
            }

        # Configure window based on session data
        self.title("BeamerSlide Generator IDE")
        self.geometry(f"{self.session_data['window_size']['width']}x{self.session_data['window_size']['height']}")
        if all(v is not None for v in self.session_data['window_position'].values()):
            self.geometry(f"+{self.session_data['window_position']['x']}+{self.session_data['window_position']['y']}")

        # Change to working directory if valid
        try:
            working_dir = Path(self.session_data['working_directory'])
            if working_dir.exists():
                os.chdir(working_dir)
                print(f"Working directory set to: {working_dir}")
            else:
                # Try to use Documents folder
                documents_dir = None
                possible_docs = [
                    Path.home() / 'Documents',
                    Path.home() / 'documents',
                    Path(os.path.expandvars('%USERPROFILE%\\Documents'))
                ]
                for doc_path in possible_docs:
                    if doc_path.exists() and doc_path.is_dir():
                        documents_dir = doc_path
                        os.chdir(documents_dir)
                        print(f"Working directory set to Documents: {documents_dir}")
                        break
                else:
                    # Fall back to home directory
                    os.chdir(Path.home())
                    print(f"Working directory set to home: {Path.home()}")
        except Exception as e:
            print(f"Warning: Could not set working directory: {str(e)}")
            print("Falling back to current directory")


        # Initialize UI components
        self.create_widgets()

        # Add recent files menu if available
        if self.session_data['recent_files']:
            self.create_recent_files_menu()

        #--------------------------------------------------
        # Set the terminal I/O in BeamerSlideGenerator
        from BeamerSlideGenerator import set_terminal_io
        set_terminal_io(self.terminal_io)

        # Configure window
        self.title("BeamerSlide Generator IDE")
        self.geometry("1200x800")

        try:
            # Try to load the logo image
            self.logo_image = ctk.CTkImage(
                light_image=Image.open("airis4d_logo.png"),
                dark_image=Image.open("airis4d_logo.png"),
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
        self.setup_top_menu()
        self.create_sidebar()
        self.create_main_editor()
        self.create_toolbar()
        self.create_context_menu()
        self.create_footer()
        # Add terminal after other UI elements
        self.create_terminal()
        # Setup output redirection after terminal creation
        self.setup_output_redirection()
        # Initialize variables
        self.current_file = None
        self.slides = []
        self.current_slide_index = -1

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Setup Python paths
        setup_python_paths()


        # Adjust grid weights to accommodate terminal
        self.grid_rowconfigure(1, weight=3)  # Main editor
        self.grid_rowconfigure(4, weight=1)  # Terminal

        # Setup output redirection after terminal creation
        self.setup_output_redirection()
#--------------------------------------------------------------------------------
        # Change to working directory if valid
        try:
            if self.session_data['working_directory']:
                os.chdir(self.session_data['working_directory'])
        except Exception as e:
            print(f"Warning: Could not change to saved working directory: {str(e)}")

        # Load last file if it exists
        if self.session_data['last_file'] and os.path.exists(self.session_data['last_file']):
            self.after(100, lambda: self.load_file(self.session_data['last_file']))

        # Bind window events
        self.bind('<Configure>', self.on_window_configure)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
    def setup_logo(self):
        """Initialize logo with colored ASCII fallback and path tracking"""
        try:
            # Store the original directory where the logo was found
            self.logo_dir = None

            # Check all possible logo locations
            possible_paths = [
                Path(__file__).parent / 'airis4d_logo.png',  # Current directory
                Path(__file__).parent / 'resources' / 'airis4d_logo.png',  # Local resources
                Path.home() / '.local' / 'lib' / 'bsg-ide' / 'airis4d_logo.png',  # User config directory
                Path('/usr/local/share/bsg-ide/resources/airis4d_logo.png'),  # System-wide installation
                Path(os.getenv('APPDATA', '')) / 'BSG-IDE' / 'resources' / 'airis4d_logo.png'  # Windows
            ]

            logo_path = None
            for path in possible_paths:
                if path.exists():
                    logo_path = path
                    self.logo_dir = path.parent
                    break

            if logo_path:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(50, 50)
                )
                self.has_logo = True
                print(f"✓ Loaded logo from {logo_path}")
            else:
                self.has_logo = False
                print("Using ASCII logo fallback - logo image not found")

        except Exception as e:
            print(f"Warning: Could not load logo image: {str(e)}")
            self.has_logo = False
#---------------------------------------------------------------------------------------

    def create_widgets(self):
        """Create and initialize all UI widgets"""
        try:
            # Create menu frame first
            self.setup_top_menu()

            # Configure grid
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Create main components
            self.create_sidebar()
            self.create_main_editor()
            self.create_toolbar()
            self.create_context_menu()
            self.create_footer()

            # Create terminal after other UI elements
            self.create_terminal()

            # Setup output redirection after terminal creation
            self.setup_output_redirection()

            # Initialize variables
            self.current_file = None
            self.slides = []
            self.current_slide_index = -1

            # Setup keyboard shortcuts
            self.setup_keyboard_shortcuts()

            # Setup Python paths
            setup_python_paths()

            # Adjust grid weights to accommodate terminal
            self.grid_rowconfigure(1, weight=3)  # Main editor
            self.grid_rowconfigure(4, weight=1)  # Terminal

            # Initialize syntax highlighter
            self.syntax_highlighter = None
            if hasattr(self, 'content_editor'):
                self.syntax_highlighter = BeamerSyntaxHighlighter(self.content_editor)

            # Create notes highlighter if notes editor exists
            if hasattr(self, 'notes_editor'):
                self.notes_highlighter = BeamerSyntaxHighlighter(self.notes_editor)

        except Exception as e:
            print(f"Error creating widgets: {str(e)}")
            raise

    def create_recent_files_menu(self):
        """Create recent files menu with error handling"""
        try:
            recent_menu = tk.Menu(self.menu_frame, tearoff=0)
            for filepath in self.session_data['recent_files']:
                if os.path.exists(filepath):
                    recent_menu.add_command(
                        label=os.path.basename(filepath),
                        command=lambda f=filepath: self.load_file(f)
                    )

            if recent_menu.index('end') is not None:  # Only add if menu has items
                self.menu_frame.add_cascade(label="Recent Files", menu=recent_menu)
        except Exception as e:
            print(f"Warning: Could not create recent files menu: {str(e)}")


    def update_recent_files(self, filepath):
        """Update recent files list"""
        if filepath not in self.session_data['recent_files']:
            self.session_data['recent_files'].append(filepath)
        if len(self.session_data['recent_files']) > 10:
            self.session_data['recent_files'].pop(0)
        self.create_recent_files_menu()

    def on_window_configure(self, event=None):
        """Track window size and position changes"""
        if event and event.widget == self:
            self.session_data['window_size'] = {
                'width': self.winfo_width(),
                'height': self.winfo_height()
            }
            self.session_data['window_position'] = {
                'x': self.winfo_x(),
                'y': self.winfo_y()
            }

    def on_closing(self):
        """Handle window closing with error handling"""
        try:
            if self.session_manager:
                # Update session data
                self.session_data.update({
                    'last_file': self.current_file,
                    'working_directory': os.getcwd()
                })

                # Save session
                self.session_manager.save_session(self.session_data)
        except Exception as e:
            print(f"Warning: Could not save session on exit: {str(e)}")
        finally:
            # Always close window
            self.destroy()

    def load_file(self, filename):
        """Override load_file with error handling"""
        try:
            super().load_file(filename)  # Call original load_file

            # Update session data if available
            if hasattr(self, 'session_data'):
                self.session_data['last_file'] = filename
                self.session_data['working_directory'] = os.path.dirname(filename) or '.'
                self.update_recent_files(filename)

                # Update terminal directory
                if hasattr(self, 'terminal'):
                    self.terminal.set_working_directory(self.session_data['working_directory'])
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            messagebox.showerror("Error", f"Could not load file:\n{str(e)}")


#--------------------------------------------------------------------------------
    def ide_callback(self, action, data):
        """Enhanced IDE callback handler with proper \\None handling"""
        if action == "update_current_slide":
            # Update slide title
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, data.get('title', ''))

            # Ensure proper highlight in slide list
            self.current_slide_index = data.get('index', 0)
            self.update_slide_list()
            self.highlight_current_slide()

            # Important: Reset media when changing slides
            self.media_entry.delete(0, 'end')

        elif action == "update_content":
            # Update content editor, ensuring clean state
            self.content_editor.delete('1.0', 'end')
            for line in data.get('content', []):
                if line and line.strip():  # Only add non-empty lines
                    self.content_editor.insert('end', f"{line}\n")

        elif action == "update_media":
            # Update media entry with proper \None handling
            self.media_entry.delete(0, 'end')
            media = data.get('media')

            # Handle different media cases
            if media is None or media == "\\None":
                self.media_entry.insert(0, "\\None")
            elif media:  # Only insert if there's actual media content
                self.media_entry.insert(0, media)

        elif action == "show_current_slide":
            # Show complete slide with proper state reset
            self.current_slide_index = data.get('index', 0)

            # Clear everything first
            self.title_entry.delete(0, 'end')
            self.media_entry.delete(0, 'end')
            self.content_editor.delete('1.0', 'end')

            # Update title
            if title := data.get('title'):
                self.title_entry.insert(0, title)

            # Update media with explicit \None handling
            media = data.get('media')
            if media is None or media == "\\None":
                self.media_entry.insert(0, "\\None")
            elif media:
                self.media_entry.insert(0, media)

            # Update content
            content = data.get('content', [])
            if content:
                for line in content:
                    if line and line.strip():
                        self.content_editor.insert('end', f"{line}\n")

            # Update slide list display
            self.update_slide_list()
            self.slide_list.see(f"{self.current_slide_index + 1}.0")
            self.highlight_current_slide()

        elif action == "navigate_to_slide":
            # Navigate to specific slide with complete state reset
            index = data.get('index', 0)
            if 0 <= index < len(self.slides):
                # Clear current state
                self.media_entry.delete(0, 'end')
                self.content_editor.delete('1.0', 'end')

                self.current_slide_index = index
                self.load_slide(index)
                self.update_slide_list()

                if data.get('focus'):
                    self.slide_list.see(f"{index + 1}.0")
                    self.highlight_current_slide()

        elif action == "error":
            # Show error in terminal
            if hasattr(self, 'terminal'):
                self.terminal.write(f"Error: {data.get('message', 'Unknown error')}\n", "red")

    def load_slide(self, index):
        """Enhanced load_slide with proper media handling"""
        if 0 <= index < len(self.slides):
            slide = self.slides[index]

            # Clear all fields first
            self.title_entry.delete(0, 'end')
            self.media_entry.delete(0, 'end')
            self.content_editor.delete('1.0', 'end')

            # Update title
            self.title_entry.insert(0, slide.get('title', ''))

            # Update media with explicit \None handling
            media = slide.get('media', '')
            if not media or media == "\\None":
                self.media_entry.insert(0, "\\None")
            else:
                self.media_entry.insert(0, media)

            # Update content
            for item in slide.get('content', []):
                if item and item.strip():
                    if not item.startswith('-'):
                        item = f"- {item}"
                    self.content_editor.insert('end', f"{item}\n")

            # Refresh syntax highlighting if active
            if hasattr(self, 'syntax_highlighter') and self.syntax_highlighter.active:
                self.syntax_highlighter.highlight()

    def update_slide_list(self):
        """Update slide list with improved current slide handling"""
        self.slide_list.delete('1.0', 'end')
        for i, slide in enumerate(self.slides):
            prefix = "→ " if i == self.current_slide_index else "  "
            title = slide.get('title', 'Untitled')
            media_type = " [None]" if not slide.get('media') or slide.get('media') == "\\None" else ""
            self.slide_list.insert('end', f"{prefix}Slide {i+1}: {title}{media_type}\n")

        self.highlight_current_slide()

    def highlight_current_slide(self):
        """Highlight current slide in list"""
        # Remove previous highlight
        self.slide_list.tag_remove('selected', '1.0', 'end')

        # Add highlight to current slide
        if self.current_slide_index >= 0:
            start = f"{self.current_slide_index + 1}.0"
            self.slide_list.see(start)  # Ensure visible
            end = f"{self.current_slide_index + 1}.end"
            self.slide_list.tag_add('selected', start, end)
            self.slide_list.tag_config('selected', background='#2F3542')
#--------------------------------------------------------------------------------------------------------------------
    def setup_output_redirection(self):
        """Set up output redirection to terminal"""
        if hasattr(self, 'terminal'):
            sys.stdout = SimpleRedirector(self.terminal, "white")
            sys.stderr = SimpleRedirector(self.terminal, "red")

    # Method to update working directory
    def update_terminal_directory(self, directory: str) -> None:
        """Update terminal working directory"""
        if hasattr(self, 'terminal'):
            self.terminal.set_working_directory(directory)
#---------------------------------------------------------------------------New run pdflatex ----------------
    # First, add an input method to handle terminal input
    def terminal_input(self, prompt: str) -> str:
        """Get input from terminal with prompt"""
        try:
            self.write(prompt, "yellow")
            # Use terminal's built-in input handling
            future_input = []
            input_ready = threading.Event()

            def on_input(text):
                future_input.append(text)
                input_ready.set()

            # Store current input handler
            old_handler = self.terminal._handle_input

            # Set temporary input handler
            def temp_handler(event):
                text = self.terminal.display._textbox.get("insert linestart", "insert lineend")
                if text.startswith("$ "):
                    text = text[2:].strip()
                    self.terminal.write("\n")
                    on_input(text)
                    return "break"
                return "break"

            self.terminal.display.bind("<Return>", temp_handler)

            # Wait for input
            input_ready.wait()

            # Restore original handler
            self.terminal.display.bind("<Return>", old_handler)

            return future_input[0] if future_input else ""

        except Exception as e:
            self.write(f"Error getting input: {str(e)}\n", "red")
            return ""

    def navigate_slides(self, event):
        """Handle keyboard navigation between slides"""
        if not self.slides:
            return

        # Save current slide before navigation
        self.save_current_slide()

        if event.keysym == 'Up':
            if self.current_slide_index > 0:
                self.current_slide_index -= 1
        elif event.keysym == 'Down':
            if self.current_slide_index < len(self.slides) - 1:
                self.current_slide_index += 1
        elif event.keysym == 'Left':
            if self.current_slide_index > 0:
                self.current_slide_index -= 1
        elif event.keysym == 'Right':
            if self.current_slide_index < len(self.slides) - 1:
                self.current_slide_index += 1

        # Load the new slide
        self.load_slide(self.current_slide_index)
        self.update_slide_list()

        # Ensure the current slide is visible in the list
        line_number = self.current_slide_index + 1
        self.slide_list.see(f"{line_number}.0")

        # Update visual highlighting
        self.highlight_current_slide()

        return "break"  # Prevent default handling
    #----------------------------------------------------------------
    def write_to_terminal(self, text: str, color: str = "white") -> None:
        """Alias for write method to maintain compatibility"""
        self.write(text, color)


    def create_terminal(self) -> None:
        """Create terminal initially hidden"""
        # Create terminal instance
        self.terminal = InteractiveTerminal(self, initial_directory=os.getcwd())
        self.terminal.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(4, weight=0)  # Initially no weight

        # Hide terminal initially
        self.terminal.grid_remove()

        # Set up redirections
        sys.stdout = SimpleRedirector(self.terminal, "white")
        sys.stderr = SimpleRedirector(self.terminal, "red")

        # Store process reference
        self.current_process = None

    def toggle_terminal(self) -> None:
        """Toggle terminal visibility"""
        self.terminal_visible = not self.terminal_visible

        if self.terminal_visible:
            # Show terminal
            self.terminal.grid()
            self.grid_rowconfigure(4, weight=1)  # Give weight when visible
            self.terminal_button.configure(text="▼ Hide Terminal")

            # Optionally resize window to accommodate terminal
            current_height = self.winfo_height()
            if current_height < 800:  # Minimum height with terminal
                new_height = min(800, self.winfo_screenheight() - 100)
                self.geometry(f"{self.winfo_width()}x{new_height}")
        else:
            # Hide terminal
            self.terminal.grid_remove()
            self.grid_rowconfigure(4, weight=0)  # Remove weight when hidden
            self.terminal_button.configure(text="▲ Show Terminal")

            # Optionally resize window back
            if self.winfo_height() > 600:  # Minimum height without terminal
                self.geometry(f"{self.winfo_width()}x600")


    def flush(self):
        """Required for stdout/stderr redirection"""
        pass

    # Replace the clear_terminal method
    def clear_terminal(self) -> None:
        """Clear terminal content"""
        if hasattr(self, 'terminal'):
            self.terminal.clear()

    def stop_compilation(self) -> None:
        """Stop current compilation process"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.write("\n[Compilation process terminated by user]\n")
            except:
                pass
            finally:
                self.current_process = None

#--------------------------------------------------------------------------------------------------------------------
    def create_footer(self):
        """Create footer with institution info and properly tracked logo"""
        # Footer frame with dark theme
        self.footer = ctk.CTkFrame(self)
        self.footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Left side - Logo and Institution name
        left_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        left_frame.pack(side="left", padx=10)

        # Add terminal toggle button
        self.terminal_visible = False
        self.terminal_button = ctk.CTkButton(
            left_frame,
            text="▲ Show Terminal",
            command=self.toggle_terminal,
            width=120,
            height=24,
            fg_color="#2F3542",
            hover_color="#404859"
        )
        self.terminal_button.pack(side="left", padx=10)

        # Logo (image or ASCII)
        if self.has_logo and hasattr(self, 'logo_image'):
            try:
                logo_label = ctk.CTkLabel(
                    left_frame,
                    image=self.logo_image,
                    text=""
                )
                logo_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Warning: Could not create logo label: {e}")
                self.create_ascii_logo(left_frame)
        else:
            self.create_ascii_logo(left_frame)

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

    def create_ascii_logo(self, parent):
        """Create ASCII logo as fallback"""
        logo_label = ctk.CTkLabel(
            parent,
            text=self.logo_ascii,
            font=("Courier", 10),
            justify="left"
        )
        logo_label.pack(side="left", padx=(0, 10))

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
    def setup_top_menu(self) -> None:
        """Create top menu bar with proper spacing and visibility"""
        # Main menu container
        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Configure menu frame grid properly
        self.menu_frame.grid_columnconfigure(1, weight=1)  # Make middle section expandable

        # Left side buttons with fixed minimum widths
        left_buttons = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        left_buttons.grid(row=0, column=0, sticky="w", padx=5)

        # Add menu buttons with minimum width
        menu_buttons = [
            ("Edit Preamble", self.edit_preamble, "Edit LaTeX preamble"),
            ("Presentation Settings", self.show_settings_dialog, "Configure presentation settings"),
            ("Get Source", self.get_source_from_tex, "Extract source from TEX file")
        ]

        for i, (text, command, tooltip) in enumerate(menu_buttons):
            btn = ctk.CTkButton(
                left_buttons,
                text=text,
                command=command,
                width=130  # Fixed minimum width for buttons
            )
            btn.pack(side="left", padx=5)
            self.create_tooltip(btn, tooltip)

        # Right side buttons
        right_buttons = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        right_buttons.grid(row=0, column=1, sticky="e", padx=5)

        # Add syntax highlighting switch
        self.highlight_var = ctk.BooleanVar(value=True)
        self.highlight_switch = ctk.CTkSwitch(
            right_buttons,
            text="Syntax Highlighting",
            variable=self.highlight_var,
            command=self.toggle_highlighting,
            width=150  # Fixed minimum width for switch
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

    def create_sidebar(self) -> None:
        """Create sidebar with slide list and controls including insert slide below"""
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

        # Slide control buttons with enhanced tooltips
        button_data = [
            ("New Slide", self.new_slide, "Add a new slide at the end"),
            ("Insert Below", self.insert_slide_below, "Insert a new slide below current"),
            ("Duplicate Slide", self.duplicate_slide, "Create a copy of current slide"),
            ("Delete Slide", self.delete_slide, "Remove current slide"),
            ("Move Up", lambda: self.move_slide(-1), "Move current slide up"),
            ("Move Down", lambda: self.move_slide(1), "Move current slide down")
        ]

        for i, (text, command, tooltip) in enumerate(button_data, start=2):
            btn = ctk.CTkButton(self.sidebar, text=text, command=command)
            btn.grid(row=i, column=0, padx=5, pady=5)
            self.create_tooltip(btn, tooltip)

    def insert_slide_below(self) -> None:
        """Insert a new slide below the current slide"""
        # Save current slide first
        self.save_current_slide()

        new_slide = {
            'title': 'New Slide',
            'media': '',
            'content': [],
            'notes': []
        }

        # If there are no slides or current_slide_index is invalid
        if not self.slides or self.current_slide_index < 0:
            self.slides.append(new_slide)
            self.current_slide_index = 0
        else:
            # Insert after current slide
            insert_position = self.current_slide_index + 1
            self.slides.insert(insert_position, new_slide)
            self.current_slide_index = insert_position

        # Update UI
        self.update_slide_list()
        self.load_slide(self.current_slide_index)

        # Focus title entry for immediate editing
        self.title_entry.focus_set()
        self.title_entry.select_range(0, 'end')

    # Add keyboard shortcut for insert slide below
    def setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for slide operations"""
        self.bind('<Control-n>', lambda e: self.new_slide())          # Ctrl+N for new slide
        self.bind('<Control-i>', lambda e: self.insert_slide_below()) # Ctrl+I for insert below
        self.bind('<Control-d>', lambda e: self.duplicate_slide())    # Ctrl+D for duplicate
        self.bind('<Control-Delete>', lambda e: self.delete_slide())          # Delete for remove slide
        self.bind('<Control-s>', lambda e: self.save_file())          # Ctrl+S for save




    def on_list_focus(self, event) -> None:
        """Handle slide list focus"""
        self.highlight_current_slide()
        # Visual feedback that list is focused
        self.slide_list.configure(border_color="#4ECDC4")

    def on_list_unfocus(self, event) -> None:
        """Handle slide list losing focus"""
        # Remove focus visual feedback
        self.slide_list.configure(border_color="")



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
        """Create main editor area with enhanced media controls and all original features"""
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Title section
        title_frame = ctk.CTkFrame(self.editor_frame)
        title_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(title_frame, text="Title:").pack(side="left", padx=5)
        self.title_entry = ctk.CTkEntry(title_frame, width=400)
        self.title_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Enhanced Media section
        media_frame = ctk.CTkFrame(self.editor_frame)
        media_frame.pack(fill="x", padx=5, pady=5)

        # Media label and entry
        media_label_frame = ctk.CTkFrame(media_frame)
        media_label_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(media_label_frame, text="Media:").pack(side="left", padx=5)
        self.media_entry = ctk.CTkEntry(media_label_frame, width=300)
        self.media_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Media buttons with both standard and capture tools
        media_buttons = ctk.CTkFrame(media_frame)
        media_buttons.pack(side="right", padx=5)

        # Standard media buttons
        standard_buttons = [
            ("Local File", self.browse_media, "Browse local media files"),
            ("YouTube", self.youtube_dialog, "Add YouTube video"),
            ("Search Images", self.search_images, "Search for images online")
        ]

        for text, command, tooltip in standard_buttons:
            btn = ctk.CTkButton(
                media_buttons,
                text=text,
                command=command,
                width=90
            )
            btn.pack(side="left", padx=2)
            self.create_tooltip(btn, tooltip)

        # Add separator
        separator = ttk.Separator(media_buttons, orient="vertical")
        separator.pack(side="left", padx=5, pady=5, fill="y")

        # Capture buttons
        capture_buttons = [
            ("📷 Camera", self.open_camera, "Capture from camera"),
            ("🖥️ Screen", self.capture_screen, "Capture screen area"),
            ("❌ No Media", lambda: self.media_entry.insert(0, "\\None"), "Create slide without media")
        ]

        for text, command, tooltip in capture_buttons:
            btn = ctk.CTkButton(
                media_buttons,
                text=text,
                command=command,
                width=90,
                fg_color="#4A90E2",
                hover_color="#357ABD"
            )
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

    def check_dependencies(self) -> dict:
        """Check if required packages are installed in current environment"""
        dependencies = {
            'PIL': {'import_name': 'PIL', 'package_name': 'pillow', 'installed': False},
            'pyautogui': {'import_name': 'pyautogui', 'package_name': 'pyautogui', 'installed': False},
            'cv2': {'import_name': 'cv2', 'package_name': 'opencv-python', 'installed': False}
        }

        for dep_name, dep_info in dependencies.items():
            try:
                __import__(dep_info['import_name'])
                dep_info['installed'] = True
            except ImportError:
                dep_info['installed'] = False

        return dependencies

    def capture_screen(self) -> None:
        """Enhanced screen capture with proper dependency checking"""
        # Check only required dependencies for screen capture
        deps = self.check_dependencies()
        required_deps = ['PIL', 'pyautogui']
        missing_deps = [deps[d]['package_name'] for d in required_deps if not deps[d]['installed']]

        if missing_deps:
            messagebox.showerror(
                "Missing Dependencies",
                f"Screen capture requires the following packages:\n{', '.join(missing_deps)}\n\n" +
                "Please install using:\npip install " + " ".join(missing_deps)
            )
            return

        try:
            import pyautogui
            from PIL import ImageGrab, ImageDraw

            # Show information dialog
            messagebox.showinfo(
                "Screen Capture",
                "1. This window will minimize\n" +
                "2. Draw a rectangle by clicking and dragging\n" +
                "3. Press ESC to cancel"
            )

            # Minimize the window
            self.iconify()
            self.update()
            time.sleep(0.5)  # Give time for window to minimize

            # Create screen overlay for selection
            root = tk.Tk()
            root.attributes('-fullscreen', True, '-alpha', 0.3)
            root.configure(background='black')

            # Variables for selection
            start_x = start_y = end_x = end_y = 0
            selection = None
            is_selecting = False

            def on_mouse_down(event):
                nonlocal start_x, start_y, is_selecting
                start_x, start_y = event.x, event.y
                is_selecting = True

            def on_mouse_move(event):
                nonlocal selection, end_x, end_y
                if is_selecting:
                    end_x, end_y = event.x, event.y
                    if selection:
                        root.delete(selection)
                    selection = root.create_rectangle(
                        start_x, start_y, end_x, end_y,
                        outline='white'
                    )

            def on_mouse_up(event):
                nonlocal is_selecting
                is_selecting = False
                root.destroy()

                try:
                    # Ensure coordinates are positive
                    x1, x2 = min(start_x, end_x), max(start_x, end_x)
                    y1, y2 = min(start_y, end_y), max(start_y, end_y)

                    # Add padding to ensure we get the full selection
                    padding = 2
                    bbox = (x1-padding, y1-padding, x2+padding, y2+padding)

                    # Capture the selected area
                    screenshot = ImageGrab.grab(bbox=bbox)

                    # Create media_files directory if it doesn't exist
                    os.makedirs('media_files', exist_ok=True)

                    # Save the image
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = f"screen_capture_{timestamp}.png"
                    filepath = os.path.join('media_files', filename)
                    screenshot.save(filepath)

                    # Update media entry
                    self.media_entry.delete(0, 'end')
                    self.media_entry.insert(0, f"\\file media_files/{filename}")

                    # Show success message
                    messagebox.showinfo(
                        "Success",
                        f"Screen capture saved as:\n{filename}"
                    )

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to capture screen area:\n{str(e)}"
                    )
                finally:
                    # Restore window
                    self.deiconify()

            # Bind events
            root.bind('<Escape>', lambda e: (root.destroy(), self.deiconify()))
            root.bind('<ButtonPress-1>', on_mouse_down)
            root.bind('<B1-Motion>', on_mouse_move)
            root.bind('<ButtonRelease-1>', on_mouse_up)

            # Create canvas for drawing selection
            canvas = tk.Canvas(root, highlightthickness=0)
            canvas.pack(fill='both', expand=True)

            root.mainloop()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Screen capture failed:\n{str(e)}"
            )
            self.deiconify()


 #-------------------------------Get Camera and Set Camera--------------------------------------------
    def open_camera(self) -> None:
            """Enhanced cross-platform camera capture with full feature set"""
            try:
                # Check for required imports
                import cv2
                from PIL import Image, ImageTk
                import platform
                from pathlib import Path
                import subprocess
                import time
                import sys

                # Create media_files directory if it doesn't exist
                os.makedirs('media_files', exist_ok=True)

                def get_available_cameras():
                    """Get list of available cameras with proper device detection for all platforms"""
                    available_cameras = []
                    system = platform.system()

                    def check_camera(index, device_path=None, device_name=None):
                        """Helper to check camera capabilities across different platforms"""
                        try:
                            # Initialize camera based on platform
                            if device_path and system == "Linux":
                                cap = cv2.VideoCapture(device_path)
                            elif system == "Windows":
                                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Use DirectShow on Windows
                            else:
                                cap = cv2.VideoCapture(index)

                            if cap.isOpened():
                                ret, _ = cap.read()
                                if ret:
                                    # Store original settings
                                    original_settings = {
                                        cv2.CAP_PROP_FRAME_WIDTH: cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                                        cv2.CAP_PROP_FRAME_HEIGHT: cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                                        cv2.CAP_PROP_FPS: cap.get(cv2.CAP_PROP_FPS),
                                        cv2.CAP_PROP_BRIGHTNESS: cap.get(cv2.CAP_PROP_BRIGHTNESS),
                                        cv2.CAP_PROP_CONTRAST: cap.get(cv2.CAP_PROP_CONTRAST),
                                        cv2.CAP_PROP_SATURATION: cap.get(cv2.CAP_PROP_SATURATION)
                                    }

                                    # Test resolutions with platform-specific considerations
                                    test_resolutions = [
                                        (3840, 2160),  # 4K
                                        (2560, 1440),  # 2K
                                        (1920, 1080),  # Full HD
                                        (1280, 720),   # HD
                                        (800, 600),    # SVGA
                                        (640, 480)     # VGA
                                    ]

                                    supported_resolutions = []
                                    highest_resolution = None

                                    for width, height in test_resolutions:
                                        try:
                                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                                            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                                            # Verify resolution with actual capture
                                            if actual_w > 0 and actual_h > 0:
                                                test_ret, test_frame = cap.read()
                                                if test_ret and test_frame is not None:
                                                    resolution = f"{actual_w}x{actual_h}"
                                                    if resolution not in supported_resolutions:
                                                        supported_resolutions.append(resolution)
                                                        if not highest_resolution or (actual_w * actual_h > highest_resolution[0] * highest_resolution[1]):
                                                            highest_resolution = (actual_w, actual_h)
                                        except:
                                            continue

                                    # Restore original settings
                                    for prop, value in original_settings.items():
                                        try:
                                            cap.set(prop, value)
                                        except:
                                            pass

                                    # Get current settings after restore
                                    current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                    current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                    current_fps = int(cap.get(cv2.CAP_PROP_FPS))

                                    # Build camera info dictionary with platform-specific details
                                    camera_info = {
                                        'index': index,
                                        'device_path': device_path,
                                        'name': device_name or f"Camera {index}",
                                        'current_resolution': f"{current_width}x{current_height}",
                                        'supported_resolutions': supported_resolutions,
                                        'highest_resolution': highest_resolution,
                                        'fps': current_fps,
                                        'original_settings': original_settings,
                                        'platform': system
                                    }

                                    cap.release()
                                    return camera_info

                            if cap.isOpened():
                                cap.release()
                        except Exception as e:
                            print(f"Error checking camera {index}: {e}")
                        return None

                    # Platform-specific camera detection
                    if system == "Linux":
                        # Linux: Check /dev/video* devices with udev information
                        try:
                            import glob
                            import pyudev
                            video_devices = sorted(glob.glob('/dev/video*'))
                            context = pyudev.Context()

                            for device_path in video_devices:
                                try:
                                    device = pyudev.Devices.from_device_file(context, device_path)
                                    # Get detailed device information
                                    device_name = device.get('ID_MODEL', '')
                                    vendor = device.get('ID_VENDOR_ID', '')
                                    product = device.get('ID_MODEL_ID', '')

                                    if not device_name:
                                        device_name = f"Camera ({device_path})"
                                    elif vendor and product:
                                        device_name = f"{device_name} ({vendor}:{product})"

                                    index = int(device_path.split('video')[-1])
                                    camera = check_camera(index, device_path, device_name)
                                    if camera:
                                        # Add additional Linux-specific information
                                        camera['device_info'] = {
                                            'vendor': vendor,
                                            'product': product,
                                            'subsystem': device.get('SUBSYSTEM', ''),
                                            'driver': device.get('ID_V4L_DRIVER', '')
                                        }
                                        available_cameras.append(camera)
                                except Exception as e:
                                    print(f"Error processing Linux device {device_path}: {e}")
                                    continue

                        except ImportError:
                            # Fallback if pyudev not available
                            for i in range(10):  # Check first 10 indices
                                camera = check_camera(i)
                                if camera:
                                    available_cameras.append(camera)

                    elif system == "Darwin":  # macOS
                        # Try built-in camera first with specific name
                        camera = check_camera(0, device_name="FaceTime Camera")
                        if camera:
                            # Add macOS-specific information
                            camera['is_builtin'] = True
                            available_cameras.append(camera)

                        # Check additional cameras
                        for i in range(1, 5):
                            camera = check_camera(i)
                            if camera:
                                camera['is_builtin'] = False
                                available_cameras.append(camera)

                    else:  # Windows
                        try:
                            # Try using Windows Management Instrumentation for device info
                            import win32com.client
                            wmi = win32com.client.GetObject("winmgmts:")

                            # Get all video devices from WMI
                            cameras_wmi = {}
                            for device in wmi.InstancesOf("Win32_PnPEntity"):
                                if "Camera" in device.Name or "Webcam" in device.Name:
                                    cameras_wmi[device.DeviceID] = device.Name

                            # Check available cameras with DirectShow
                            for i in range(10):  # Check first 10 indices
                                try:
                                    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                                    if cap.isOpened():
                                        # Try to match with WMI device
                                        device_name = next(
                                            (name for id, name in cameras_wmi.items() if str(i) in id),
                                            f"Camera {i}"
                                        )
                                        camera = check_camera(i, device_name=device_name)
                                        if camera:
                                            available_cameras.append(camera)
                                    cap.release()
                                except:
                                    continue

                        except ImportError:
                            # Fallback if WMI access fails
                            for i in range(10):
                                camera = check_camera(i)
                                if camera:
                                    available_cameras.append(camera)

                    return available_cameras

                def start_camera_capture(camera_index, camera_info=None):  # Modified to accept camera_info
                    """Initialize and start camera capture with camera-specific highest resolution"""
                    try:
                        # Create camera dialog
                        dialog = ctk.CTkToplevel(self)
                        dialog.title("Camera Capture")
                        dialog.geometry("800x600")
                        dialog.transient(self)
                        dialog.grab_set()

                        # Center the dialog
                        dialog.update_idletasks()
                        x = (dialog.winfo_screenwidth() - 800) // 2
                        y = (dialog.winfo_screenheight() - 600) // 2
                        dialog.geometry(f"+{x}+{y}")

                        # Initialize camera
                        #cap = cv2.VideoCapture(camera_index)
                        # Initialize camera with default settings
                        if platform.system() == "Linux" and camera_info.get('device_path'):
                            cap = cv2.VideoCapture(camera_info['device_path'])
                        else:
                            cap = cv2.VideoCapture(camera_index)
                        if not cap.isOpened():
                            raise Exception(f"Could not open camera {camera_index}")
                        max_res=None
                        # Only set resolution if highest_resolution is available for this camera
                        if camera_info.get('highest_resolution'):
                            width, height = camera_info['highest_resolution']
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                            # Get actual resolution achieved
                            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
                            max_res = (actual_width, actual_height)


                        # Create main content frame
                        content_frame = ctk.CTkFrame(dialog)
                        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

                        # Preview frame
                        preview_frame = ctk.CTkFrame(content_frame)
                        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

                        preview_label = tk.Label(preview_frame, background="black")
                        preview_label.pack(fill="both", expand=True)

                        # Status frame
                        status_frame = ctk.CTkFrame(dialog)
                        status_frame.pack(fill="x", padx=10, pady=5)

                        # Resolution label
                        if max_res:
                            res_text = f"Resolution: {max_res[0]}x{max_res[1]}"
                        else:
                            res_text = "Resolution: Unknown"

                        resolution_label = ctk.CTkLabel(
                            status_frame,
                            text=res_text,
                            font=("Arial", 12)
                        )
                        resolution_label.pack(side="left", padx=5)

                        # Status label
                        status_label = ctk.CTkLabel(
                            status_frame,
                            text="",
                            font=("Arial", 12)
                        )
                        status_label.pack(side="right", padx=5)

                        # Control frame
                        control_frame = ctk.CTkFrame(dialog)
                        control_frame.pack(fill="x", padx=10, pady=5)

                        # Variables for recording
                        recording_data = {
                            'is_recording': False,
                            'start_time': None,
                            'output': None,
                            'current_file': None
                        }

                        def create_camera_controls(dialog, cap, preview_frame, status_label, recording_data):
                            """Create enhanced camera controls with resolution and file management"""
                            # Create control panels
                            settings_frame = ctk.CTkFrame(dialog)
                            settings_frame.pack(fill="x", padx=10, pady=5)

                            # Resolution controls
                            resolution_frame = ctk.CTkFrame(settings_frame)
                            resolution_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)

                            resolutions = [
                                "3840x2160 (4K)",
                                "1920x1080 (Full HD)",
                                "1280x720 (HD)",
                                "800x600 (SVGA)",
                                "640x480 (VGA)"
                            ]

                            current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            current_res = f"{current_width}x{current_height}"

                            ctk.CTkLabel(
                                resolution_frame,
                                text="Resolution:",
                                font=("Arial", 12)
                            ).pack(side="left", padx=5)

                            def change_resolution(choice):
                                try:
                                    width, height = map(int, choice.split()[0].split('x'))
                                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                                    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                                    if actual_width == width and actual_height == height:
                                        status_label.configure(text=f"Resolution changed to {width}x{height}")
                                    else:
                                        status_label.configure(
                                            text=f"Actual resolution: {actual_width}x{actual_height}"
                                        )
                                    dialog.after(2000, lambda: status_label.configure(text=""))
                                except Exception as e:
                                    status_label.configure(text=f"Error changing resolution: {str(e)}")
                                    dialog.after(2000, lambda: status_label.configure(text=""))

                            resolution_menu = ctk.CTkOptionMenu(
                                resolution_frame,
                                values=resolutions,
                                command=change_resolution,
                                width=150
                            )
                            resolution_menu.pack(side="left", padx=5)

                            # Set current resolution in menu
                            for res in resolutions:
                                if res.startswith(current_res):
                                    resolution_menu.set(res)
                                    break

                            # File management functions
                            def get_save_location(default_name, file_type):
                                """Get save location with custom filename"""
                                file_types = {
                                    'photo': [('PNG files', '*.png'), ('JPEG files', '*.jpg')],
                                    'video': [('MP4 files', '*.mp4'), ('AVI files', '*.avi')]
                                }

                                initialdir = os.path.abspath('media_files')
                                if not os.path.exists(initialdir):
                                    os.makedirs(initialdir)

                                return filedialog.asksaveasfilename(
                                    initialfile=default_name,
                                    defaultextension=file_types[file_type][0][1],
                                    filetypes=file_types[file_type],
                                    initialdir=initialdir,
                                    title=f"Save {file_type.title()} As"
                                )

                            def capture_photo():
                                """Enhanced photo capture with custom save location"""
                                try:
                                    ret, frame = cap.read()
                                    if ret:
                                        # Convert to RGB for PIL
                                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                        image = Image.fromarray(rgb_frame)

                                        # Default filename
                                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                                        default_name = f"camera_photo_{timestamp}.png"

                                        # Get save location
                                        filepath = get_save_location(default_name, 'photo')
                                        if not filepath:  # User cancelled
                                            return

                                        # Save image
                                        image.save(filepath)

                                        # Update media entry with relative path if in media_files
                                        rel_path = os.path.relpath(filepath, 'media_files')
                                        if not rel_path.startswith('..'):
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file media_files/{rel_path}")
                                        else:
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file {filepath}")

                                        # Show success message
                                        status_label.configure(text="✓ Photo saved!")
                                        dialog.after(2000, lambda: status_label.configure(text=""))

                                        # Flash effect
                                        preview_frame.configure(fg_color="white")
                                        dialog.after(100, lambda: preview_frame.configure(fg_color="black"))

                                except Exception as e:
                                    status_label.configure(text=f"Error: {str(e)}")
                                    dialog.after(2000, lambda: status_label.configure(text=""))

                            def toggle_recording():
                                """Enhanced video recording with custom save location"""
                                try:
                                    if not recording_data['is_recording']:
                                        # Get save location first
                                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                                        default_name = f"camera_video_{timestamp}.mp4"
                                        filepath = get_save_location(default_name, 'video')

                                        if not filepath:  # User cancelled
                                            return

                                        # Start recording
                                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                        fps = int(cap.get(cv2.CAP_PROP_FPS))

                                        # Create video writer
                                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                                        recording_data['output'] = cv2.VideoWriter(
                                            filepath, fourcc, fps, (width, height)
                                        )
                                        recording_data['current_file'] = filepath
                                        recording_data['is_recording'] = True
                                        recording_data['start_time'] = time.time()

                                        # Update UI
                                        record_button.configure(
                                            text="Stop Recording",
                                            fg_color="#FF4444",
                                            hover_color="#CC3333"
                                        )
                                        photo_button.configure(state="disabled")
                                        resolution_menu.configure(state="disabled")
                                        update_recording_time()

                                    else:
                                        # Stop recording
                                        recording_data['is_recording'] = False
                                        if recording_data['output']:
                                            recording_data['output'].release()

                                        # Update media entry with relative path if in media_files
                                        filepath = recording_data['current_file']
                                        rel_path = os.path.relpath(filepath, 'media_files')
                                        if not rel_path.startswith('..'):
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file media_files/{rel_path}")
                                        else:
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file {filepath}")

                                        # Reset UI
                                        record_button.configure(
                                            text="Record Video",
                                            fg_color="#4A90E2",
                                            hover_color="#357ABD"
                                        )
                                        photo_button.configure(state="normal")
                                        resolution_menu.configure(state="normal")
                                        status_label.configure(text="✓ Video saved!")
                                        dialog.after(2000, lambda: status_label.configure(text=""))

                                except Exception as e:
                                    status_label.configure(text=f"Error: {str(e)}")
                                    dialog.after(2000, lambda: status_label.configure(text=""))
                                    recording_data['is_recording'] = False
                                    photo_button.configure(state="normal")
                                    resolution_menu.configure(state="normal")

                            def update_recording_time():
                                """Update recording duration display"""
                                if recording_data['is_recording']:
                                    elapsed = time.time() - recording_data['start_time']
                                    minutes = int(elapsed // 60)
                                    seconds = int(elapsed % 60)
                                    status_label.configure(
                                        text=f"Recording: {minutes:02d}:{seconds:02d} ({os.path.basename(recording_data['current_file'])})"
                                    )
                                    dialog.after(1000, update_recording_time)

                            # Create control buttons
                            control_frame = ctk.CTkFrame(dialog)
                            control_frame.pack(fill="x", padx=10, pady=5)

                            photo_button = ctk.CTkButton(
                                control_frame,
                                text="Take Photo",
                                command=capture_photo,
                                width=120,
                                font=("Arial", 13),
                                fg_color="#4A90E2",
                                hover_color="#357ABD"
                            )
                            photo_button.pack(side="left", padx=5)

                            record_button = ctk.CTkButton(
                                control_frame,
                                text="Record Video",
                                command=toggle_recording,
                                width=120,
                                font=("Arial", 13),
                                fg_color="#4A90E2",
                                hover_color="#357ABD"
                            )
                            record_button.pack(side="left", padx=5)

                            close_button = ctk.CTkButton(
                                control_frame,
                                text="Close",
                                command=dialog.destroy,
                                width=100,
                                font=("Arial", 13),
                                fg_color="#FF4444",
                                hover_color="#CC3333"
                            )
                            close_button.pack(side="right", padx=5)

                            return photo_button, record_button, resolution_menu



                        def close_camera():
                            """Clean up and close camera"""
                            try:
                                # Stop recording if active
                                if recording_data['is_recording']:
                                    recording_data['is_recording'] = False
                                    if recording_data['output']:
                                        recording_data['output'].release()

                                # Release camera
                                cap.release()
                                dialog.destroy()

                            except Exception as e:
                                print(f"Error closing camera: {str(e)}")
                                dialog.destroy()

                        # Create controls
                        photo_button, record_button, resolution_menu = create_camera_controls(
                            dialog, cap, preview_frame, status_label, recording_data
                        )

                        close_button = ctk.CTkButton(
                            control_frame,
                            text="Close",
                            command=close_camera,
                            width=100,
                            font=("Arial", 13),
                            fg_color="#FF4444",
                            hover_color="#CC3333"
                        )
                        close_button.pack(side="right", padx=5)

                        def update_preview():
                            """Update camera preview"""
                            if cap.isOpened():
                                ret, frame = cap.read()
                                if ret:
                                    # Record frame if recording
                                    if recording_data['is_recording']:
                                        recording_data['output'].write(frame)

                                    # Convert frame for display
                                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    image = Image.fromarray(rgb_frame)

                                    # Scale for display
                                    display_size = (800, 600)
                                    image.thumbnail(display_size, Image.Resampling.LANCZOS)

                                    # Convert to PhotoImage
                                    photo = ImageTk.PhotoImage(image=image)
                                    preview_label.configure(image=photo)
                                    preview_label.image = photo  # Keep reference

                                    # Schedule next update
                                    dialog.after(10, update_preview)

                        # Start preview
                        update_preview()

                        # Handle window closing
                        dialog.protocol("WM_DELETE_WINDOW", close_camera)

                    except Exception as e:
                        messagebox.showerror("Error", f"Camera initialization failed: {str(e)}")
                        dialog.destroy()

                # Main camera initialization
                cameras = get_available_cameras()
                if not cameras:
                    messagebox.showerror(
                        "No Cameras",
                        "No working cameras found.\nPlease connect a camera and try again."
                    )
                    return

                # Create camera selection dialog if multiple cameras found
                if len(cameras) > 1:
                    select_dialog = ctk.CTkToplevel(self)
                    select_dialog.title("Select Camera")
                    select_dialog.geometry("400x400")
                    select_dialog.transient(self)
                    select_dialog.grab_set()

                    # Center dialog
                    select_dialog.update_idletasks()
                    x = (select_dialog.winfo_screenwidth() - 400) // 2
                    y = (select_dialog.winfo_screenheight() - 400) // 2
                    select_dialog.geometry(f"+{x}+{y}")

                    # Title label
                    ctk.CTkLabel(
                        select_dialog,
                        text="Available Cameras",
                        font=("Arial", 16, "bold")
                    ).pack(pady=10, padx=20)

                    # Create scrollable frame for camera options
                    scroll_frame = ctk.CTkScrollableFrame(
                        select_dialog,
                        width=360,
                        height=280
                    )
                    scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

                    # Camera selection variable
                    selected_camera = tk.StringVar(value="0")  # Default to first camera

                    # Create radio buttons for each camera
                    for camera in cameras:
                        # Create frame for each camera option
                        camera_frame = ctk.CTkFrame(scroll_frame)
                        camera_frame.pack(fill="x", padx=5, pady=5)

                        # Radio button with camera name
                        rb = ctk.CTkRadioButton(
                            camera_frame,
                            text=camera['name'],
                            variable=selected_camera,
                            value=str(camera['index']),
                            font=("Arial", 13)
                        )
                        rb.pack(side="top", padx=10, pady=2, anchor="w")

                        # Add resolution and FPS info
                        info_text = f"Resolution: {camera['current_resolution']}"
                        if camera.get('supported_resolutions'):
                            info_text += f"\nSupported: {', '.join(camera['supported_resolutions'][:3])}"
                        if camera.get('fps'):
                            info_text += f"\nFPS: {camera['fps']}"

                        info_label = ctk.CTkLabel(
                            camera_frame,
                            text=info_text,
                            font=("Arial", 12),
                            justify="left",
                            text_color="gray"
                        )
                        info_label.pack(side="top", padx=30, pady=2, anchor="w")

                    # Create buttons frame
                    button_frame = ctk.CTkFrame(select_dialog)
                    button_frame.pack(fill="x", padx=10, pady=10)

                    def on_camera_selected():
                        camera_index = int(selected_camera.get())
                        selected_camera_info = next(
                            (cam for cam in cameras if cam['index'] == camera_index),
                            None
                        )
                        select_dialog.destroy()
                        # Start capture with selected camera
                        if selected_camera_info:
                            start_camera_capture(camera_index, selected_camera_info)


                        #start_camera_capture(camera_index)

                    # Select button
                    ctk.CTkButton(
                        button_frame,
                        text="Open Camera",
                        command=on_camera_selected,
                        width=200,
                        font=("Arial", 13),
                        fg_color="#4A90E2",
                        hover_color="#357ABD"
                    ).pack(side="left", padx=10)

                    # Cancel button
                    ctk.CTkButton(
                        button_frame,
                        text="Cancel",
                        command=select_dialog.destroy,
                        width=100,
                        font=("Arial", 13),
                        fg_color="#FF4444",
                        hover_color="#CC3333"
                    ).pack(side="right", padx=10)

                else:
                    # If only one camera, use it directly with its info
                    start_camera_capture(cameras[0]['index'], cameras[0])
                    # If only one camera, use it directly
                    #start_camera_capture(cameras[0]['index'])

            except ImportError as e:
                messagebox.showerror(
                    "Missing Dependencies",
                    "Camera capture requires additional modules.\n" +
                    "Please install required packages:\n\n" +
                    "pip install opencv-python pillow"
                )
            except Exception as e:
                messagebox.showerror(
                    "Camera Error",
                    f"Camera initialization failed:\n{str(e)}\n\n" +
                    "Please check your camera connection and permissions."
                )


 #----------------------------------------------------------------------------
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
        """Create main editor toolbar with presentation features"""
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Basic file operations buttons
        buttons = [
            ("New", self.new_file, "Create new presentation"),
            ("Open", self.open_file, "Open existing presentation"),
            ("Save", self.save_file, "Save current presentation"),
            ("Convert to TeX", self.convert_to_tex, "Convert to LaTeX format"),
            ("Generate PDF", self.generate_pdf, "Generate PDF file"),
            ("Present with Notes", self.present_with_notes, "Launch dual-screen presentation with notes"),
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
            elif text == "Present with Notes":
                btn = ctk.CTkButton(
                    self.toolbar,
                    text=text,
                    command=command,
                    width=120,
                    fg_color="#4A90E2",  # Distinctive blue color
                    hover_color="#357ABD"
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
            global working_folder
            # Change to tet file directory
            working_folder= os.path.dirname(filename) or '.'
            os.chdir(working_folder)

            # Update working directory in terminal
            self.terminal.set_working_directory(working_folder)

#-----------------------------------------------------------------------------
    def save_file(self) -> None:
        """Save presentation preserving custom preamble"""
        if not self.current_file:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.current_file = filename
                global working_folder
                # Change to tet file directory
                working_folder= os.path.dirname(filename) or '.'
                os.chdir(working_folder)

                # Update working directory in terminal
                self.terminal.set_working_directory(working_folder)
            else:
                return

        # Save current slide before generating content
        self.save_current_slide()

        try:
            # Get custom preamble with logo
            content = self.get_custom_preamble()

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

            self.write("✓ File saved successfully: " + self.current_file + "\n", "green")

        except Exception as e:
            self.write(f"✗ Error saving file: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error saving file:\n{str(e)}")

    def convert_media_to_latex(self, line: str) -> str:
        """Convert media directives to proper LaTeX commands"""
        if '\\file' in line:
            # Convert \file to \includegraphics
            media_path = line.split('\\file')[-1].strip()
            return f"\\includegraphics[width=0.48\\textwidth,keepaspectratio]{{{media_path}}}"
        elif '\\play' in line:
            # Handle play directives
            if '\\file' in line:
                media_path = line.split('\\file')[-1].strip()
                # Using raw string to handle nested braces
                return (r"\movie[externalviewer]{"
                       r"\includegraphics[width=0.48\textwidth,keepaspectratio]"
                       f"{{{media_path}}}}}{{{media_path}}}")
            elif '\\url' in line:
                url = line.split('\\url')[-1].strip()
                return f"\\href{{{url}}}{{\\textcolor{{blue}}{{Click to play video}}}}"
        elif '\\None' in line:
            return ""  # Return empty string for \None directive
        return line

    def convert_to_tex(self):
        """Convert text to TeX with real-time updates"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            self.save_file()
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            self.clear_terminal()
            self.write("Converting text to TeX...\n")

            from BeamerSlideGenerator import process_input_file
            processed, failed, errors = process_input_file(
                self.current_file,
                tex_file,
                ide_callback=self.ide_callback
            )

            if errors:
                for error in errors:
                    self.write(f"Error: {error}\n", "red")
            else:
                self.write("✓ Conversion completed successfully\n", "green")
                self.write(f"Processed: {processed}, Failed: {failed}\n")

        except Exception as e:
            self.write(f"✗ Error in conversion: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error converting to TeX:\n{str(e)}")

    def get_custom_preamble(self) -> str:
            """Generate custom preamble with proper logo handling"""
            try:
                # If we have a stored custom preamble, use it as base
                if hasattr(self, 'custom_preamble'):
                    base_preamble = self.custom_preamble
                else:
                    # Get base preamble from BeamerSlideGenerator
                    from BeamerSlideGenerator import get_beamer_preamble
                    base_preamble = get_beamer_preamble(
                        self.presentation_info['title'],
                        self.presentation_info['subtitle'],
                        self.presentation_info['author'],
                        self.presentation_info['institution'],
                        self.presentation_info['short_institute'],
                        self.presentation_info['date']
                    )

                # Process logo
                if 'logo' in self.presentation_info and self.presentation_info['logo']:
                    # Remove any existing logo commands
                    preamble = re.sub(
                        r'\\logo{[^}]*}\s*\n?',
                        '',
                        base_preamble
                    )

                    # Add our logo command just before \begin{document}
                    doc_pos = preamble.find("\\begin{document}")
                    if doc_pos != -1:
                        logo_command = self.presentation_info['logo'] + "\n\n"
                        preamble = preamble[:doc_pos] + logo_command + preamble[doc_pos:]
                    else:
                        # If no \begin{document} found, append logo at end
                        preamble = base_preamble + "\n" + self.presentation_info['logo'] + "\n"
                else:
                    preamble = base_preamble

                return preamble

            except Exception as e:
                print(f"Error generating custom preamble: {e}")
                # Fallback to default preamble without logo
                try:
                    from BeamerSlideGenerator import get_beamer_preamble
                    preamble = get_beamer_preamble(
                        self.presentation_info['title'],
                        self.presentation_info['subtitle'],
                        self.presentation_info['author'],
                        self.presentation_info['institution'],
                        self.presentation_info['short_institute'],
                        self.presentation_info['date']
                    )
                    # Remove default logo if any
                    preamble = re.sub(
                        r'\\logo{[^}]*}\s*\n?',
                        '',
                        preamble
                    )
                    return preamble
                except Exception as e2:
                    print(f"Error in fallback preamble generation: {e2}")
                    return ""
#------------------------------------------------------------------------------


    def generate_pdf(self) -> None:
        """Generate PDF with improved terminal handling and progress feedback"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Clear terminal
            self.clear_terminal()

            # Save current state
            self.save_current_slide()

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Step 1: Convert text to TeX first
            self.write("Step 1: Converting text to TeX...\n", "white")
            self.convert_to_tex()  # This will handle notes mode correctly

            # Step 2: First pdflatex pass
            self.write("\nStep 2: First pdflatex pass...\n", "white")
            success = self.run_pdflatex(tex_file)

            if success:
                # Step 3: Second pdflatex pass for references
                self.write("\nStep 3: Second pdflatex pass...\n", "white")
                success = self.run_pdflatex(tex_file)

                if success:
                    pdf_file = base_filename + '.pdf'
                    if os.path.exists(pdf_file):
                        # Calculate file size
                        size = os.path.getsize(pdf_file)
                        size_str = self.format_file_size(size)

                        self.write("\n✓ PDF generated successfully!\n", "green")
                        self.write(f"PDF Size: {size_str}\n", "green")

                        # Check for any warnings in the log file
                        log_file = base_filename + '.log'
                        if os.path.exists(log_file):
                            self.check_latex_log(log_file)

                        # Ask if user wants to view the PDF
                        if messagebox.askyesno("Success",
                                             f"PDF generated successfully!\nSize: {size_str}\n\nWould you like to view it now?"):
                            self.preview_pdf()
                    else:
                        self.write("\n✗ Error: PDF file not found after compilation\n", "red")
                else:
                    self.write("\n✗ Error in second pdflatex pass\n", "red")
            else:
                self.write("\n✗ Error in first pdflatex pass\n", "red")

        except Exception as e:
            error_msg = f"\n✗ Error generating PDF: {str(e)}\n"
            self.write(error_msg, "red")

            # Add detailed error information
            if hasattr(e, '__traceback__'):
                self.write("\nDetailed error information:\n", "red")
                self.write(traceback.format_exc(), "red")

            messagebox.showerror("Error", f"Error generating PDF:\n{str(e)}")

    def check_latex_log(self, log_file: str) -> None:
        """Check LaTeX log file for warnings and errors"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            # Check for common issues
            warnings = []
            errors = []

            warning_patterns = [
                r'Warning: ([^\n]+)',
                r'LaTeX Warning: ([^\n]+)',
                r'Package [^\n]+ Warning: ([^\n]+)'
            ]

            error_patterns = [
                r'! ([^\n]+)',
                r'Error: ([^\n]+)',
                r'! LaTeX Error: ([^\n]+)'
            ]

            for pattern in warning_patterns:
                for match in re.finditer(pattern, log_content):
                    warnings.append(match.group(1))

            for pattern in error_patterns:
                for match in re.finditer(pattern, log_content):
                    errors.append(match.group(1))

            if warnings or errors:
                self.write("\nCompilation Report:\n", "yellow")

                if errors:
                    self.write("\nErrors:\n", "red")
                    for error in errors:
                        self.write(f"• {error}\n", "red")

                if warnings:
                    self.write("\nWarnings:\n", "yellow")
                    for warning in warnings:
                        self.write(f"• {warning}\n", "yellow")

        except Exception as e:
            self.write(f"\nError reading log file: {str(e)}\n", "red")

    def write(self, text: str, color: str = "white") -> None:
        """Write text to terminal with color support"""
        try:
            if hasattr(self, 'terminal'):
                self.terminal.write(text, color)
        except Exception as e:
            print(f"Error writing to terminal: {str(e)}", file=sys.__stdout__)


    def run_pdflatex(self, tex_file: str) -> bool:
        """Run pdflatex with output to terminal"""
        try:
            # Store original directory
            original_dir = os.getcwd()

            # Change to tex file directory
            tex_dir = os.path.dirname(tex_file) or '.'
            os.chdir(tex_dir)

            # Update working directory in terminal
            self.terminal.set_working_directory(tex_dir)

            # Start pdflatex process
            self.current_process = subprocess.Popen(
                ['pdflatex', '-interaction=nonstopmode', tex_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output in real-time
            while True:
                line = self.current_process.stdout.readline()
                if not line and self.current_process.poll() is not None:
                    break

                if line:
                    # Color code the output
                    if any(err in line for err in ['Error:', '!', 'Fatal error']):
                        self.write(line, "red")
                    elif 'Warning' in line:
                        self.write(line, "yellow")
                    else:
                        self.write(line)

                    # Keep UI responsive
                    self.update_idletasks()

            # Get process result
            return_code = self.current_process.wait()
            self.current_process = None

            return return_code == 0

        except Exception as e:
            self.write(f"\nProcess error: {str(e)}\n", "red")
            if self.current_process:
                self.current_process = None
            return False

        finally:
            # Restore original directory
            os.chdir(original_dir)
            self.terminal.set_working_directory(original_dir)



    def handle_pdf_completion(self, pdf_file: str, size_str: str) -> None:
        """Handle successful PDF generation"""
        if messagebox.askyesno("Success",
                              f"PDF generated successfully!\nSize: {size_str}\n\nWould you like to view it now?"):
            self.preview_pdf()

    def handle_compilation_error(self, error: Exception) -> None:
        """Handle compilation errors"""
        error_msg = f"Error generating PDF: {str(error)}\n"
        self.write_to_terminal(f"\n✗ {error_msg}", "red")

        # Add detailed error information to terminal
        if hasattr(error, '__traceback__'):
            self.write_to_terminal("\nDetailed error information:\n", "red")
            self.write_to_terminal(traceback.format_exc(), "red")

        messagebox.showerror("Error", f"Error generating PDF:\n{str(error)}")

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



    def on_slide_select(self, event) -> None:
        """Handle slide selection from list"""
        index = self.slide_list.index("@%d,%d" % (event.x, event.y)).split('.')[0]
        index = int(index)
        if 0 <= index < len(self.slides):
            self.save_current_slide()
            self.current_slide_index = index
            self.load_slide(index)
            self.update_slide_list()



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

    def show_settings_dialog(self) -> None:
        """Show presentation settings dialog with logo handling"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Presentation Settings")
        dialog.geometry("500x450")

        # Make dialog modal but wait until it's visible
        dialog.transient(self)

        # Center the dialog on parent window
        def center_dialog():
            dialog.update_idletasks()  # Make sure dialog is fully created
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            window_width = dialog.winfo_width()
            window_height = dialog.winfo_height()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            dialog.geometry(f"+{x}+{y}")

            # Set grab after dialog is visible
            dialog.after(100, lambda: dialog.grab_set())

        # Container frame for settings
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create entry fields for presentation metadata
        entries = {}
        row = 0
        for key, value in self.presentation_info.items():
            if key != 'logo':  # Handle logo separately
                label = ctk.CTkLabel(main_frame, text=key.title() + ":")
                label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

                entry = ctk.CTkEntry(main_frame, width=300)
                entry.insert(0, value)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                entries[key] = entry
                row += 1

        # Add logo selection
        logo_label = ctk.CTkLabel(main_frame, text="Logo:")
        logo_label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

        logo_frame = ctk.CTkFrame(main_frame)
        logo_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        logo_entry = ctk.CTkEntry(logo_frame, width=240)
        logo_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)

        # Insert existing logo path if present
        if 'logo' in self.presentation_info:
            logo_path = self.presentation_info['logo']
            # Extract path from logo command if present
            if '\\includegraphics' in logo_path:
                match = re.search(r'\\includegraphics\[.*?\]{(.*?)}', logo_path)
                if match:
                    logo_entry.insert(0, match.group(1))
            else:
                logo_entry.insert(0, logo_path)

        def browse_logo():
            """Handle logo file selection"""
            filename = filedialog.askopenfilename(
                title="Select Logo Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.pdf"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ],
                parent=dialog  # Set parent for proper modal behavior
            )
            if filename:
                logo_entry.delete(0, 'end')
                logo_entry.insert(0, filename)

        ctk.CTkButton(logo_frame, text="Browse",
                      command=browse_logo).pack(side="left", padx=5)

        def save_settings():
            """Save settings including logo"""
            try:
                # Save regular metadata
                for key, entry in entries.items():
                    self.presentation_info[key] = entry.get()

                # Save logo if specified
                logo_path = logo_entry.get().strip()
                if logo_path:
                    if os.path.exists(logo_path):
                        # Save logo path with LaTeX formatting
                        self.presentation_info['logo'] = f"\\logo{{\\includegraphics[height=1cm]{{{logo_path}}}}}"
                    else:
                        messagebox.showerror("Error",
                                           f"Logo file not found:\n{logo_path}",
                                           parent=dialog)
                        return
                else:
                    # Remove logo if entry is empty
                    self.presentation_info.pop('logo', None)

                dialog.grab_release()
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Error",
                                   f"Error saving settings:\n{str(e)}",
                                   parent=dialog)

        def on_cancel():
            """Handle dialog cancellation"""
            dialog.grab_release()
            dialog.destroy()

        # Add buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.grid(row=row + 1, column=0, columnspan=2, pady=20)

        # Add Save and Cancel buttons
        ctk.CTkButton(buttons_frame, text="Save Settings",
                      command=save_settings).pack(side="left", padx=10)

        ctk.CTkButton(buttons_frame, text="Cancel",
                      command=on_cancel).pack(side="left", padx=10)

        # Configure grid
        main_frame.columnconfigure(1, weight=1)

        # Handle dialog close button
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        # Center and show dialog
        dialog.after(10, center_dialog)

        # Lift dialog to top
        dialog.lift()


    def edit_preamble(self):
        """Open preamble editor with logo support"""
        # Get current preamble including logo
        current_preamble = self.get_custom_preamble()

        # Open preamble editor
        new_preamble = PreambleEditor.edit_preamble(self, current_preamble)

        if new_preamble is not None:
            # Store the custom preamble
            self.custom_preamble = new_preamble
            messagebox.showinfo("Success", "Preamble updated successfully!")


    def present_with_notes(self) -> None:
        """Present PDF using pympress for dual-screen display with notes"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Get absolute paths
            base_filename = os.path.splitext(self.current_file)[0]
            pdf_file = base_filename + '.pdf'
            abs_pdf_path = os.path.abspath(pdf_file)

            # Check if PDF exists and generate if needed
            if not os.path.exists(abs_pdf_path):
                self.write_to_terminal("PDF not found. Generating...")
                self.generate_pdf()

                if not os.path.exists(abs_pdf_path):
                    messagebox.showerror("Error", "Failed to generate PDF presentation.")
                    return

            # Get virtual environment path
            venv_path = Path.home() / 'my_python'
            if platform.system() == "Windows":
                pympress_path = venv_path / "Scripts" / "pympress.exe"
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                pympress_path = venv_path / "bin" / "pympress"
                python_path = venv_path / "bin" / "python"

            # Setup environment variables
            env = os.environ.copy()

            # Add virtual environment to PATH
            if platform.system() == "Windows":
                env["PATH"] = f"{venv_path / 'Scripts'};{env.get('PATH', '')}"
            else:
                env["PATH"] = f"{venv_path / 'bin'}:{env.get('PATH', '')}"

            # Add virtual environment's site-packages to PYTHONPATH
            site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env.get('PYTHONPATH', '')}"

            # Launch presentation with pympress using absolute path
            self.write_to_terminal("Launching pympress presentation viewer...")
            try:
                if platform.system() == "Windows":
                    if pympress_path.exists():
                        subprocess.Popen([str(pympress_path), abs_pdf_path], env=env)
                    else:
                        # Fall back to using python to run pympress module
                        subprocess.Popen([str(python_path), "-m", "pympress", abs_pdf_path], env=env)
                else:
                    if pympress_path.exists():
                        subprocess.Popen([str(pympress_path), abs_pdf_path], env=env)
                    else:
                        # Try alternative locations while maintaining venv context
                        possible_paths = [
                            venv_path / "bin" / "pympress",
                            Path("/usr/local/bin/pympress"),
                            Path("/usr/bin/pympress"),
                            Path.home() / '.local/bin/pympress'
                        ]
                        for path in possible_paths:
                            if path.exists():
                                subprocess.Popen([str(path), abs_pdf_path], env=env)
                                break
                        else:
                            # If no pympress found, try using python -m pympress
                            subprocess.Popen([str(python_path), "-m", "pympress", abs_pdf_path], env=env)

                self.write_to_terminal("✓ Presentation launched successfully\n", "green")
                self.write_to_terminal("\nPympress Controls:\n")
                self.write_to_terminal("- Right Arrow/Space/Page Down: Next slide\n")
                self.write_to_terminal("- Left Arrow/Page Up: Previous slide\n")
                self.write_to_terminal("- Escape: Exit presentation\n")
                self.write_to_terminal("- F11: Toggle fullscreen\n")
                self.write_to_terminal("- N: Toggle notes\n")
                self.write_to_terminal("- P: Pause/unpause timer\n")

            except Exception as e:
                error_msg = f"Error launching pympress: {str(e)}\n"
                self.write_to_terminal(error_msg, "red")
                self.write_to_terminal("\nTrying to locate pympress...\n")

                # Check pympress in virtual environment
                self.write_to_terminal(f"Checking virtual environment: {venv_path}\n")
                if pympress_path.exists():
                    self.write_to_terminal(f"✓ Found pympress at: {pympress_path}\n", "green")
                else:
                    self.write_to_terminal("✗ pympress not found in virtual environment\n", "red")

        except Exception as e:
            self.write_to_terminal(f"✗ Error launching presentation: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error launching presentation:\n{str(e)}")
            traceback.print_exc()


#----------------------------------------------Interactive Terminal ------------------------------------
import customtkinter as ctk
import tkinter as tk
import threading
import queue
import socket
import os

class InteractiveTerminal(ctk.CTkFrame):
    """Interactive terminal with proper input capture and validation"""
    def __init__(self, master, initial_directory=None, **kwargs):
        super().__init__(master, **kwargs)

        # Initialize variables
        self.working_dir = initial_directory or os.getcwd()
        self.command_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.waiting_for_input = False
        self.input_response = None
        self.input_event = threading.Event()
        self.current_prompt = None

        # Create UI
        self._create_ui()

        # Start command processor
        self.running = True
        self.process_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.process_thread.start()

    def _create_ui(self):
        """Create terminal UI with improved input handling"""
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
        self.display._textbox.tag_configure("prompt", foreground="cyan")
        self.display._textbox.tag_configure("input", foreground="white")

        # Enhanced input handling
        self.display.bind("<Return>", self._handle_input)
        self.display.bind("<Key>", self._handle_key)
        self.display.bind("<BackSpace>", self._handle_backspace)

        # Initial prompt
        self.show_prompt()

    def _get_input_start(self):
        """Get the starting position of current input"""
        if self.waiting_for_input:
            # Find the last prompt position
            last_prompt = self.display._textbox.search(
                self.current_prompt or "$ ",
                "1.0",
                stopindex="end",
                backwards=True
            )
            if last_prompt:
                return f"{last_prompt}+{len(self.current_prompt or '$ ')}c"
        return "insert"

    def _handle_key(self, event):
        """Handle regular key input"""
        if self.waiting_for_input:
            if event.char and ord(event.char) >= 32:  # Printable characters
                self.display._textbox.insert("insert", event.char)
                return "break"
        return None

    def _handle_backspace(self, event):
        """Handle backspace key"""
        if self.waiting_for_input:
            input_start = self._get_input_start()
            if self.display._textbox.compare("insert", ">", input_start):
                self.display._textbox.delete("insert-1c", "insert")
            return "break"
        return None

    def terminal_input(self, prompt: str) -> str:
        """Get input synchronously using keyboard event handler"""
        try:
            self.current_prompt = prompt
            self.waiting_for_input = True
            self.input_done = False  # Flag to track input completion
            self.input_result = None  # Store input result

            # Show prompt
            self.write(prompt, "yellow")

            # Focus the display
            self.display.focus_set()

            # Wait for input with active event handling
            while not self.input_done:
                self.update()  # Process events
                self.master.update()  # Allow window updates

            # Get result and reset state
            result = self.input_result
            self.waiting_for_input = False
            self.current_prompt = None
            self.input_done = False
            self.input_result = None

            return result if result is not None else ""

        except Exception as e:
            self.write(f"\nError getting input: {str(e)}\n", "red")
            return ""

    def _handle_input(self, event):
        """Handle Return key for input completion"""
        try:
            if self.waiting_for_input:
                # Get current line
                current_line = self.display._textbox.get("insert linestart", "insert lineend")

                # Extract input after prompt
                if self.current_prompt:
                    input_text = current_line[len(self.current_prompt):].strip()
                else:
                    input_text = current_line.strip()

                # Store result and signal completion
                self.input_result = input_text
                self.input_done = True

                # Add newline for visual feedback
                self.write("\n")
                return "break"

            # Handle regular command input
            current_line = self.display._textbox.get("insert linestart", "insert lineend")
            if current_line.startswith("$ "):
                command = current_line[2:]
                if command.strip():
                    self.command_queue.put(command)
                self.write("\n")
                self.show_prompt()
                return "break"

        except Exception as e:
            self.write(f"\nInput error: {str(e)}\n", "red")

        return "break"

    def write(self, text, color="white"):
        """Write text to terminal with proper scroll"""
        try:
            # Insert text with color tag
            self.display._textbox.insert("end", text, color)
            self.display.see("end")
            self.update_idletasks()

            # Move cursor to end
            self.display._textbox.mark_set("insert", "end")

        except Exception as e:
            print(f"Write error: {e}", file=sys.__stdout__)

    def clear(self):
        """Clear terminal content"""
        self.display._textbox.delete("1.0", "end")
        self.show_prompt()

    def _process_commands(self):
        """Process commands in background"""
        while self.running:
            try:
                command = self.command_queue.get(timeout=0.1)
                if command.startswith("cd "):
                    path = command[3:].strip()
                    self._change_directory(path)
                else:
                    try:
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=self.working_dir,
                            text=True
                        )
                        out, err = process.communicate()
                        if out:
                            self.after(0, lambda: self.write(out))
                        if err:
                            self.after(0, lambda: self.write(err, "red"))
                    except Exception as e:
                        self.after(0, lambda: self.write(f"\nError: {str(e)}\n", "red"))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command processing error: {e}", file=sys.__stdout__)

    def show_prompt(self):
        """Show command prompt if not waiting for input"""
        if not self.waiting_for_input:
            self.write("\n$ ", "prompt")

    def set_working_directory(self, directory):
        """Set working directory"""
        if os.path.exists(directory):
            self.working_dir = directory
            os.chdir(directory)
            self.dir_label.configure(text=f"📁 {self.working_dir}")
    def _change_directory(self, path):
        """Change working directory"""
        try:
            os.chdir(path)
            self.working_dir = os.getcwd()
            self.dir_label.configure(text=f"📁 {self.working_dir}")
            self.write(f"Changed directory to: {self.working_dir}\n", "green")
        except Exception as e:
            self.write(f"Error changing directory: {str(e)}\n", "red")

#------------------------------------------End Interactive Terminal -----------------------------------------

#-------------------------------------------Session Manager ------------------------------------------
#import json
#import os
#from pathlib import Path

class SessionManager:
    """Manages persistence of session data between IDE launches"""

    def __init__(self):
        try:
            # Get user's home directory
            self.home_dir = Path.home()
            # Create .bsg-ide directory in user's home if it doesn't exist
            self.config_dir = self.home_dir / '.bsg-ide'
            self.config_dir.mkdir(exist_ok=True)
            self.session_file = self.config_dir / 'session.json'

            # Try to find Documents folder
            documents_dir = None
            possible_docs = [
                self.home_dir / 'Documents',  # Linux/macOS
                self.home_dir / 'documents',  # Alternative spelling
                Path(os.path.expandvars('%USERPROFILE%\\Documents'))  # Windows
            ]

            for doc_path in possible_docs:
                if doc_path.exists() and doc_path.is_dir():
                    documents_dir = doc_path
                    break

            # Fall back to home directory if Documents not found
            default_dir = str(documents_dir) if documents_dir else str(self.home_dir)

            self.default_session = {
                'last_file': None,
                'working_directory': default_dir,
                'recent_files': [],
                'window_size': {'width': 1200, 'height': 800},
                'window_position': {'x': None, 'y': None}
            }
        except Exception as e:
            print(f"Warning: Could not initialize session manager: {str(e)}")
            # Still allow the program to run with defaults
            self.session_file = None
            self.default_session = {
                'last_file': None,
                'working_directory': str(Path.home()),
                'recent_files': [],
                'window_size': {'width': 1200, 'height': 800},
                'window_position': {'x': None, 'y': None}
            }

    def load_session(self):
        """Load session data from file with Documents folder preference"""
        try:
            if self.session_file and self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    data = json.load(f)

                # Validate loaded data
                session_data = self.default_session.copy()

                # Only update working directory if it exists and there's a last file or recent files
                if data.get('last_file') or data.get('recent_files'):
                    if os.path.exists(data.get('working_directory', '')):
                        session_data.update({k: v for k, v in data.items() if k in self.default_session})

                # Filter out non-existent recent files
                session_data['recent_files'] = [
                    f for f in session_data['recent_files']
                    if os.path.exists(f)
                ]

                return session_data

            return self.default_session.copy()

        except Exception as e:
            print(f"Warning: Could not load session data: {str(e)}")
            return self.default_session.copy()

    def save_session(self, data):
        """Save session data to file"""
        if not self.session_file:
            return  # Skip saving if no session file available

        try:
            # Ensure all paths are strings
            session_data = {
                'last_file': str(data.get('last_file')) if data.get('last_file') else None,
                'working_directory': str(data.get('working_directory', self.default_session['working_directory'])),
                'recent_files': [str(f) for f in data.get('recent_files', [])[-10:]],  # Keep last 10 files
                'window_size': data.get('window_size', self.default_session['window_size']),
                'window_position': data.get('window_position', self.default_session['window_position'])
            }

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save session data: {str(e)}")




#---------------------------------------------------------------------------------


def verify_pymupdf_installation():
    """
    Verify PyMuPDF is installed correctly and usable.
    """
    try:
        import fitz
        # Try to access version info
        version = fitz.version[0]
        print(f"PyMuPDF version: {version}")

        # Try to create a simple test document
        test_doc = fitz.open()  # Creates an empty PDF
        test_doc.new_page()     # Adds a page
        test_doc.close()        # Closes the document

        print("✓ PyMuPDF verification successful")
        return True
    except Exception as e:
        print(f"PyMuPDF verification failed: {str(e)}")
        return False

def get_pymupdf_info():
    """
    Get detailed information about PyMuPDF installation.
    """
    try:
        import fitz
        return {
            'version': fitz.version[0],
            'binding_version': fitz.version[1],
            'build_date': fitz.version[2],
            'lib_path': fitz.__file__
        }
    except Exception as e:
        return f"Error getting PyMuPDF info: {str(e)}"

def import_required_packages():
    """
    Import all required packages with proper error handling and verification.
    """
    try:
        # First verify PyMuPDF
        if not verify_pymupdf_installation():
            raise ImportError("PyMuPDF installation verification failed")

        # Now import everything else
        import tkinter as tk
        from PIL import Image, ImageDraw, ImageTk
        import customtkinter as ctk
        from tkinter import ttk, filedialog, messagebox, simpledialog
        import screeninfo
        import requests
        import cv2
        import yt_dlp
        import fitz

        modules = {
            'tk': tk,
            'Image': Image,
            'ImageDraw': ImageDraw,
            'ImageTk': ImageTk,
            'ctk': ctk,
            'ttk': ttk,
            'fitz': fitz,
            'screeninfo': screeninfo,
            'requests': requests,
            'cv2': cv2,
            'yt_dlp': yt_dlp
        }

        # Print success message with version info
        print(f"\nSuccessfully imported all packages:")
        print(f"PyMuPDF version: {fitz.version[0]}")
        print(f"PIL version: {Image.__version__}")
        print(f"OpenCV version: {cv2.__version__}")

        return modules

    except Exception as e:
        print(f"Error importing required packages: {str(e)}")
        traceback.print_exc()
        sys.exit(1)



class MediaURLDialog(ctk.CTkToplevel):
    def __init__(self, parent, slide_index, media_entry):
        super().__init__(parent)
        self.title("Update Media Location")
        self.geometry("500x150")
        self.media_entry = media_entry

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create widgets
        ctk.CTkLabel(self, text=f"Enter media URL for slide {slide_index + 1}:").pack(pady=10)

        self.url_entry = ctk.CTkEntry(self, width=400)
        self.url_entry.pack(pady=10)
        self.url_entry.insert(0, media_entry.get())

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Play URL",
                     command=self.use_play_url).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Static URL",
                     command=self.use_static_url).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel",
                     command=self.cancel).pack(side="left", padx=5)

    def use_play_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, f"\\play \\url {url}")
        self.destroy()

    def use_static_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, f"\\url {url}")
        self.destroy()

    def cancel(self):
        self.destroy()

def update_installation():
    """Silently update installed files if running from a newer version"""
    try:
        system, paths = get_installation_paths()
        current_path = Path(__file__).resolve()

        # Determine installation directory
        install_dir = paths['share'] / 'bsg-ide' if system != "Windows" else paths['bin']

        # If running from an installation directory, no need to update
        if str(current_path).startswith(str(install_dir)):
            return True

        # Get installed version info
        installed_version = "0.0.0"
        version_file = install_dir / "version.txt"
        if version_file.exists():
            installed_version = version_file.read_text().strip()

        # Compare with current version
        current_version = getattr(BeamerSlideEditor, '__version__', "1.0.0")

        # Always update files if versions don't match
        if installed_version != current_version:
            print(f"Updating BSG-IDE from version {installed_version} to {current_version}")

            # Create directories if they don't exist
            os.makedirs(install_dir, exist_ok=True)
            os.makedirs(paths['bin'], exist_ok=True)

            # Copy current files to installation directory
            current_dir = current_path.parent
            required_files = [
                'BSG_IDE.py',
                'BeamerSlideGenerator.py',
                'requirements.txt'
            ]

            for file in required_files:
                src = current_dir / file
                if src.exists():
                    shutil.copy2(src, install_dir)
                    print(f"Updated {file}")

            # Update version file
            version_file.write_text(current_version)

            # Update launcher script
            launcher_script = create_bsg_launcher(install_dir, paths)

            if system == "Linux":
                launcher_path = paths['bin'] / 'bsg-ide'
                launcher_path.write_text(launcher_script)
                launcher_path.chmod(0o755)

            elif system == "Windows":
                batch_content = f"""@echo off
set PYTHONPATH={install_dir};%PYTHONPATH%
pythonw "{install_dir}\\BSG_IDE.py" %*
"""
                batch_path = paths['bin'] / 'bsg-ide.bat'
                batch_path.write_text(batch_content)

            # Update desktop entry if needed
            if system == "Linux":
                desktop_entry = f"""[Desktop Entry]
Version={current_version}
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec={paths['bin']}/bsg-ide
Icon=bsg-ide
Terminal=false
Categories=Office;Development;Education;
Keywords=presentation;latex;beamer;slides;
StartupWMClass=bsg-ide
"""
                desktop_path = paths['apps'] / 'bsg-ide.desktop'
                desktop_path.write_text(desktop_entry)
                desktop_path.chmod(0o755)

            # Ensure Python paths are correct
            setup_python_paths()

            print("Update completed successfully")

        return True

    except Exception as e:
        print(f"Warning: Update check failed: {str(e)}")
        traceback.print_exc()
        return False
#--------------------------------------------------Dialogs -------------------------
class InstitutionNameDialog(ctk.CTkToplevel):
    """Dialog for handling long institution names"""
    def __init__(self, parent, institution_name):
        super().__init__(parent)
        self.title("Institution Name Warning")
        self.geometry("500x250")
        self.short_name = None

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create widgets
        ctk.CTkLabel(self, text="Long Institution Name Detected",
                    font=("Arial", 14, "bold")).pack(pady=10)

        ctk.CTkLabel(self, text=f"Current name:\n{institution_name}",
                    wraplength=450).pack(pady=10)

        ctk.CTkLabel(self, text="Please provide a shorter version for slide footers:").pack(pady=5)

        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Use Short Name",
                     command=self.use_short_name).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Keep Original",
                     command=self.keep_original).pack(side="left", padx=10)

    def use_short_name(self):
        self.short_name = self.entry.get()
        self.destroy()

    def keep_original(self):
        self.destroy()

class MediaSelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting media when URL fails"""
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title("Media Selection")
        self.geometry("600x400")
        self.result = None

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create widgets
        ctk.CTkLabel(self, text="Media Selection Required",
                    font=("Arial", 14, "bold")).pack(pady=10)

        # Show search query
        search_query = construct_search_query(title, content)
        query_frame = ctk.CTkFrame(self)
        query_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(query_frame, text=f"Search query: {search_query}",
                    wraplength=550).pack(side="left", pady=5)

        ctk.CTkButton(query_frame, text="Open Search",
                     command=lambda: open_google_image_search(search_query)).pack(side="right", padx=5)

        # Options
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # URL Entry
        url_frame = ctk.CTkFrame(options_frame)
        url_frame.pack(fill="x", pady=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=400)
        self.url_entry.pack(side="left", padx=5)
        ctk.CTkButton(url_frame, text="Use URL",
                     command=self.use_url).pack(side="left", padx=5)

        # File Selection
        file_frame = ctk.CTkFrame(options_frame)
        file_frame.pack(fill="x", pady=5)
        self.file_listbox = ctk.CTkTextbox(file_frame, height=150)
        self.file_listbox.pack(fill="x", pady=5)

        # Populate file list
        try:
            files = os.listdir('media_files')
            for i, file in enumerate(files, 1):
                self.file_listbox.insert('end', f"{i}. {file}\n")
        except Exception as e:
            self.file_listbox.insert('end', f"Error accessing media_files: {str(e)}")

        ctk.CTkButton(file_frame, text="Use Selected File",
                     command=self.use_file).pack(pady=5)

        # No Media Option
        ctk.CTkButton(options_frame, text="Create Slide Without Media",
                     command=self.use_none).pack(pady=10)

    def use_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.result = url
            self.destroy()

    def use_file(self):
        # Get selected line
        try:
            selection = self.file_listbox.get("sel.first", "sel.last")
            if selection:
                file_name = selection.split('.', 1)[1].strip()
                self.result = f"\\file media_files/{file_name}"
                self.destroy()
        except:
            messagebox.showwarning("Selection Required",
                                 "Please select a file from the list")

    def use_none(self):
        self.result = "\\None"
        self.destroy()


# Function to replace console prompts with GUI dialogs
def handle_long_institution(parent, institution_name):
    """Handle long institution name with GUI dialog"""
    dialog = InstitutionNameDialog(parent, institution_name)
    parent.wait_window(dialog)
    return dialog.short_name

def handle_media_selection(parent, title, content):
    """Handle media selection with GUI dialog"""
    dialog = MediaSelectionDialog(parent, title, content)
    parent.wait_window(dialog)
    return dialog.result
#----------------------------------------------------------Install in local bin -----------------------------------

def setup_python_paths():
    """Setup Python paths for imports"""
    import sys
    import site
    from pathlib import Path

    # Get user's home directory
    home = Path.home()

    # Add common installation paths
    paths = [
        home / '.local' / 'lib' / 'bsg-ide',  # Linux/macOS user installation
        home / '.local' / 'bin',              # Linux/macOS binaries
        home / 'Library' / 'Application Support' / 'BSG-IDE',  # macOS
        Path(site.getusersitepackages()) / 'bsg-ide',  # Windows user site-packages
    ]

    # Add installation directory to PYTHONPATH
    for path in paths:
        str_path = str(path)
        if path.exists() and str_path not in sys.path:
            sys.path.insert(0, str_path)

def create_bsg_launcher(install_dir: Path, paths: dict) -> str:
    """Create launcher script with updated terminal handling"""
    launcher_script = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

# Add all possible installation paths
INSTALL_PATHS = [
    '{install_dir}',
    '{paths["bin"]}',
    str(Path.home() / '.local' / 'lib' / 'bsg-ide'),
    str(Path.home() / '.local' / 'bin'),
    str(Path.home() / 'Library' / 'Application Support' / 'BSG-IDE'),
]

# Add paths to Python path
for path in INSTALL_PATHS:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Import the terminal module
from BSG_terminal import InteractiveTerminal, SimpleRedirector

# Import and run main program
try:
    #from BSG_IDE import BeamerSlideEditor

    # Create application instance
    app = BeamerSlideEditor()

    # Redirect stdout and stderr to app's terminal after it's created
    if hasattr(app, 'terminal'):
        sys.stdout = SimpleRedirector(app.terminal)
        sys.stderr = SimpleRedirector(app.terminal, "red")

    # Start the application
    app.mainloop()

except Exception as e:
    import traceback
    print(f"Error starting BSG-IDE: {str(e)}")
    traceback.print_exc()
    if sys.platform != "win32":
        input("Press Enter to exit...")
"""
    return launcher_script


def setup_desktop_entry():
    """Create desktop entry and set up icons"""
    try:
        # Get user's home directory
        home_dir = Path.home()

        # Create necessary directories
        apps_dir = home_dir / '.local' / 'share' / 'applications'
        apps_dir.mkdir(parents=True, exist_ok=True)

        icon_base = home_dir / '.local' / 'share' / 'icons' / 'hicolor'

        # Copy icon to appropriate locations for different resolutions
        icon_sizes = ['16x16', '32x32', '48x48', '64x64', '128x128', '256x256']

        # First, ensure we have the source icon
        source_icon = (Path(__file__).parent / 'icons' / 'bsg-ide.png')
        if not source_icon.exists():
            source_icon = Path(__file__).parent / 'bsg-ide.png'

        if not source_icon.exists():
            print("Warning: Could not find source icon file")
            return False

        for size in icon_sizes:
            icon_dir = icon_base / size / 'apps'
            icon_dir.mkdir(parents=True, exist_ok=True)
            icon_path = icon_dir / 'bsg-ide.png'

            try:
                shutil.copy2(source_icon, icon_path)
                print(f"✓ Copied icon for size {size}")
            except Exception as e:
                print(f"Warning: Could not copy icon for size {size}: {e}")

        # Create desktop entry
        desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec=bsg-ide
Icon=bsg-ide
Terminal=false
Categories=Office;Development;Education;
Keywords=presentation;latex;beamer;slides;
StartupWMClass=bsg-ide
"""

        # Write desktop entry file
        desktop_path = apps_dir / 'bsg-ide.desktop'
        desktop_path.write_text(desktop_entry)
        desktop_path.chmod(0o755)

        # Update icon cache
        try:
            subprocess.run(['gtk-update-icon-cache', '--force', '--quiet', str(icon_base)])
            print("✓ Icon cache updated")
        except Exception as e:
            print(f"Warning: Could not update icon cache: {e}")

        print("✓ Desktop entry created successfully")
        return True

    except Exception as e:
        print(f"Error creating desktop entry: {str(e)}")
        return False

def verify_desktop_entry():
    """Verify desktop entry and icon installation"""
    try:
        home_dir = Path.home()
        desktop_entry = home_dir / '.local' / 'share' / 'applications' / 'bsg-ide.desktop'
        icon_path = home_dir / '.local' / 'share' / 'icons' / 'hicolor' / '128x128' / 'apps' / 'bsg-ide.png'

        if not desktop_entry.exists() or not icon_path.exists():
            print("Desktop entry or icon missing. Setting up...")
            return setup_desktop_entry()

        return True

    except Exception as e:
        print(f"Error verifying desktop entry: {str(e)}")
        return False



#-------------------------------------------------pympress installation -----------------------------
def setup_pympress():
    """Verify pympress installation and setup with all required dependencies"""
    try:
        # Check if pympress works by importing required modules
        def check_pympress_deps():
            try:
                import gi
                import cairo
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                import pympress
                return True
            except ImportError:
                return False

        if check_pympress_deps():
            print("✓ Pympress and dependencies already installed")
            return True

        print("Installing pympress and dependencies...")

        # Install system dependencies first
        if sys.platform.startswith('linux'):
            dependencies = [
                'python3-gi',
                'python3-gi-cairo',
                'gir1.2-gtk-3.0',
                'python3-cairo',
                'libgtk-3-0',
                'librsvg2-common',
                'poppler-utils',
                'libgirepository1.0-dev',  # Required for PyGObject
                'gcc',                     # Required for compilation
                'python3-dev',             # Python development files
                'pkg-config',              # Required for build process
                'cairo-dev',               # Cairo development files
                'libcairo2-dev',          # Cairo development files
                'gobject-introspection'    # GObject introspection
            ]

            # Detect package manager and set appropriate commands
            if shutil.which('apt'):
                install_cmd = ['sudo', 'apt', 'install', '-y']
                deps = dependencies + ['libgirepository1.0-dev', 'python3-gi-dev']
            elif shutil.which('dnf'):
                install_cmd = ['sudo', 'dnf', 'install', '-y']
                deps = dependencies + ['gobject-introspection-devel', 'python3-gobject-devel']
            elif shutil.which('pacman'):
                install_cmd = ['sudo', 'pacman', '-S', '--noconfirm']
                deps = dependencies + ['gobject-introspection', 'python-gobject']
            else:
                print("Could not detect package manager. Please install dependencies manually.")
                print("Required packages:", " ".join(dependencies))
                return False

            # Install system dependencies
            print("\nInstalling system dependencies...")
            for dep in deps:
                try:
                    subprocess.check_call(install_cmd + [dep])
                    print(f"✓ Installed {dep}")
                except subprocess.CalledProcessError:
                    print(f"✗ Failed to install {dep}")
                    continue

        # Install Python packages
        print("\nInstalling Python packages...")
        packages = [
            'pycairo',
            'PyGObject',
            'pympress'
        ]

        for package in packages:
            try:
                # Try installing in user space first
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "--user", "--no-cache-dir", package
                ])
                print(f"✓ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                continue

        # Verify installation
        if check_pympress_deps():
            print("\n✓ Pympress and all dependencies installed successfully")
            return True
        else:
            print("\n✗ Installation completed but verification failed")
            print("Please try installing manually:")
            print("sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
            print("pip install --user pycairo PyGObject pympress")
            return False

    except Exception as e:
        print(f"✗ Error setting up pympress: {str(e)}")
        traceback.print_exc()
        return False

def launch_pympress(pdf_path):
    """Launch pympress with proper environment setup"""
    try:
        # Ensure absolute path
        abs_pdf_path = os.path.abspath(pdf_path)

        # Set up environment variables
        env = os.environ.copy()

        # Add GI typelib path if needed
        typelib_paths = [
            '/usr/lib/girepository-1.0',
            '/usr/local/lib/girepository-1.0',
            '/usr/lib/x86_64-linux-gnu/girepository-1.0'
        ]

        existing_typelib = env.get('GI_TYPELIB_PATH', '').split(':')
        new_typelib = ':'.join(filter(os.path.exists, typelib_paths + existing_typelib))
        env['GI_TYPELIB_PATH'] = new_typelib

        # Try to launch pympress
        if sys.platform.startswith('win'):
            subprocess.Popen(['pympress', abs_pdf_path], shell=True, env=env)
        else:
            # Try different possible pympress locations
            pympress_paths = [
                shutil.which('pympress'),
                '/usr/local/bin/pympress',
                '/usr/bin/pympress',
                os.path.expanduser('~/.local/bin/pympress')
            ]

            for path in filter(None, pympress_paths):
                if os.path.exists(path):
                    subprocess.Popen([path, abs_pdf_path], env=env)
                    return True

            raise FileNotFoundError("pympress executable not found")

    except Exception as e:
        print(f"Error launching pympress: {str(e)}")
        traceback.print_exc()
        return False
#-------------------------------------------------------------------------
def create_icon(install_dir: Path) -> bool:
    """Create icon with airis4D logo and BSG-IDE text below"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os

        # Create icons directory
        icons_dir = install_dir / 'icons'
        os.makedirs(icons_dir, exist_ok=True)

        # Icon sizes needed for different platforms
        sizes = [16, 32, 48, 64, 128, 256]

        # Create base icon image (make it square)
        size = 256  # Base size
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw airis4D logo - maintaining exact proportions from ASCII art
        logo_height = size * 0.6  # Logo takes up 60% of height
        margin = size * 0.2  # 20% margin from top

        # Calculate logo dimensions
        logo_width = logo_height * 0.8  # Maintain aspect ratio

        # Logo starting position
        start_x = (size - logo_width) / 2
        start_y = margin

        # Draw the triangle (airis4D logo)
        triangle_points = [
            (start_x, start_y + logo_height),  # Bottom left
            (start_x + logo_width/2, start_y), # Top
            (start_x + logo_width, start_y + logo_height)  # Bottom right
        ]

        # Draw outer triangle
        draw.polygon(triangle_points, fill=(255, 0, 0, 255))  # Red for outer triangle

        # Calculate inner triangle points (80% size of outer)
        inner_scale = 0.8
        inner_offset_x = (logo_width * (1 - inner_scale)) / 2
        inner_offset_y = (logo_height * (1 - inner_scale))
        inner_points = [
            (start_x + inner_offset_x, start_y + logo_height - inner_offset_y),
            (start_x + logo_width/2, start_y + inner_offset_y),
            (start_x + logo_width - inner_offset_x, start_y + logo_height - inner_offset_y)
        ]
        draw.polygon(inner_points, fill=(0, 0, 0, 255))  # Black for inner triangle

        # Add "BSG-IDE" text below logo
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.15))
        except:
            font = ImageFont.load_default()

        text = "BSG-IDE"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (size - text_width) // 2
        text_y = start_y + logo_height + (size * 0.05)  # Small gap between logo and text
        draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0, 255))

        # Save in different sizes
        for icon_size in sizes:
            resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            icon_path = icons_dir / f'bsg-ide_{icon_size}x{icon_size}.png'
            resized.save(icon_path, 'PNG')

            # For Linux, also save in appropriate hicolor directory
            if sys.platform.startswith('linux'):
                hicolor_path = Path.home() / '.local' / 'share' / 'icons' / 'hicolor' / f'{icon_size}x{icon_size}' / 'apps'
                os.makedirs(hicolor_path, exist_ok=True)
                resized.save(hicolor_path / 'bsg-ide.png', 'PNG')

        # Create .ico file for Windows
        if sys.platform.startswith('win'):
            icon_sizes = [(16,16), (32,32), (48,48), (256,256)]
            images = []
            for size in icon_sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                images.append(resized)
            ico_path = icons_dir / 'bsg-ide.ico'
            img.save(ico_path, format='ICO', sizes=icon_sizes)

        return True

    except Exception as e:
        print(f"Error creating icon: {str(e)}")
        traceback.print_exc()
        return False
#--------------------------------------------------------------------------
def setup_static_directory():
    """
    Create required static directory structure for PyMuPDF
    """
    print("Setting up static directory structure...")

    # Create required directories
    directories = [
        'static',
        'static/css',
        'static/js',
        'static/images'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

    # Create minimal required files
    minimal_files = {
        'static/css/style.css': '/* Minimal CSS */',
        'static/js/script.js': '// Minimal JS',
        'static/.keep': ''  # Empty file to ensure directory is tracked
    }

    for filepath, content in minimal_files.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created file: {filepath}")



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
class FileThumbnailBrowser(ctk.CTkToplevel):
    def __init__(self, parent, initial_dir="media_files", callback=None):
        super().__init__(parent)

        # Import required modules
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.Image = Image
            self.ImageDraw = ImageDraw
            self.ImageFont = ImageFont
            self.has_pil = True
        except ImportError as e:
            print(f"Error importing PIL modules: {e}")
            self.has_pil = False
            messagebox.showwarning("Warning",
                                 "Image processing libraries not available.\nThumbnails will be limited.")

        self.title("Media Browser")
        self.geometry("800x600")

        # Store initial directory and callback
        self.current_dir = os.path.abspath(initial_dir)
        self.callback = callback
        self.thumbnails = []
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4

        # Create media_files directory if it doesn't exist
        os.makedirs(initial_dir, exist_ok=True)

        # File categories with extended video types
        self.file_categories = {
            'image': ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'),
            'video': ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.gif'),
            'audio': ('.mp3', '.wav', '.ogg', '.m4a', '.flac'),
            'document': ('.pdf', '.doc', '.docx', '.txt', '.tex'),
            'data': ('.csv', '.xlsx', '.json', '.xml')
        }

        # Create UI components
        self.create_navigation_bar()
        self.create_toolbar()
        self.create_content_area()
        self.load_files()

    def create_thumbnail(self, file_path):
        """Create thumbnail with proper error handling"""
        if not self.has_pil:
            return self.create_fallback_thumbnail()

        try:
            category = self.get_file_category(file_path)
            thumb_size = (150, 150)

            if category == 'image':
                try:
                    with self.Image.open(file_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')

                        # Create thumbnail
                        img.thumbnail(thumb_size, self.Image.Resampling.LANCZOS)

                        # Create background
                        thumb_bg = self.Image.new('RGB', thumb_size, 'black')

                        # Center image on background
                        offset = ((thumb_size[0] - img.size[0]) // 2,
                                (thumb_size[1] - img.size[1]) // 2)
                        thumb_bg.paste(img, offset)

                        return ctk.CTkImage(light_image=thumb_bg,
                                          dark_image=thumb_bg,
                                          size=thumb_size)
                except Exception as e:
                    print(f"Error creating image thumbnail: {str(e)}")
                    return self.create_generic_thumbnail("Image\nError", "#8B0000")

            else:
                # Create appropriate generic thumbnail based on category
                colors = {
                    'video': "#4a90e2",
                    'audio': "#e24a90",
                    'document': "#90e24a",
                    'data': "#4ae290"
                }
                color = colors.get(category, "#808080")
                text = category.upper() if category else "FILE"
                return self.create_generic_thumbnail(text, color)

        except Exception as e:
            print(f"Error creating thumbnail for {file_path}: {str(e)}")
            return self.create_fallback_thumbnail()

    def create_generic_thumbnail(self, text, color):
        """Create generic thumbnail with text"""
        if not self.has_pil:
            return self.create_fallback_thumbnail()

        try:
            thumb_size = (150, 150)
            img = self.Image.new('RGB', thumb_size, 'black')
            draw = self.ImageDraw.Draw(img)

            # Draw colored rectangle
            margin = 20
            draw.rectangle(
                [margin, margin, thumb_size[0]-margin, thumb_size[1]-margin],
                fill=color
            )

            # Draw text
            text_bbox = draw.textbbox((0, 0), text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            text_x = (thumb_size[0] - text_width) // 2
            text_y = (thumb_size[1] - text_height) // 2

            draw.text((text_x, text_y), text, fill="white")

            return ctk.CTkImage(light_image=img,
                              dark_image=img,
                              size=thumb_size)
        except Exception as e:
            print(f"Error creating generic thumbnail: {str(e)}")
            return self.create_fallback_thumbnail()

    def create_fallback_thumbnail(self):
        """Create a basic fallback thumbnail when PIL is not available or errors occur"""
        try:
            img = self.Image.new('RGB', (150, 150), color='gray')
            return ctk.CTkImage(light_image=img,
                              dark_image=img,
                              size=(150, 150))
        except:
            # Create an empty CTkImage if all else fails
            return ctk.CTkImage(light_image=None,
                              dark_image=None,
                              size=(150, 150))

#-------------------------------------------------------------------------------------------


    def create_file_item(self, file_name):
        """Create file display item with proper error handling"""
        try:
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.grid(row=self.current_row, column=self.current_col,
                      padx=10, pady=10, sticky="nsew")

            file_path = os.path.join(self.current_dir, file_name)

            # Create thumbnail
            try:
                thumbnail = self.create_thumbnail(file_path)
            except Exception as e:
                print(f"Error creating thumbnail: {e}")
                thumbnail = self.create_generic_thumbnail("Error", "#8B0000")

            if thumbnail:
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

                # Store reference to thumbnail
                self.thumbnails.append(thumbnail)

            # Update grid position
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1

        except Exception as e:
            print(f"Error creating file item: {str(e)}")

    def on_file_click(self, file_path: str) -> None:
        """Handle file selection with proper path handling"""
        if self.callback:
            # Create relative path if file is in media_files directory
            try:
                relative_to_media = os.path.relpath(file_path, 'media_files')
                if relative_to_media.startswith('..'):
                    # File is outside media_files - use absolute path
                    final_path = file_path
                else:
                    # File is inside media_files - use relative path
                    final_path = os.path.join('media_files', relative_to_media)

                # Determine if file should be played
                ext = os.path.splitext(file_path)[1].lower()
                is_video = ext in self.file_categories['video']

                if is_video and hasattr(self, 'play_vars') and self.play_vars.get(file_path, tk.BooleanVar(value=True)).get():
                    self.callback(f"\\play \\file {final_path}")
                else:
                    self.callback(f"\\file {final_path}")

            except Exception as e:
                print(f"Error handling file selection: {str(e)}")
                return

        self.destroy()

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


class TerminalIO:
    """Improved terminal I/O handler for BSG-IDE integration"""
    def __init__(self, editor):
        self.editor = editor

    def write(self, text, color="white"):
        """Write to terminal with color"""
        if hasattr(self.editor, 'terminal'):
            self.editor.terminal.write(text, color)

    def terminal_input(self, prompt):
        """Get input from terminal with proper synchronization"""
        if hasattr(self.editor, 'terminal'):
            # Use the terminal's input method directly
            text = self.editor.terminal.terminal_input(prompt)
            # Write back the input for visual feedback
            self.editor.terminal.write(text + "\n", "green")
            return text
        else:
            # Fallback to standard input
            text = input(prompt)
            return text



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
                    print("Please ensure BeamerSlideGenerator.py is in the same directory as BSG_IDE.py")
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


#-------------------------------------INSTALLATION----------------------------
import os
import sys
import platform
import shutil
import subprocess
import json
from pathlib import Path
import site
import socket
import ctypes
from importlib import util

class InstallationDialog(ctk.CTkToplevel):
    """Installation progress dialog with visual feedback"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("BSG-IDE Installation")
        self.geometry("400x300")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.center_window()

        # Progress elements
        self.status_label = ctk.CTkLabel(self, text="Preparing installation...")
        self.status_label.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)

        self.detail_text = ctk.CTkTextbox(self, height=150)
        self.detail_text.pack(pady=10, padx=20, fill="both", expand=True)

    def center_window(self):
        """Center dialog on parent window"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def update_progress(self, value: float, message: str):
        """Update progress bar and status message"""
        self.progress.set(value)
        self.status_label.configure(text=message)
        self.detail_text.insert('end', f"{message}\n")
        self.detail_text.see('end')
        self.update()

    def write(self, message: str, color: str = None):
        """Write message to detail text with optional color"""
        if color:
            tag = f"color_{color}"
            self.detail_text.tag_configure(tag, foreground=color)
            self.detail_text.insert('end', message + "\n", tag)
        else:
            self.detail_text.insert('end', message + "\n")
        self.detail_text.see('end')
        self.update()

class InstallationManager:
    """Enhanced installation manager with GUI feedback"""
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.system = platform.system()
        # Set is_admin attribute first
        self.is_admin = False  # Default value
        try:
            if self.system == "Windows":
                import ctypes
                self.is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
            else:
                self.is_admin = os.geteuid() == 0
        except Exception as e:
            print(f"Warning: Could not determine admin status: {e}")
            self.is_admin = False

        # Now get installation paths after is_admin is set
        self.install_paths = self._get_install_paths()

    def install(self):
        """Start installation process with GUI feedback"""
        try:
            self.dialog = InstallationDialog(self.parent)

            # Verify Python environment
            self.dialog.update_progress(0.1, "Checking Python environment...")
            self._verify_python_env()

            # Create installation directories
            self.dialog.update_progress(0.2, "Creating directories...")
            self._create_directories()

            # Copy files
            self.dialog.update_progress(0.4, "Copying required files...")
            self._copy_files()

            # Create launcher
            if not self.create_launcher():
                return False

            # Setup OS integration
            self.dialog.update_progress(0.6, "Setting up system integration...")
            self._setup_os_integration()

            # Install dependencies
            self.dialog.update_progress(0.8, "Installing dependencies...")
            self._install_dependencies()

            # Final checks
            self.dialog.update_progress(0.9, "Performing final checks...")
            self._verify_installation()

            # Complete
            self.dialog.update_progress(1.0, "Installation completed successfully!")
            self.dialog.write("✓ BSG-IDE installation completed!", "green")

            # Close dialog after delay
            self.dialog.after(2000, self.dialog.destroy)
            return True


        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Installation failed: {str(e)}", "red")
                self.dialog.write("\nDetails:", "red")
                self.dialog.write(traceback.format_exc(), "red")
                # Keep dialog open for error review
            return False

    def create_launcher(self):
        """Create platform-specific launcher scripts and shortcuts"""
        try:
            if self.system == "Linux":
                return self._create_linux_launcher()
            elif self.system == "Windows":
                return self._create_windows_launcher()
            else:  # macOS
                return self._create_macos_launcher()
        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating launcher: {str(e)}")
            return False

    def _create_linux_launcher(self):
        """Create Linux launcher script and desktop entry"""
        try:
            # Create launcher script
            launcher_path = self.install_paths['bin'] / 'bsg-ide'
            launcher_content = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add installation directory to Python path
sys.path.insert(0, "{self.install_paths['base']}")

# Import and run main program
try:
    from BSG_IDE import main
    main()
except Exception as e:
    print(f"Error starting BSG-IDE: {{str(e)}}")
    import traceback
    traceback.print_exc()
"""
            # Write launcher script
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)  # Make executable

            if self.dialog:
                self.dialog.write(f"✓ Created launcher script: {launcher_path}", "green")
            else:
                print(f"✓ Created launcher script: {launcher_path}")

            # Create desktop entry
            desktop_entry_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec={launcher_path}
Icon=bsg-ide
Terminal=false
Categories=Office;Development;Education;
Keywords=presentation;latex;beamer;slides;
"""
            desktop_path = self.install_paths['applications'] / 'bsg-ide.desktop'
            desktop_path.write_text(desktop_entry_content)
            desktop_path.chmod(0o755)

            if self.dialog:
                self.dialog.write("✓ Created desktop entry", "green")
            else:
                print("✓ Created desktop entry")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating Linux launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating Linux launcher: {str(e)}")
            return False

    def _create_windows_launcher(self):
        """Create Windows launcher script and shortcuts"""
        try:
            # Create batch file
            launcher_path = self.install_paths['bin'] / 'bsg-ide.bat'
            launcher_content = f"""@echo off
set PYTHONPATH={self.install_paths['base']};%PYTHONPATH%
python -c "from BSG_IDE import main; main()" %*
"""
            launcher_path.write_text(launcher_content)

            if self.dialog:
                self.dialog.write(f"✓ Created launcher script: {launcher_path}", "green")
            else:
                print(f"✓ Created launcher script: {launcher_path}")

            # Create Start Menu shortcut
            try:
                import winshell
                from win32com.client import Dispatch
                shortcut_dir = self.install_paths['start_menu'] / "BSG-IDE"
                shortcut_dir.mkdir(parents=True, exist_ok=True)

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_dir / "BSG-IDE.lnk"))
                shortcut.Targetpath = str(launcher_path)
                shortcut.save()

                if self.dialog:
                    self.dialog.write("✓ Created Start Menu shortcut", "green")
                else:
                    print("✓ Created Start Menu shortcut")
            except ImportError:
                if self.dialog:
                    self.dialog.write("! Warning: Could not create Start Menu shortcut", "yellow")
                else:
                    print("! Warning: Could not create Start Menu shortcut")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating Windows launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating Windows launcher: {str(e)}")
            return False

    def _create_macos_launcher(self):
        """Create macOS launcher script and application bundle"""
        try:
            # Create launcher script
            launcher_path = self.install_paths['bin'] / 'bsg-ide'
            launcher_content = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add installation directory to Python path
sys.path.insert(0, "{self.install_paths['base']}")

# Import and run main program
try:
    from BSG_IDE import main
    main()
except Exception as e:
    print(f"Error starting BSG-IDE: {{str(e)}}")
    import traceback
    traceback.print_exc()
"""
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)

            if self.dialog:
                self.dialog.write(f"✓ Created launcher script: {launcher_path}", "green")
            else:
                print(f"✓ Created launcher script: {launcher_path}")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating macOS launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating macOS launcher: {str(e)}")
            return False

    def copy_resources(self, source_dir):
            """Copy required resources to installation directories"""
            try:
                # Define required files to copy
                required_files = {
                    'BSG_IDE.py': ['base', 'python_site'],
                    'BeamerSlideGenerator.py': ['base', 'python_site'],
                    'requirements.txt': ['base'],
                    'airis4d_logo.png': ['resources'],
                    'bsg-ide.png': ['resources']
                }

                # Copy each required file
                for filename, destinations in required_files.items():
                    source_file = source_dir / filename
                    if source_file.exists():
                        for dest_type in destinations:
                            if dest_type in self.install_paths:
                                dest_path = self.install_paths[dest_type] / filename
                                try:
                                    shutil.copy2(source_file, dest_path)
                                    if self.dialog:
                                        self.dialog.write(f"✓ Copied {filename} to {dest_path}", "green")
                                    else:
                                        print(f"✓ Copied {filename} to {dest_path}")
                                except Exception as e:
                                    if self.dialog:
                                        self.dialog.write(f"! Warning: Could not copy {filename}: {e}", "yellow")
                                    else:
                                        print(f"! Warning: Could not copy {filename}: {e}")
                    else:
                        if self.dialog:
                            self.dialog.write(f"! Warning: Source file {filename} not found", "yellow")
                        else:
                            print(f"! Warning: Source file {filename} not found")

                return True

            except Exception as e:
                if self.dialog:
                    self.dialog.write(f"✗ Error copying resources: {str(e)}", "red")
                else:
                    print(f"✗ Error copying resources: {str(e)}")
                return False

    def create_directory_structure(self):
        """Create all required directories for installation"""
        try:
            # Create all directories from install_paths
            for path_type, path in self.install_paths.items():
                try:
                    # Skip creation of python_site as it's handled by pip
                    if path_type == 'python_site':
                        continue

                    path.mkdir(parents=True, exist_ok=True)
                    if self.dialog:
                        self.dialog.write(f"✓ Created directory: {path}", "green")
                    else:
                        print(f"✓ Created directory: {path}")
                except Exception as e:
                    if self.dialog:
                        self.dialog.write(f"! Warning: Could not create {path}: {e}", "yellow")
                    else:
                        print(f"! Warning: Could not create {path}: {e}")

            # Create additional required subdirectories
            media_dirs = [
                self.install_paths['base'] / 'media_files',
                self.install_paths['resources'] / 'templates',
                self.install_paths['resources'] / 'icons'
            ]

            for directory in media_dirs:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    if self.dialog:
                        self.dialog.write(f"✓ Created directory: {directory}", "green")
                    else:
                        print(f"✓ Created directory: {directory}")
                except Exception as e:
                    if self.dialog:
                        self.dialog.write(f"! Warning: Could not create {directory}: {e}", "yellow")
                    else:
                        print(f"! Warning: Could not create {directory}: {e}")

            # Create .keep files in empty directories to ensure they're tracked
            for directory in self.install_paths.values():
                if directory.is_dir() and not any(directory.iterdir()):
                    keep_file = directory / '.keep'
                    try:
                        keep_file.touch()
                    except Exception:
                        pass

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating directory structure: {str(e)}", "red")
            else:
                print(f"✗ Error creating directory structure: {str(e)}")
            return False

    def _get_install_paths(self):
        """Get installation paths based on platform and permissions"""
        paths = {}

        # Get user's home directory
        home_dir = Path.home()

        if self.is_admin:
            # System-wide installation paths
            if self.system == "Linux":
                paths.update({
                    'base': Path('/usr/local/lib/bsg-ide'),
                    'bin': Path('/usr/local/bin'),
                    'share': Path('/usr/local/share/bsg-ide'),
                    'resources': Path('/usr/local/share/bsg-ide/resources'),
                    'applications': Path('/usr/share/applications'),
                    'icons': Path('/usr/share/icons/hicolor'),
                    'python_site': Path(site.getsitepackages()[0]) / 'bsg_ide'
                })
            elif self.system == "Windows":
                program_files = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files'))
                paths.update({
                    'base': program_files / 'BSG-IDE',
                    'bin': program_files / 'BSG-IDE' / 'bin',
                    'resources': program_files / 'BSG-IDE' / 'resources',
                    'start_menu': Path(os.environ['PROGRAMDATA']) / 'Microsoft/Windows/Start Menu/Programs',
                    'python_site': Path(site.getsitepackages()[0]) / 'bsg_ide'
                })
            else:  # macOS
                paths.update({
                    'base': Path('/Applications/BSG-IDE.app/Contents'),
                    'resources': Path('/Applications/BSG-IDE.app/Contents/Resources'),
                    'bin': Path('/usr/local/bin'),
                    'python_site': Path(site.getsitepackages()[0]) / 'bsg_ide'
                })
        else:
            # User-specific installation paths
            if self.system == "Linux":
                paths.update({
                    'base': home_dir / '.local/lib/bsg-ide',
                    'bin': home_dir / '.local/bin',
                    'share': home_dir / '.local/share/bsg-ide',
                    'resources': home_dir / '.local/share/bsg-ide/resources',
                    'applications': home_dir / '.local/share/applications',
                    'icons': home_dir / '.local/share/icons/hicolor',
                    'python_site': Path(site.getusersitepackages()) / 'bsg_ide'
                })
            elif self.system == "Windows":
                appdata = Path(os.environ['APPDATA'])
                paths.update({
                    'base': appdata / 'BSG-IDE',
                    'bin': appdata / 'BSG-IDE' / 'bin',
                    'resources': appdata / 'BSG-IDE' / 'resources',
                    'start_menu': appdata / 'Microsoft/Windows/Start Menu/Programs',
                    'python_site': Path(site.getusersitepackages()) / 'bsg_ide'
                })
            else:  # macOS
                paths.update({
                    'base': home_dir / 'Applications/BSG-IDE.app/Contents',
                    'resources': home_dir / 'Applications/BSG-IDE.app/Contents/Resources',
                    'bin': home_dir / '.local/bin',
                    'python_site': Path(site.getusersitepackages()) / 'bsg_ide'
                })

        return paths

    def _verify_python_env(self):
        """Verify Python environment and dependencies"""
        required_version = (3, 7)
        if sys.version_info < required_version:
            raise RuntimeError(f"Python {required_version[0]}.{required_version[1]} or higher required")

        # Check virtual environment
        if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix') != sys.prefix:
            self.dialog.write("! Creating virtual environment...")
            venv_path = os.path.join(os.path.expanduser("~"), "my_python")
            venv.create(venv_path, with_pip=True)
            self.dialog.write("✓ Virtual environment created", "green")

    def _create_directories(self):
        """Create required directories with proper permissions"""
        for path in self.install_paths.values():
            path.mkdir(parents=True, exist_ok=True)
            self.dialog.write(f"✓ Created: {path}", "green")

    def _copy_files(self):
        """Copy required files to installation directories"""
        package_root = Path(__file__).parent
        required_files = {
            'BSG_IDE.py': {'dest': ['base', 'python_site']},
            'BeamerSlideGenerator.py': {'dest': ['base', 'python_site']},
            'requirements.txt': {'dest': ['base']},
            'airis4d_logo.png': {'dest': ['resources']},
            'bsg-ide.png': {'dest': ['resources']}
        }

        for filename, config in required_files.items():
            src = package_root / filename
            if src.exists():
                for dest_key in config['dest']:
                    dest = self.install_paths[dest_key] / filename
                    shutil.copy2(src, dest)
                    self.dialog.write(f"✓ Copied {filename} to {dest}", "green")
            else:
                self.dialog.write(f"! Warning: {filename} not found", "yellow")

    def _setup_os_integration(self):
        """Setup OS-specific integration features"""
        if self.system == "Linux":
            self._setup_linux()
        elif self.system == "Darwin":
            self._setup_macos()
        else:
            self._setup_windows()

    def _install_dependencies(self):
        """Install Python package dependencies"""
        requirements_file = self.install_paths['base'] / 'requirements.txt'
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "-r", str(requirements_file)
                ])
                self.dialog.write("✓ Installed Python dependencies", "green")
            except subprocess.CalledProcessError as e:
                self.dialog.write(f"! Warning: Some dependencies failed to install: {e}", "yellow")

    def _verify_installation(self):
        """Verify installation success"""
        problems = []

        # Check core files
        for path in self.install_paths.values():
            if not path.exists():
                problems.append(f"Missing directory: {path}")

        # Check dependencies
        try:
            import customtkinter
            import PIL
            self.dialog.write("✓ Required packages verified", "green")
        except ImportError as e:
            problems.append(f"Missing dependency: {e}")

        if problems:
            self.dialog.write("\nInstallation warnings:", "yellow")
            for problem in problems:
                self.dialog.write(f"! {problem}", "yellow")



def main():
    """Main entry point for both source and installed runs"""
    try:
        # Setup paths first
        package_root, resources_dir = setup_paths()

        # Parse arguments
        import argparse
        parser = argparse.ArgumentParser(description='BSG-IDE - Beamer Slide Generator IDE')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--fix', action='store_true',
                          help='Fix installation issues')
        group.add_argument('--install', action='store_true',
                          help='Install BSG-IDE')
        group.add_argument('--verify', action='store_true',
                          help='Verify installation')

        args = parser.parse_args()

        if args.fix or args.install:
            #from installation import install_bsg_ide
            success = install_bsg_ide(fix_mode=args.fix)
            verify_installation()
            sys.exit(0 if success else 1)

        # Launch IDE

        app = BeamerSlideEditor()
        app.mainloop()

    except Exception as e:
        print(f"Error starting BSG-IDE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
#---------------------------------------------------------------------------------------

