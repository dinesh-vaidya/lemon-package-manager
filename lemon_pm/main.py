import os
import subprocess
import sys
import json
import argparse
import requests
import importlib.resources
import tempfile
import ctypes
import shlex
import pathlib
import shutil
import time
import random
import difflib
from rich.console import Console
from rich.table import Table
from rich.live import Live
from ._version import __version__, __status__


def typewriter_effect(text, console, delay=0.05, style=None):
    """Prints text with a typewriter effect."""
    for char in text:
        console.print(char, style=style, end="")
        time.sleep(delay)
    print()

def chat():
    """Starts an interactive chat session to manage packages."""
    console = Console()
    console.print("--- Welcome to Lemon Package Manager Chat ---", style="bold yellow")

    if sys.platform == 'win32' and not is_admin():
        console.print("WARNING: Running without administrator privileges. You will not be able to install or uninstall packages.", style="bold yellow")

    console.print("Assistant:", style="bold cyan", end=" ")
    typewriter_effect("I can help you manage packages. Here are the commands you can use:", console, style="grey50")
    console.print("  list, search <pkg>, install <pkg>, info <pkg>, uninstall <pkg>, exit", style="grey50")

    try:
        with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
            packages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading package list: {e}")
        return

    package_names = list(packages.keys())
    goodbye_messages = [
        "Goodbye!",
        "See you later!",
        "Happy to help. Bye!",
        "Take care!"
    ]

    while True:
        try:
            console.print("User:", style="bold green", end=" ")
            user_input = input().lower().strip()

            if not user_input:
                continue

            if user_input in ["exit", "quit", "bye", "q"]:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect(random.choice(goodbye_messages), console)
                break

            if handle_smart_suggestions(user_input, packages, console):
                pass  # Handled in the function
            elif user_input.startswith("list") or user_input.startswith("show me"):
                handle_list_packages(packages, console)
            elif user_input.startswith("search"):
                handle_search(user_input, package_names, console)
            elif user_input.startswith("info"):
                handle_info(user_input, packages, console)
            elif user_input.startswith("uninstall"):
                handle_uninstall(user_input, package_names, console)
            elif user_input.startswith("install"):
                handle_install(user_input, package_names, console)
            else:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect("I'm not sure how to help with that. You can ask me to 'list', 'search', 'install', 'info', or 'uninstall'.", console)

        except (KeyboardInterrupt, EOFError):
            print("\n")
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(random.choice(goodbye_messages), console)
            break

def handle_list_packages(packages, console):
    console.print("Assistant:", style="bold cyan", end=" ")
    typewriter_effect("Of course! Here are all the available packages:", console, style="grey50")
    list_packages_chat(packages, console)

def handle_search(user_input, package_names, console):
    parts = user_input.split(maxsplit=1)
    if len(parts) > 1:
        package_name = parts[1]
        if package_name in package_names:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"Yes, '{package_name}' is available.", console, style="grey50")
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect("Would you like to install it? (y/n):", console, style="grey50")
            confirmation = input().lower().strip()
            if confirmation == 'y':
                install_package(package_name, from_chat=True)
            else:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect("Okay, I will not install it.", console, style="grey50")
        else:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"Sorry, '{package_name}' is not available.", console, style="grey50")
    else:
        console.print("Assistant:", style="bold cyan", end=" ")
        typewriter_effect("Please specify a package to search for.", console, style="grey50")

def handle_info(user_input, packages, console):
    parts = user_input.split(maxsplit=1)
    if len(parts) > 1:
        package_name = parts[1]
        if package_name in packages:
            pkg_data = packages[package_name]
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"Here is some information about '{package_name}':", console, style="grey50")
            console.print(f"  Version: {pkg_data.get('version', 'N/A')}", style="cyan")
            console.print(f"  Description: {pkg_data.get('description', 'No description available.')}", style="cyan")
        else:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"Sorry, I couldn't find '{package_name}'.", console, style="grey50")
    else:
        console.print("Assistant:", style="bold cyan", end=" ")
        typewriter_effect("Please specify a package to get info about.", console, style="grey50")

