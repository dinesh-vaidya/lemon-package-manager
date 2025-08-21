import os
import subprocess
import sys
import json
import argparse
import requests
import importlib.resources
import tempfile
import ctypes

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-launches the script with administrator privileges."""
    # This will show a UAC prompt to the user.
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def list_packages():
    """Lists all available packages."""
    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)
    print("Available packages:")
    for name, data in packages.items():
        print(f"  - {name} ({data['version']})")

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
        print("Administrator privileges are required to install packages. Requesting elevation...")
        run_as_admin()
        sys.exit(0)

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
            install_command = package_data.get('install_command')
            if not install_command:
                print(f"Error: No install_command defined for '{package_name}'.")
                # Still need to clean up the downloaded file
                os.remove(temp_filepath)
                return

            # NOTE: This will not work in a non-Windows environment.
            print(f"Running installer for {package_name}...")
            try:
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

def uninstall_package(package_name):
    """Uninstalls a package using its uninstall command, or provides instructions."""
    if sys.platform == 'win32' and not is_admin():
        print("Administrator privileges are required to uninstall packages. Requesting elevation...")
        run_as_admin()
        sys.exit(0)

    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]
    package_type = package_data.get('type', 'installer')

    if package_type == 'portable':
        bin_dir = get_portable_bin_dir()
        # For portable apps, the 'uninstall_command' is just the filename to be deleted.
        executable_name = package_data.get('uninstall_command') # Re-using this field
        if not executable_name:
             print(f"Error: No executable name defined for portable package '{package_name}'. Cannot uninstall.")
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
                # Using shell=True is necessary to expand environment variables like %ProgramFiles%.
                # This is safe here because the commands are defined by us in packages.json.
                # This command will only work on Windows.
                result = subprocess.run(uninstall_command, shell=True, check=True, capture_output=True, text=True)
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
    list_parser = subparsers.add_parser('list', help='List available packages')

    args = parser.parse_args()

    if args.command == 'install':
        install_package(args.package_name)
    elif args.command == 'uninstall':
        uninstall_package(args.package_name)
    elif args.command == 'list':
        list_packages()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
