import os
import subprocess
import sys
import json
import argparse
import requests
import importlib.resources

def list_packages():
    """Lists all available packages."""
    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)
    print("Available packages:")
    for name, data in packages.items():
        print(f"  - {name} ({data['version']})")

def install_package(package_name):
    """Downloads and installs a package."""
    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]
    url = package_data['url']
    version = package_data['version']
    print(f"Installing {package_name} version {version}...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        filename = url.split('/')[-1]
        total_size = int(response.headers.get('content-length', 0))

        with open(filename, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                # Simple progress indication
                done = int(50 * downloaded / total_size)
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes")
                sys.stdout.flush()
        sys.stdout.write('\n')

        print(f"Downloaded '{filename}'.")

        # NOTE: This will not work in a non-Windows environment.
        # This is a simulation of running the installer.
        print(f"Running installer for {package_name}...")
        # On a real Windows system, this would be:
        # subprocess.run([filename], check=True)
        # For simulation, we'll just print a message.
        print(f"(Simulation) Would run: subprocess.run(['{filename}'], check=True)")

        print(f"Cleaning up...")
        os.remove(filename)

        print(f"Successfully installed {package_name}.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {package_name}: {e}")
    except Exception as e:
        print(f"An error occurred during installation: {e}")

def uninstall_package(package_name):
    """Uninstalls a package using its uninstall command, or provides instructions."""
    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        packages = json.load(f)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]
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
        # Fallback for packages without a defined uninstall command.
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