def handle_uninstall(user_input, package_names, console):
    parts = user_input.split(maxsplit=1)
    if len(parts) > 1:
        package_name = parts[1]
        if package_name in package_names:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"Are you sure you want to uninstall '{package_name}'? (y/n):", console, style="grey50")
            confirmation = input().lower().strip()
            if confirmation == 'y':
                uninstall_package(package_name, from_chat=True)
            else:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect("Okay, I will not uninstall it.", console, style="grey50")
        else:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"Sorry, '{package_name}' is not in the package list.", console, style="grey50")
    else:
        console.print("Assistant:", style="bold cyan", end=" ")
        typewriter_effect("Please specify a package to uninstall.", console, style="grey50")

def handle_install(user_input, package_names, console):
    parts = user_input.split(maxsplit=1)
    if len(parts) > 1:
        package_name = parts[1]
        if package_name in package_names:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"I found '{package_name}' in our list. It is available.", console, style="grey50")
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect("Would you like to install it? (y/n):", console, style="grey50")
            confirmation = input().lower().strip()
            if confirmation == 'y':
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect(f"Great! Starting the installation for {package_name}.", console, style="grey50")
                install_package(package_name, from_chat=True)
            else:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect("Understood. I will not install it.", console, style="grey50")
        else:
            close_matches = difflib.get_close_matches(package_name, package_names)
            if close_matches:
                suggestion = close_matches[0]
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect(f"I couldn't find '{package_name}'. Did you mean '{suggestion}'? (y/n):", console, style="grey50")
                confirmation = input().lower().strip()
                if confirmation == 'y':
                    console.print("Assistant:", style="bold cyan", end=" ")
                    typewriter_effect(f"Great! Starting the installation for {suggestion}.", console, style="grey50")
                    install_package(suggestion, from_chat=True)
                else:
                    console.print("Assistant:", style="bold cyan", end=" ")
                    typewriter_effect("My mistake. I won't install that.", console, style="grey50")
            else:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect("I'm sorry, I couldn't find the requested software in our package list.", console, style="grey50")
    else:
        console.print("Assistant:", style="bold cyan", end=" ")
        typewriter_effect("Please specify a package to install.", console, style="grey50")

def handle_smart_suggestions(user_input, packages, console):
    categories = set(data.get('category', 'Uncategorized').lower() for data in packages.values())
    found_category = None
    for cat in categories:
        if cat in user_input:
            found_category = cat
            break

    if found_category:
        console.print("Assistant:", style="bold cyan", end=" ")
        typewriter_effect(f"I found some packages in the '{found_category}' category:", console, style="grey50")

        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Package", style="green", no_wrap=True)
        table.add_column("Version", style="cyan")

        category_packages = []
        for name, data in packages.items():
            if data.get('category', '').lower() == found_category:
                table.add_row(name, data.get('version', 'N/A'))
                category_packages.append(name)
        console.print(table)
        console.print("\nAssistant:", style="bold cyan", end=" ")
        typewriter_effect("Would you like to install any of these? If so, just type the name.", console, style="grey50")

        console.print("User:", style="bold green", end=" ")
        next_input = input().lower().strip()
        if next_input in category_packages:
            install_package(next_input, from_chat=True)
        else:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect("Okay, I will not install any of these.", console, style="grey50")
        return True
    return False

def demo():
    """Demonstrates all available commands with examples."""
    console = Console()
    console.print("--- Lemon Package Manager Demo ---", style="bold yellow")

    typewriter_effect("\n1. List all available packages:", console)
    console.print("$ lemon list", style="cyan")
    list_packages(animate=True)

    typewriter_effect("\n2. List packages in a specific category:", console)
    console.print("$ lemon list Utilities", style="cyan")
    list_packages(category_filter="Utilities", animate=True)

    typewriter_effect("\n3. Install a package:", console)
    console.print("$ lemon install 7-zip", style="cyan")
    typewriter_effect("   (This will download and run the installer for 7-zip)", console)

    typewriter_effect("\n4. Uninstall a package:", console)
    console.print("$ lemon uninstall 7-zip", style="cyan")
    typewriter_effect("   (This will run the uninstaller for 7-zip)", console)

    typewriter_effect("\n5. Run a package:", console)
    console.print("$ lemon run 7-zip", style="cyan")
    typewriter_effect("   (This will attempt to launch the main executable for 7-zip)", console)

    typewriter_effect("\n6. List all available categories:", console)
    console.print("$ lemon categories", style="cyan")
    list_categories()

    typewriter_effect("\n7. Show the version of lemon-pm:", console)
    console.print("$ lemon version", style="cyan")
    console.print(f"Lemon Package Manager version {__version__} (status: {__status__})")

    typewriter_effect("\n8. Uninstall the lemon package manager itself:", console)
    console.print("$ lemon uninstall-lpm", style="cyan")
    typewriter_effect("   (This will prompt for confirmation before uninstalling)", console)

    console.print("\n--- End of Demo ---", style="bold yellow")

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_version():
    """Reads the version from _version.py."""
    return f"{__version__} (status: {__status__})"

