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
from rich.console import Console
from rich.table import Table
from ._version import __version__, __status__


def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_version():
    """Reads the version from _version.py."""
    return f"{__version__} (status: {__status__})"

def list_packages(category_filter=None):
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
        categorized_packages[category].append({'name': name, 'version': version})

    console = Console()
    console.print("Available packages:", style="bold white")

    for category in sorted(categorized_packages.keys()):

        table = Table(title=f"[bold yellow]{category}[/bold yellow]", show_header=True, header_style="bold magenta")
        table.add_column("Package", style="green", no_wrap=True)
        table.add_column("Version", style="cyan")

        sorted_packages = sorted(categorized_packages[category], key=lambda x: x['name'])
        if not sorted_packages:
            continue

        for pkg in sorted_packages:
            table.add_row(pkg['name'], pkg['version'])

        console.print(table)

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

def install_package(package_name):
    """Downloads and installs a package."""
    if sys.platform == 'win32' and not is_admin():
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

def uninstall_package(package_name):
    """Uninstalls a package using its uninstall command, or provides instructions."""
    if sys.platform == 'win32' and not is_admin():
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
    print("Uninstalling lemon-pm...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "lemon-pm", "-y"], check=True)
        print("lemon-pm has been successfully uninstalled.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during uninstallation: {e}")
    except FileNotFoundError:
        print("Error: 'pip' command not found. Please ensure you have pip installed and in your PATH.")

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

    # 'uninstall-lemon' command
    uninstall_lemon_parser = subparsers.add_parser('uninstall-lemon', help='Uninstall the lemon package manager itself')


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
        print(f"lemon-pm version {__version__} (status: {__status__})")
    elif args.command == 'uninstall-lemon':
        uninstall_lemon()
    elif args.command == 'help':
        parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