def list_packages_chat(packages, console):
    """Lists all available packages with only name and version for the chat command."""
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Package", style="green", no_wrap=True)
    table.add_column("Version", style="cyan")

    sorted_packages = sorted(packages.items(), key=lambda x: x[0])

    for name, data in sorted_packages:
        version = data.get('version', 'N/A')
        table.add_row(name, version)

    console.print(table)

def list_packages(category_filter=None, animate=False):
    """Lists all available packages in a category-wise table."""
    try:
        with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
            packages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading package list: {e}")
        return

    categorized_packages = {}
    for name, data in packages.items():
        category = data.get('category', 'Uncategorized')
        if category_filter and category.lower() != category_filter.lower():
            continue
        if category not in categorized_packages:
            categorized_packages[category] = []
        version = data.get('version', 'N/A')
        description = data.get('description', 'No description available.')
        categorized_packages[category].append({'name': name, 'version': version, 'description': description})

    console = Console()
    console.print("Available packages:", style="bold white")

    sorted_categories = sorted(categorized_packages.keys())

    # Pre-sort all packages to avoid doing it in the loop
    for category in sorted_categories:
        categorized_packages[category] = sorted(categorized_packages[category], key=lambda x: x['name'])

    if not animate:
        for category in sorted_categories:
            if not categorized_packages[category]:
                continue
            table = Table(title=f"[bold yellow]{category}[/bold yellow]", show_header=True, header_style="bold magenta", expand=True)
            table.add_column("Package", style="green", no_wrap=True)
            table.add_column("Version", style="cyan")
            table.add_column("Description", style="white")

            for pkg in categorized_packages[category]:
                table.add_row(pkg['name'], pkg['version'], pkg['description'])
            console.print(table)
    else:
        # Animation mode
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Package", style="green", no_wrap=True)
        table.add_column("Version", style="cyan")
        table.add_column("Description", style="white")

        current_category = None

        with Live(table, console=console, screen=False, vertical_overflow="visible") as live:
            for category in sorted_categories:
                if not categorized_packages[category]:
                    continue

                # Add a temporary row for the category header
                if current_category != category:
                    if current_category is not None:
                        # Add a separator before the new category
                        table.add_row("---", "---", "---")
                    table.title = f"[bold yellow]{category}[/bold yellow]"
                    current_category = category
                    live.update(table) # Refresh to show the new title
                    time.sleep(0.5)

                for pkg in categorized_packages[category]:
                    table.add_row(pkg['name'], pkg['version'], pkg['description'])
                    live.update(table)
                    time.sleep(0.1)

    console.print("End of list.", style="bold white")

def get_portable_bin_dir():
    """Gets the directory for storing portable application binaries."""
    # On Windows, this will expand to C:\\Users\\<user>\\AppData\\Local
    local_app_data = os.path.expandvars('%LOCALAPPDATA%')
    if '%LOCALAPPDATA%' in local_app_data:
        # If the variable wasn't expanded (on non-Windows), use a fallback
        # This is mainly for testing in the sandbox environment.
        home = os.path.expanduser("~")
        local_app_data = os.path.join(home, '.local', 'share')

    lemon_dir = os.path.join(local_app_data, 'lemon')
    bin_dir = os.path.join(lemon_dir, 'bin')
    os.makedirs(bin_dir, exist_ok=True)
    return bin_dir


def is_installed(package_name):
    """Checks if a package is likely installed."""
    try:
        with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
            packages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False  # Cannot determine if installed if package list is missing

    if package_name not in packages:
        return False

    package_data = packages[package_name]
    package_type = package_data.get('type', 'installer')

    if package_type == 'portable':
        executable_name = package_data.get('executable_name')
        if not executable_name:
            return False
        bin_dir = get_portable_bin_dir()
        executable_path = pathlib.Path(bin_dir) / executable_name
        return executable_path.exists()

    elif package_type == 'installer':
        uninstall_command = package_data.get('uninstall_command')
        if not uninstall_command:
            return False

        if sys.platform == 'win32':
            replacements = {
                '%ProgramFiles%': os.environ.get('ProgramW6432', os.environ.get('ProgramFiles')),
                '%ProgramFiles(x86)%': os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles')),
                '%LOCALAPPDATA%': os.environ.get('LOCALAPPDATA'),
                '%APPDATA%': os.environ.get('APPDATA')
            }
            for var, val in replacements.items():
                if val:
                    uninstall_command = uninstall_command.replace(var, val)

        try:
            command_parts = shlex.split(uninstall_command)
            if not command_parts:
                return False

            uninstaller_path = pathlib.Path(command_parts[0])

            if uninstaller_path.name.lower() in ['msiexec.exe', 'wmic.exe']:
                return False

            return uninstaller_path.exists()
        except Exception:
            return False

    return False


def install_package(package_name, from_chat=False):
    """Downloads and installs a package."""
    if is_installed(package_name):
        print(f"'{package_name}' is already installed.")
        return

    if sys.platform == 'win32' and not is_admin():
        if from_chat:
            console = Console()
            console.print("Administrator privileges are required to install packages.", style="bold red")
            console.print("Please restart chat with administrator privileges to install packages.", style="bold red")
            return
        print("ERROR: Administrator privileges are required to install packages.")
        print("Please re-run this command from a terminal with administrator privileges.")
        sys.exit(1)

    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]
    url = package_data['url']
    version = package_data['version']
    package_type = package_data.get('type', 'installer') # Default to 'installer'

    print(f"Installing {package_name} version {version} ({package_type})...")

    try:
        # Some servers (like GitHub) block requests without a User-Agent header.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        filename = url.split('/')[-1]
        # Download to a temp location first
        temp_dir = tempfile.gettempdir()
        temp_filepath = os.path.join(temp_dir, filename)

        total_size = int(response.headers.get('content-length', 0))

        with open(temp_filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                done = int(50 * downloaded / total_size)
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes")
                sys.stdout.flush()
        sys.stdout.write('\n')

        print(f"Downloaded '{filename}'.")

        if package_type == 'installer':
            install_command = package_data.get('install_command', [])

            print(f"Running installer for {package_name}...")
            try:
                # Base command
                command = [temp_filepath]

                # If it's an MSI file, it must be installed with msiexec
                if temp_filepath.endswith('.msi'):
                    command = ['msiexec', '/i', temp_filepath] + install_command
                else:
                    command = [temp_filepath] + install_command

                # Using check=True will raise a CalledProcessError if the command returns a non-zero exit code.
                result = subprocess.run(command, check=True, capture_output=True, text=True, shell=False)

                print(f"Installation of {package_name} completed.")
                if result.stdout:
                    print("Output:", result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
                print(f"Successfully installed {package_name}.")

            except subprocess.CalledProcessError as e:
                print(f"An error occurred during installation for {package_name}.")
                print(f"Return code: {e.returncode}")
                if e.stdout:
                    print("Output:", e.stdout)
                if e.stderr:
                    print("Errors:", e.stderr)
            except FileNotFoundError:
                # This can happen if the downloaded file is not a valid executable
                print(f"Error: Installer not found at '{temp_filepath}'. The file may be corrupted or not a valid installer.")
            except PermissionError:
                print(f"Error: Permission denied to execute the installer at '{temp_filepath}'.")
            finally:
                # Always clean up the downloaded installer
                print(f"Cleaning up...")
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)

        elif package_type == 'portable':
            bin_dir = get_portable_bin_dir()
            executable_name = package_data.get('executable_name', filename)
            final_filepath = os.path.join(bin_dir, executable_name)
            print(f"Moving '{filename}' to '{bin_dir}'...")
            os.rename(temp_filepath, final_filepath)
            # Make the file executable
            os.chmod(final_filepath, 0o755)
            print(f"Successfully installed {package_name} to {final_filepath}")
            print("NOTE: You may need to add this directory to your system's PATH to run the command from anywhere.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {package_name}: {e}")
    except Exception as e:
        print(f"An error occurred during installation: {e}")

def run_package(package_name):
    """Launches a package's main executable."""
    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]
    package_type = package_data.get('type', 'installer')

    try:
        executable_path = None
        if package_type == 'portable':
            executable_name = package_data.get('executable_name')
            if not executable_name:
                print(f"Error: No executable_name defined for portable package '{package_name}'.")
                return
            bin_dir = get_portable_bin_dir()
            executable_path = pathlib.Path(bin_dir) / executable_name

        else: # 'installer' type
            executable = package_data.get('executable')
            if not executable:
                print(f"Error: No executable defined for '{package_name}'. Cannot run.")
                return

            uninstall_command = package_data.get('uninstall_command')
            if not uninstall_command:
                # If there's no uninstall command, we can't infer the path.
                # This is a limitation for now.
                print(f"Error: Cannot determine installation directory for '{package_name}' without an uninstall_command.")
                return

            # First, expand environment variables in the uninstall command path
            if sys.platform == 'win32':
                replacements = {
                    '%ProgramFiles%': os.environ.get('ProgramW6432', os.environ.get('ProgramFiles')),
                    '%ProgramFiles(x86)%': os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles')),
                    '%LOCALAPPDATA%': os.environ.get('LOCALAPPDATA'),
                    '%APPDATA%': os.environ.get('APPDATA')
                }
                for var, val in replacements.items():
                    if val and uninstall_command:
                        uninstall_command = uninstall_command.replace(var, val)

            # Use shlex to handle quotes and split the command
            parts = shlex.split(uninstall_command)
            if not parts:
                raise ValueError("Uninstall command is empty.")

            # The first part is usually the path to the uninstaller
            uninstaller_path = pathlib.Path(parts[0])
            install_dir = uninstaller_path.parent

            # For some apps, the uninstaller is in a sub-folder (e.g., .../Installer/setup.exe)
            # We might need to go up one level. A simple check: if parent is "Installer", go up.
            if install_dir.name.lower() == 'installer':
                install_dir = install_dir.parent

            executable_path = install_dir / executable

            if not executable_path.exists():
                # Second guess: maybe it's in a subdirectory like 'bin'
                if (install_dir / 'bin' / executable).exists():
                    executable_path = install_dir / 'bin' / executable
                else:
                    print(f"Error: Could not find executable '{executable}' at '{executable_path}'")
                    print("The installation directory was inferred as:", install_dir)
                    return

        if not executable_path or not executable_path.exists():
            print(f"Error: Executable path not found or does not exist: {executable_path}")
            return

        print(f"Launching '{executable_path.name}' from '{executable_path}'...")
        # Use Popen to launch the process in the background without blocking the terminal.
        subprocess.Popen([str(executable_path)], shell=False)

    except Exception as e:
        print(f"An error occurred while trying to run {package_name}: {e}")
        print("Note: The 'run' command relies on heuristics to find the executable and may not work for all packages.")

def uninstall_package(package_name, from_chat=False):
    """Uninstalls a package using its uninstall command, or provides instructions."""
    if not is_installed(package_name):
        print(f"'{package_name}' is not installed.")
        return

    if sys.platform == 'win32' and not is_admin():
        if from_chat:
            console = Console()
            console.print("Administrator privileges are required to uninstall packages.", style="bold red")
            console.print("Please restart chat with administrator privileges to uninstall packages.", style="bold red")
            return
        print("ERROR: Administrator privileges are required to uninstall packages.")
        print("Please re-run this command from a terminal with administrator privileges.")
        sys.exit(1)

    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]
    package_type = package_data.get('type', 'installer')

    if package_type == 'portable':
        bin_dir = get_portable_bin_dir()
        executable_name = package_data.get('executable_name')
        if not executable_name:
             print(f"Error: No executable_name defined for portable package '{package_name}'. Cannot uninstall.")
             return

        final_filepath = os.path.join(bin_dir, executable_name)

        print(f"Uninstalling portable package: {package_name}")
        if os.path.exists(final_filepath):
            try:
                os.remove(final_filepath)
                print(f"Successfully removed '{final_filepath}'.")
            except OSError as e:
                print(f"Error removing file '{final_filepath}': {e}")
        else:
            print(f"Warning: Executable '{final_filepath}' not found. It may have already been uninstalled.")

    elif package_type == 'installer':
        uninstall_command = package_data.get('uninstall_command')
        if uninstall_command:
            print(f"Attempting to silently uninstall {package_name}...")
            print(f"Running command: {uninstall_command}")
            try:
                # Manually expand known environment variables for security and correctness.
                if sys.platform == 'win32':
                    # On 64-bit Windows, ProgramW6432 is the path to the 64-bit Program Files
                    # folder, which is what we usually want. %ProgramFiles% can point to the
                    # x86 folder if the script is run with a 32-bit Python interpreter.
                    replacements = {
                        '%ProgramFiles%': os.environ.get('ProgramW6432', os.environ.get('ProgramFiles')),
                        '%ProgramFiles(x86)%': os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles')),
                        '%LOCALAPPDATA%': os.environ.get('LOCALAPPDATA'),
                        '%APPDATA%': os.environ.get('APPDATA')
                    }
                    for var, val in replacements.items():
                        if val: # Only replace if the environment variable exists
                            uninstall_command = uninstall_command.replace(var, val)

                # Use shlex.split to safely parse the command string into a list.
                command_parts = shlex.split(uninstall_command)

                # Using shell=False is safer as it avoids shell injection vulnerabilities.
                result = subprocess.run(command_parts, check=True, capture_output=True, text=True, shell=False)

                print(f"Uninstallation command for {package_name} completed.")
                if result.stdout:
                    print("Output:", result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
            except FileNotFoundError:
                print(f"Error: Uninstaller not found. It's possible '{package_name}' is not installed or the path is incorrect.")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred during uninstallation for {package_name}.")
                print(f"Return code: {e.returncode}")
                if e.stdout:
                    print("Output:", e.stdout)
                if e.stderr:
                    print("Errors:", e.stderr)
        else:
            # Fallback for installer packages without a defined uninstall command.
            print(f"No automatic uninstall command found for '{package_name}'.")
            print("Please uninstall it manually using the 'Add or Remove Programs' feature in Windows Settings.")
            print("1. Open Settings > Apps > Apps & features.")
            print(f"2. Find '{package_name}' in the list and select 'Uninstall'.")


def uninstall_lemon():
    """Uninstalls the lemon package manager itself."""
    console = Console()
    console.print("This will uninstall the Lemon Package Manager from your system. This action is irreversible.", style="bold red")

    confirm = input("Are you sure you want to continue? (y/n): ")

    if confirm.lower() == 'y':
        print("Uninstalling Lemon Package Manager...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "lemon-pm", "-y"], check=True)
            print("Lemon Package Manager has been successfully uninstalled.")
            console.print("Thank you for using Lemon Package Manager!", style="bold green")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during uninstallation: {e}")
        except FileNotFoundError:
            print("Error: 'pip' command not found. Please ensure you have pip installed and in your PATH.")
    else:
        print("Uninstallation cancelled.")

def list_categories():
    """Lists all available package categories."""
    try:
        with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
            packages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading package list: {e}")
        return

    categories = set(data.get('category', 'Uncategorized') for data in packages.values())
    console = Console()
    console.print("Available categories:", style="bold white")
    for category in sorted(categories):
        console.print(f"- [yellow]{category}[/yellow]")

def main():
    """Main function for the lemon package manager."""
    parser = argparse.ArgumentParser(description="A simple package manager for Windows.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # 'install' command
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package_name', help='The name of the package to install')

    # 'uninstall' command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package_name', help='The name of the package to uninstall')

    # 'list' command
    list_parser = subparsers.add_parser('list', help='List available packages, optionally filtered by category')
    list_parser.add_argument('category', nargs='?', default=None, help='The category to filter by')

    # 'categories' command
    categories_parser = subparsers.add_parser('categories', help='List all available package categories')

    # 'run' command
    run_parser = subparsers.add_parser('run', help='Run an installed package')
    run_parser.add_argument('package_name', help='The name of the package to run')

    # 'version' command
    version_parser = subparsers.add_parser('version', help='Show the version of lemon-pm')

    # 'help' command
    help_parser = subparsers.add_parser('help', help='Show this help message')

    # 'uninstall-lpm' command
    uninstall_lemon_parser = subparsers.add_parser('uninstall-lpm', help='Uninstall the lemon package manager itself')

    # 'demo' command
    demo_parser = subparsers.add_parser('demo', help='Demonstrate all available commands')

    # 'chat' command
    chat_parser = subparsers.add_parser('chat', help='Start an interactive chat session')


    args = parser.parse_args()

    if args.command == 'install':
        install_package(args.package_name)
    elif args.command == 'uninstall':
        uninstall_package(args.package_name)
    elif args.command == 'run':
        run_package(args.package_name)
    elif args.command == 'list':
        list_packages(args.category)
    elif args.command == 'categories':
        list_categories()
    elif args.command == 'version':
        print(f"Lemon Package Manager version {__version__} (status: {__status__})")
    elif args.command == 'uninstall-lpm':
        uninstall_lemon()
    elif args.command == 'demo':
        demo()
    elif args.command == 'chat':
        chat()
    elif args.command == 'help':
        parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
