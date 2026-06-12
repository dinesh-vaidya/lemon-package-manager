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
import zipfile
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

def get_packages():
    """Reads the package list, prioritizing the updated local archive if it exists."""
    local_archive = os.path.join(get_lemon_dir(), 'packages.json')
    if os.path.exists(local_archive):
        try:
            with open(local_archive, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Fallback to the bundled version
    with importlib.resources.open_text('lemon_pm', 'packages.json') as f:
        return json.load(f)

def get_cache_file():
    """Gets the path to the update cache file."""
    return os.path.join(get_lemon_dir(), 'cache.json')

def get_cache():
    """Reads the update cache."""
    cache_file = get_cache_file()
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def update_cache(key, value):
    """Updates a value in the update cache."""
    cache = get_cache()
    cache[key] = value
    try:
        with open(get_cache_file(), 'w') as f:
            json.dump(cache, f, indent=2)
    except OSError:
        pass

def sync_archive(quiet=False):
    """Fetches the latest packages.json from the remote repository efficiently."""
    url = "https://raw.githubusercontent.com/dinesh-vaidya/lemon-package-manager/main/lemon_pm/packages.json"
    if not quiet: print("Syncing package archive...")

    cache = get_cache()
    headers = {}
    if 'packages_etag' in cache:
        headers['If-None-Match'] = cache['packages_etag']
    if 'packages_last_modified' in cache:
        headers['If-Modified-Since'] = cache['packages_last_modified']

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 304:
            if not quiet: print("Package archive is already up to date (cached).")
            return True

        response.raise_for_status()
        new_packages = response.json()

        local_archive = os.path.join(get_lemon_dir(), 'packages.json')
        with open(local_archive, 'w') as f:
            json.dump(new_packages, f, indent=2)

        # Update cache with new ETag/Last-Modified
        if 'ETag' in response.headers:
            update_cache('packages_etag', response.headers['ETag'])
        if 'Last-Modified' in response.headers:
            update_cache('packages_last_modified', response.headers['Last-Modified'])

        if not quiet: print("Successfully updated package archive.")
        return True
    except Exception as e:
        if not quiet: print(f"Failed to sync archive: {e}")
        return False

def self_update():
    """Updates the package manager itself efficiently."""
    base_url = "https://raw.githubusercontent.com/dinesh-vaidya/lemon-package-manager/main/lemon_pm/"
    files_to_update = ["main.py", "_version.py", "__init__.py"]

    print("Checking for Lemon Package Manager updates...")

    # Get the directory where the current module is located
    try:
        module_dir = pathlib.Path(__file__).parent.resolve()
    except NameError:
        print("Error: Could not determine module directory for self-update.")
        return False

    cache = get_cache()
    updated_files = 0

    for filename in files_to_update:
        url = base_url + filename
        file_path = module_dir / filename

        headers = {}
        etag_key = f'file_etag_{filename}'
        last_mod_key = f'file_last_mod_{filename}'

        if etag_key in cache:
            headers['If-None-Match'] = cache[etag_key]
        if last_mod_key in cache:
            headers['If-Modified-Since'] = cache[last_mod_key]

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 304:
                continue

            response.raise_for_status()

            # Write the new content to a temporary file first for atomicity
            temp_fd, temp_path = tempfile.mkstemp(dir=module_dir)
            try:
                with os.fdopen(temp_fd, 'wb') as f:
                    f.write(response.content)
                # Atomic move
                os.replace(temp_path, file_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise

            # Update cache
            if 'ETag' in response.headers:
                update_cache(etag_key, response.headers['ETag'])
            if 'Last-Modified' in response.headers:
                update_cache(last_mod_key, response.headers['Last-Modified'])

            updated_files += 1
            print(f"Updated {filename}.")

        except Exception as e:
            print(f"Failed to update {filename}: {e}")
            return False

    if updated_files > 0:
        print(f"Successfully updated {updated_files} file(s). Changes will take effect on next run.")
        # Also sync the archive to be sure
        sync_archive(quiet=True)
    else:
        print("Lemon Package Manager is already up to date.")
        # Still sync the archive if we are checking for updates
        sync_archive()

    return True

def chat():
    """Starts an interactive chat session to manage packages."""
    console = Console()
    console.print("--- Welcome to Lemon Package Manager AI Chat ---", style="bold yellow")

    if sys.platform == 'win32' and not is_admin():
        console.print("WARNING: Running without administrator privileges. You will not be able to install or uninstall packages.", style="bold yellow")

    console.print("Assistant:", style="bold cyan", end=" ")
    typewriter_effect(f"Hello! I'm your Lemon PM assistant (version {__version__}).", console, style="grey50")
    console.print("Assistant:", style="bold cyan", end=" ")
    typewriter_effect("I can help you search, install, and manage your software. Try asking for a category like 'AI' or just 'list' everything.", console, style="grey50")
    console.print("Available commands: list, search, install, check, upgrade, update, info, uninstall, exit", style="dim grey50")

    packages = get_packages()
    package_names = list(packages.keys())

    goodbye_messages = [
        "Goodbye! Have a great day!",
        "See you later! Happy computing!",
        "Happy to help. Come back anytime!",
        "Take care! Your system is now a little more lemony."
    ]

    while True:
        try:
            console.print("\nUser:", style="bold green", end=" ")
            user_input = input().lower().strip()

            if not user_input:
                continue

            if user_input in ["exit", "quit", "bye", "q"]:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect(random.choice(goodbye_messages), console)
                break

            if user_input in ["ok", "okay", "thanks", "thank you", "hello", "hi"]:
                console.print("Assistant:", style="bold cyan", end=" ")
                if user_input in ["hello", "hi"]:
                    typewriter_effect("Hello! How can I assist you with your packages today?", console, style="grey50")
                else:
                    typewriter_effect("You're very welcome! Is there anything else you'd like to do?", console, style="grey50")
            elif any(p in user_input for p in ["how many", "number of", "total", "count"]) and "packages" in user_input:
                handle_package_count(packages, console)
            elif handle_smart_suggestions(user_input, packages, console):
                pass  # Handled in the function
            elif user_input.startswith("list") or user_input.startswith("show me") or user_input == "ls":
                handle_list_packages(packages, console)
            elif user_input.startswith("search") or user_input.startswith("find"):
                handle_search(user_input, package_names, console)
            elif user_input.startswith("info") or user_input.startswith("about"):
                handle_info(user_input, packages, console)
            elif user_input.startswith("uninstall") or user_input.startswith("remove"):
                handle_uninstall(user_input, package_names, console)
            elif user_input.startswith("install") or user_input.startswith("get") or user_input.startswith("add"):
                handle_install(user_input, package_names, console)
            elif user_input.startswith("upgrade"):
                handle_upgrade(user_input, console)
            elif user_input.startswith("check") or "updates" in user_input:
                check_updates()
            elif user_input.startswith("update") or user_input == "sync":
                sync_archive()
            elif user_input.startswith("self-update") or user_input == "upgrade-lpm":
                self_update()
            elif user_input in ["help", "help me", "?"]:
                console.print("Assistant:", style="bold cyan", end=" ")
                typewriter_effect("I can help with the following tasks:", console, style="grey50")
                console.print("  - [bold]List[/bold]: Show all packages or filtered by category.")
                console.print("  - [bold]Search[/bold]: Find a specific package by name.")
                console.print("  - [bold]Install[/bold]: Download and set up a new application.")
                console.print("  - [bold]Info[/bold]: Get details about a specific software.")
                console.print("  - [bold]Upgrade[/bold]: Update your installed apps to the latest version.")
                console.print("  - [bold]Uninstall[/bold]: Remove software from your system.")
            else:
                # Fuzzy matching for common commands
                commands = ["list", "install", "uninstall", "search", "info", "upgrade", "check", "update"]
                closest = difflib.get_close_matches(user_input.split()[0], commands, n=1, cutoff=0.6)

                console.print("Assistant:", style="bold cyan", end=" ")
                if closest:
                    typewriter_effect(f"I didn't quite catch that. Did you mean '{closest[0]}'? If not, you can type 'help' to see what I can do.", console)
                else:
                    typewriter_effect("I'm not sure how to help with that. You can ask me to 'list', 'search', 'install', or type 'help' for more options.", console)

        except (KeyboardInterrupt, EOFError):
            print("\n")
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(random.choice(goodbye_messages), console)
            break

def handle_package_count(packages, console):
    """Handles the user's request for the total number of packages."""
    total_packages = len(packages)
    console.print("Assistant:", style="bold cyan", end=" ")
    typewriter_effect(f"There are currently {total_packages} packages available.", console, style="grey50")


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

def handle_upgrade(user_input, console):
    parts = user_input.split(maxsplit=1)
    package_name = parts[1] if len(parts) > 1 else None
    upgrade_package(package_name)

def handle_install(user_input, package_names, console):
    parts = user_input.split(maxsplit=1)
    if len(parts) > 1:
        raw_package_name = parts[1]
        package_name = raw_package_name.split('@')[0]
        target_version = raw_package_name.split('@')[1] if '@' in raw_package_name else None

        if package_name in package_names:
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect(f"I found '{package_name}' in our list. It is available.", console, style="grey50")
            console.print("Assistant:", style="bold cyan", end=" ")
            typewriter_effect("Would you like to install it? (y/n):", console, style="grey50")
            confirmation = input().lower().strip()
            if confirmation == 'y':
                console.print("Assistant:", style="bold cyan", end=" ")
                msg = f"Great! Starting the installation for {package_name}."
                if target_version:
                    msg = f"Great! Starting the installation for {package_name} version {target_version}."
                typewriter_effect(msg, console, style="grey50")
                install_package(raw_package_name, from_chat=True)
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
    user_input_lower = user_input.lower()
    categories = set(data.get('category', 'Uncategorized').lower() for data in packages.values())
    found_category = None
    for cat in categories:
        # Check if the category name (or its singular form) is in the input
        if cat in user_input_lower or (cat.endswith('s') and cat[:-1] in user_input_lower):
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

    typewriter_effect("\n1. List all available packages (Animated/Typewriter):", console)
    console.print("$ lemon list", style="cyan")
    console.print("[dim](Tip: Press Ctrl+C during the list animation to skip to the end)[/dim]")
    try:
        list_packages(animate=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]List animation skipped by user.[/yellow]")

    typewriter_effect("\n2. List packages in a specific category:", console)
    console.print("$ lemon list AI", style="cyan")
    list_packages(category_filter="AI", animate=False)

    typewriter_effect("\n3. Install a package (Supports EXE, MSI, MSIX, and Portable):", console)
    console.print("$ lemon install claude-code", style="cyan")
    typewriter_effect("   (This will download and silently run the installer for Claude Code)", console)

    typewriter_effect("\n4. Install a specific version of a package:", console)
    console.print("$ lemon install vscode@1.96.2", style="cyan")
    typewriter_effect("   (Downloads and installs the exact version requested)", console)

    typewriter_effect("\n5. Uninstall a package:", console)
    console.print("$ lemon uninstall 7-zip", style="cyan")
    typewriter_effect("   (This will silently run the uninstaller for 7-zip)", console)

    typewriter_effect("\n6. Check for updates:", console)
    console.print("$ lemon check", style="cyan")
    typewriter_effect("   (Shows a table of packages with newer versions available)", console)

    typewriter_effect("\n7. Upgrade packages interactively:", console)
    console.print("$ lemon upgrade", style="cyan")
    typewriter_effect("   (Prompts to upgrade all or specific outdated packages)", console)

    typewriter_effect("\n8. Sync the package archive:", console)
    console.print("$ lemon update", style="cyan")
    typewriter_effect("   (Fetches the latest package definitions from the remote repo)", console)

    typewriter_effect("\n9. Run a package:", console)
    console.print("$ lemon run vscode", style="cyan")
    typewriter_effect("   (This will attempt to launch the main executable for VS Code)", console)

    typewriter_effect("\n10. List all available categories (with aliases):", console)
    console.print("$ lemon cat", style="cyan")
    list_categories()

    typewriter_effect("\n11. Chat with the AI Assistant (Smart suggestions, fuzzy search):", console)
    console.print("$ lemon chat", style="cyan")
    typewriter_effect("   (Starts an interactive session to manage packages with natural language)", console)

    typewriter_effect("\n12. Show the version of lemon-pm:", console)
    console.print("$ lemon version", style="cyan")
    console.print(f"Lemon Package Manager version {__version__} (status: {__status__})")

    typewriter_effect("\n13. Uninstall the lemon package manager itself:", console)
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
    packages = get_packages()

    categorized_packages = {}
    for name, data in packages.items():
        category = data.get('category', 'Uncategorized')
        if category_filter and category.lower() != category_filter.lower():
            continue
        if category not in categorized_packages:
            categorized_packages[category] = []

        status, local_ver = get_package_status(name)
        status_style = "white"
        if status == "Tracked": status_style = "bold green"
        elif status == "Manual Install": status_style = "bold yellow"

        display_status = status
        if local_ver:
             display_status = f"{status} ({local_ver})"

        version = data.get('version', 'N/A')
        description = data.get('description', 'No description available.')
        categorized_packages[category].append({
            'name': name,
            'version': version,
            'description': description,
            'status': display_status,
            'status_style': status_style
        })

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
            table.add_column("Status", no_wrap=True)
            table.add_column("Description", style="white")

            for pkg in categorized_packages[category]:
                table.add_row(pkg['name'], pkg['version'], f"[{pkg['status_style']}]{pkg['status']}[/]", pkg['description'])
            console.print(table)
    else:
        # Animation mode
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Package", style="green", no_wrap=True)
        table.add_column("Version", style="cyan")
        table.add_column("Status", no_wrap=True)
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
                        table.add_row("---", "---", "---", "---")
                    table.title = f"[bold yellow]{category}[/bold yellow]"
                    current_category = category
                    live.update(table) # Refresh to show the new title
                    time.sleep(0.5)

                for pkg in categorized_packages[category]:
                    table.add_row(pkg['name'], pkg['version'], f"[{pkg['status_style']}]{pkg['status']}[/]", pkg['description'])
                    live.update(table)
                    time.sleep(0.2)

    console.print("End of list.", style="bold white")

def get_lemon_dir():
    """Gets the base directory for Lemon Package Manager data."""
    local_app_data = os.environ.get('LOCALAPPDATA')
    if not local_app_data:
        # Fallback for non-Windows or if env var is missing
        home = os.path.expanduser("~")
        local_app_data = os.path.join(home, '.local', 'share')

    lemon_dir = os.path.join(local_app_data, 'lemon')
    os.makedirs(lemon_dir, exist_ok=True)
    return lemon_dir

def get_portable_bin_dir():
    """Gets the directory for storing portable application binaries."""
    bin_dir = os.path.join(get_lemon_dir(), 'bin')
    os.makedirs(bin_dir, exist_ok=True)
    return bin_dir

def get_state_file():
    """Gets the path to the installed packages state file."""
    return os.path.join(get_lemon_dir(), 'installed.json')

def track_installation(package_name, version):
    """Tracks an installed package and its version."""
    state_file = get_state_file()
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    state[package_name] = {
        'version': version,
        'install_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except OSError as e:
        print(f"Warning: Could not save installation state: {e}")

def untrack_installation(package_name):
    """Removes a package from the tracking state."""
    state_file = get_state_file()
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            if package_name in state:
                del state[package_name]
                with open(state_file, 'w') as f:
                    json.dump(state, f, indent=2)
        except (json.JSONDecodeError, OSError):
            pass

def get_exe_version(filepath):
    """Attempts to get the file version of an executable on Windows."""
    if sys.platform != 'win32' or not os.path.exists(filepath):
        return None
    try:
        # Use PowerShell as a cross-arch reliable way to get file version
        cmd = ['powershell', '-Command', f'(Get-Item "{filepath}").VersionInfo.FileVersion']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        return version if version else None
    except Exception:
        return None

def find_installed_executable(package_data):
    """Finds the path to an installed executable based on package data."""
    package_type = package_data.get('type', 'installer')

    if package_type == 'portable':
        executable_name = package_data.get('executable_name')
        if not executable_name:
            return None
        bin_dir = get_portable_bin_dir()
        path = pathlib.Path(bin_dir) / executable_name
        return str(path) if path.exists() else None

    arches_to_check = []
    if "architectures" in package_data:
        arches_to_check.extend(package_data["architectures"].keys())
    else:
        arches_to_check.append(None)

    for arch_key in arches_to_check:
        package_info = package_data
        if arch_key:
            package_info = package_data["architectures"][arch_key]

        executable = package_info.get('executable', package_data.get('executable'))
        if not executable:
            continue

        uninstall_command = package_info.get('uninstall_command', package_data.get('uninstall_command'))
        if not uninstall_command:
            continue

        if sys.platform == 'win32':
            replacements = {
                '%ProgramFiles%': os.environ.get('ProgramW6432', os.environ.get('ProgramFiles')),
                '%ProgramFiles(x86)%': os.environ.get('ProgramFiles(x86)', os.environ.get('ProgramFiles')),
                '%LocalAppData%': os.environ.get('LOCALAPPDATA'),
                '%AppData%': os.environ.get('APPDATA'),
            }
            for var, val in replacements.items():
                if val:
                    uninstall_command = uninstall_command.replace(var, val)

        try:
            parts = shlex.split(uninstall_command)
            if not parts:
                continue

            uninstaller_path = pathlib.Path(parts[0])
            install_dir = uninstaller_path.parent

            # Sub-sub folder check (e.g. .../Installer/setup.exe)
            if install_dir.name.lower() == 'installer':
                 install_dir = install_dir.parent

            # Potential locations
            search_paths = [
                install_dir / executable,
                install_dir / 'bin' / executable,
                install_dir / 'Application' / executable, # Chrome
            ]

            for path in search_paths:
                if path.exists():
                    return str(path)
        except Exception:
            continue
    return None

def is_installed(package_name):
    """Checks if a package is installed by checking for the executable."""
    packages = get_packages()

    if package_name not in packages:
        return False

    return find_installed_executable(packages[package_name]) is not None

def get_package_status(package_name):
    """Returns detailed installation status of a package."""
    # Check if tracked by LPM
    state_file = get_state_file()
    tracked_version = None
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                tracked_version = state.get(package_name, {}).get('version')
        except (json.JSONDecodeError, OSError):
            pass

    packages = get_packages()

    if package_name not in packages:
        return "Not in package list", None

    exe_path = find_installed_executable(packages[package_name])

    if exe_path:
        if tracked_version:
            return "Tracked", tracked_version
        else:
            # Found on disk but not in installed.json
            found_version = get_exe_version(exe_path)
            return "Manual Install", found_version or "Unknown"

    return "Not Installed", None


def _install_package_with_arch(package_name, package_data, arch):
    """Helper function to install a package for a specific architecture."""
    version = package_data['version']
    package_type = package_data.get('type', 'installer')

    if "architectures" in package_data:
        if arch not in package_data["architectures"]:
            print(f"'{arch}-bit' architecture not available for '{package_name}'.")
            return False
        arch_data = package_data["architectures"][arch]
        url = arch_data['url']
        install_command = arch_data.get('install_command', [])
    else:
        url = package_data['url']
        install_command = package_data.get('install_command', [])

    print(f"Attempting to install {package_name} version {version} ({arch}-bit)...")

    try:
        headers = {
            'User-Agent': f'LemonPackageManager/{__version__}'
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        # Validation: Ensure we are not downloading an HTML page (e.g., a mirror's error page or bot detection)
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            print(f"\nERROR: The download URL returned an HTML page instead of a binary file.")
            print(f"URL: {url}")
            print("This can happen if the version is no longer available on the mirror or if the request was blocked.")
            return False

        filename = url.split('/')[-1]
        temp_dir = tempfile.gettempdir()
        temp_filepath = os.path.join(temp_dir, filename)

        total_size = int(response.headers.get('content-length', 0))
        with open(temp_filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                done = int(50 * downloaded / total_size) if total_size else 0
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes")
                sys.stdout.flush()
        sys.stdout.write('\n')

        if total_size and downloaded < total_size:
            print(f"\nERROR: Download incomplete. Expected {total_size} bytes, got {downloaded} bytes.")
            return False

        print(f"Downloaded '{filename}'.")
        os.chmod(temp_filepath, 0o755)

        if package_type == 'installer':
            if temp_filepath.endswith('.msi'):
                command = ['msiexec', '/i', temp_filepath] + install_command
            elif temp_filepath.endswith('.msix') or temp_filepath.endswith('.msixbundle'):
                command = ['powershell', '-Command', f'Add-AppxPackage -Path "{temp_filepath}"']
            else:
                command = [temp_filepath] + install_command

            subprocess.run(command, check=True, capture_output=True, text=True, shell=False)
            print(f"Successfully installed {package_name} version {version}.")
            track_installation(package_name, version)
            return True
        elif package_type == 'portable':
            bin_dir = get_portable_bin_dir()
            executable_name = package_data.get('executable_name', filename)
            final_filepath = os.path.join(bin_dir, executable_name)
            os.makedirs(os.path.dirname(final_filepath), exist_ok=True)

            if temp_filepath.endswith('.zip'):
                print(f"Extracting {filename} to {bin_dir}...")
                with zipfile.ZipFile(temp_filepath, 'r') as zip_ref:
                    # Security Check: Zip Slip protection
                    for member in zip_ref.namelist():
                        member_path = os.path.join(bin_dir, member)
                        if not os.path.abspath(member_path).startswith(os.path.abspath(bin_dir)):
                             print(f"ERROR: Potential Zip Slip vulnerability detected in {filename}. Extraction aborted.")
                             return False

                    # Check if all files are under a single top-level directory
                    members = zip_ref.namelist()
                    top_level_dirs = {m.split('/')[0] for m in members if '/' in m}
                    only_files_in_root = all('/' not in m for m in members if not m.endswith('/'))

                    zip_ref.extractall(bin_dir)

                    # If everything is in a single subfolder, move it up to flatten
                    if not only_files_in_root and len(top_level_dirs) == 1:
                        top_dir = list(top_level_dirs)[0]
                        top_dir_path = os.path.join(bin_dir, top_dir)
                        if os.path.isdir(top_dir_path):
                            for item in os.listdir(top_dir_path):
                                shutil.move(os.path.join(top_dir_path, item), os.path.join(bin_dir, item))
                            try:
                                os.rmdir(top_dir_path)
                            except OSError:
                                pass # Directory not empty or other issue

                if os.path.exists(final_filepath):
                    os.chmod(final_filepath, 0o755)
                else:
                    # Fallback: search for the executable if not in the expected path
                    base_exe = os.path.basename(executable_name)
                    for root, dirs, files in os.walk(bin_dir):
                        if base_exe in files:
                            source_path = os.path.join(root, base_exe)
                            if source_path != final_filepath:
                                shutil.move(source_path, final_filepath)
                            os.chmod(final_filepath, 0o755)
                            break
            else:
                if os.path.exists(final_filepath):
                    os.remove(final_filepath)
                os.rename(temp_filepath, final_filepath)
                os.chmod(final_filepath, 0o755)

            print(f"Successfully installed {package_name} version {version} to {final_filepath}")
            track_installation(package_name, version)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Installation failed for {arch}-bit architecture.")
        # Re-raise the specific error to be caught by the calling function
        raise e
    except (requests.exceptions.RequestException, FileNotFoundError, PermissionError, OSError) as e:
        print(f"An error occurred during installation: {e}")
        return False
    finally:
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            print("Cleaning up...")
            os.remove(temp_filepath)
    return False

def install_package(package_name, from_chat=False, target_version=None):
    """Downloads and installs a package, with fallback for architecture."""
    if sys.platform == 'win32' and not is_admin():
        print("ERROR: Administrator privileges are required to install packages.")
        sys.exit(1)

    packages = get_packages()

    # Handle package@version syntax
    if not target_version and '@' in package_name:
        package_name, target_version = package_name.split('@', 1)

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]

    if target_version:
        if target_version == package_data.get('version'):
            # Already set to use latest version details
            pass
        elif "versions" in package_data and target_version in package_data["versions"]:
            # Use specific version data, but merge with base package metadata (category, type, etc.)
            base_data = package_data.copy()
            version_specific_data = base_data.pop("versions")[target_version]
            base_data.update(version_specific_data)
            base_data['version'] = target_version
            package_data = base_data
        else:
            print(f"Version '{target_version}' not found for '{package_name}'.")
            available_versions = [package_data.get('version')] + list(package_data.get('versions', {}).keys())
            print(f"Available versions: {', '.join(filter(None, available_versions))}")
            return

    if is_installed(package_name):
        state_file = get_state_file()
        current_version = None
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    current_version = state.get(package_name, {}).get('version')
            except (json.JSONDecodeError, OSError):
                pass

        # If target_version is specified and different from current, or if it's an upgrade, allow installation
        if target_version and current_version and target_version == current_version:
            print(f"'{package_name}' version {target_version} is already installed.")
            return
        elif not target_version and current_version == package_data.get('version'):
            print(f"'{package_name}' is already at the latest version ({current_version}).")
            return
        elif not current_version:
             # Manual install detected
             print(f"'{package_name}' was installed manually (LPM version untracked).")
             print(f"To manage it with LPM, we will install the requested version ({target_version or package_data.get('version')}).")
             confirmation = input("Proceed? (y/n): ")
             if confirmation.lower() != 'y':
                  return
        else:
            print(f"Software '{package_name}' found. Proceeding with version change/upgrade ({current_version} -> {target_version or package_data.get('version')})...")

    if "architectures" in package_data:
        is_64bit_os = sys.maxsize > 2**32

        if is_64bit_os and "64" in package_data["architectures"]:
            try:
                if _install_package_with_arch(package_name, package_data, "64"):
                    return
            except (subprocess.CalledProcessError, OSError) as e:
                # This specific error code can indicate a 64-bit app on a 32-bit OS
                # WinError 216: This version of %1 is not compatible with the version of Windows you're running.
                win_err = getattr(e, 'winerror', None)
                if win_err == 216 and "32" in package_data["architectures"]:
                    print("64-bit installation failed (Architecture mismatch), attempting 32-bit fallback.")
                    if _install_package_with_arch(package_name, package_data, "32"):
                        return
                else:
                    print(f"64-bit installation failed: {e}")

        # If 64-bit failed or wasn't attempted, try 32-bit
        if "32" in package_data["architectures"]:
            try:
                if _install_package_with_arch(package_name, package_data, "32"):
                    return
            except (subprocess.CalledProcessError, OSError) as e:
                 print(f"32-bit installation also failed: {e}")
    else:
        # For packages without specified architectures
        try:
            if _install_package_with_arch(package_name, package_data, "N/A"):
                return
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Installation failed for {package_name}: {e}")

    print(f"Could not install {package_name}.")

def run_package(package_name):
    """Launches a package's main executable."""
    packages = get_packages()

    if package_name not in packages:
        print(f"Package '{package_name}' not found.")
        return

    package_data = packages[package_name]

    try:
        executable_path = find_installed_executable(package_data)
        if not executable_path:
            print(f"Error: Could not find installed executable for '{package_name}'.")
            print("Make sure the package is installed and its path is correct.")
            return

        print(f"Launching '{package_name}' from '{executable_path}'...")
        # Use Popen to launch the process in the background without blocking the terminal.
        subprocess.Popen([executable_path], shell=False)

    except Exception as e:
        print(f"An error occurred while trying to run {package_name}: {e}")
        print("Note: The 'run' command relies on heuristics to find the executable and may not work for all packages.")

def uninstall_package(package_name, from_chat=False):
    """Uninstalls a package using its uninstall command, or provides instructions."""
    status, ver = get_package_status(package_name)
    if status == "Not Installed":
         print(f"Package '{package_name}' is not installed.")
         return
    elif status == "Manual Install":
         print(f"Warning: '{package_name}' was installed manually (LPM version untracked).")
         print("LPM will attempt to run its built-in uninstaller.")
         if input("Proceed? (y/n): ").lower() != 'y':
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

    packages = get_packages()

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
                untrack_installation(package_name)
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
                untrack_installation(package_name)
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


def check_for_updates(quiet=False):
    """Checks for available updates and returns a list of packages that can be upgraded."""
    state_file = get_state_file()
    if not os.path.exists(state_file):
        if not quiet: print("No packages tracked for upgrade. Use 'lemon install' to install packages first.")
        return []

    try:
        with open(state_file, 'r') as f:
            installed_packages = json.load(f)
    except (json.JSONDecodeError, OSError):
        if not quiet: print("Error reading installation state.")
        return []

    available_packages = get_packages()
    updates = []

    for name, data in installed_packages.items():
        if name not in available_packages:
            continue

        current_version = data.get('version')
        latest_version = available_packages[name].get('version')

        if latest_version and latest_version != "latest" and latest_version != current_version:
            updates.append({
                'name': name,
                'current': current_version,
                'latest': latest_version
            })

    return updates

def check_updates():
    """Checks for and displays available updates."""
    updates = check_for_updates()
    if not updates:
        print("All tracked packages are already up to date.")
        return

    print("Available updates:")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Package", style="green")
    table.add_column("Current Version", style="yellow")
    table.add_column("Latest Version", style="cyan")

    for up in updates:
        table.add_row(up['name'], up['current'], up['latest'])

    console = Console()
    console.print(table)
    print("\nRun 'lemon upgrade' to install these updates.")

def upgrade_package(package_name=None):
    """Upgrades a specific package or all installed packages interactively."""
    available_packages = get_packages()
    state_file = get_state_file()

    try:
        with open(state_file, 'r') as f:
            installed_packages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        installed_packages = {}

    if package_name:
        status, ver = get_package_status(package_name)
        if status == "Tracked":
            latest = available_packages[package_name].get('version')
            if latest == "latest":
                 print(f"Re-installing {package_name} to ensure latest version...")
                 install_package(package_name)
            elif latest != ver:
                 print(f"Upgrading {package_name}: {ver} -> {latest}")
                 install_package(package_name)
            else:
                 print(f"{package_name} is already up to date ({ver}).")
        elif status == "Manual Install":
            print(f"Package '{package_name}' was installed manually (Version: {ver}).")
            if input("Would you like LPM to adopt and upgrade it? (y/n): ").lower() == 'y':
                 install_package(package_name)
        else:
            print(f"Package '{package_name}' is not installed.")
        return

    # Bulk Upgrade Flow
    updates = check_for_updates(quiet=True)

    if not updates:
        print("All tracked packages are already up to date.")
        # Check for manual installs anyway to be helpful
        manual_installs = []
        for name in available_packages:
            if name not in installed_packages:
                status, ver = get_package_status(name)
                if status == "Manual Install":
                    manual_installs.append((name, ver))

        if manual_installs:
            print("\nFound manual installations that LPM can manage:")
            for name, ver in manual_installs:
                print(f"- {name} (Version: {ver})")
            print("Use 'lemon upgrade <name>' to adopt any of these.")
        return

    print("Available updates:")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Package", style="green")
    table.add_column("Current Version", style="yellow")
    table.add_column("Latest Version", style="cyan")

    for up in updates:
        table.add_row(up['name'], up['current'], up['latest'])

    console = Console()
    console.print(table)

    choice = input("\nUpgrade all? (y) / Upgrade specific? (s) / Cancel (n): ").lower()

    if choice == 'y':
        for up in updates:
            print(f"\n--- Upgrading {up['name']} ---")
            install_package(up['name'])
    elif choice == 's':
        pkg = input("Enter package name to upgrade: ").strip()
        if pkg in [u['name'] for up in updates]:
             install_package(pkg)
        else:
             print("Invalid selection or package not in update list.")

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
    packages = get_packages()

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

    # 'upgrade' command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade a package or all packages interactively')
    upgrade_parser.add_argument('package_name', nargs='?', default=None, help='The name of the package to upgrade (optional)')

    # 'check' command
    check_parser = subparsers.add_parser('check', help='Check for available updates')

    # 'update' command
    update_parser = subparsers.add_parser('update', help='Sync the package archive with remote repository')

    # 'self-update' command
    self_update_parser = subparsers.add_parser('self-update', help='Update the lemon package manager itself')

    # 'list' command
    list_parser = subparsers.add_parser('list', help='List available packages, optionally filtered by category')
    list_parser.add_argument('category', nargs='?', default=None, help='The category to filter by')

    # 'categories' command
    categories_parser = subparsers.add_parser('categories', aliases=['cat', 'cats'], help='List all available package categories')

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
    elif args.command == 'upgrade':
        upgrade_package(args.package_name)
    elif args.command == 'check':
        check_updates()
    elif args.command == 'update':
        sync_archive()
    elif args.command == 'self-update':
        self_update()
    elif args.command == 'run':
        run_package(args.package_name)
    elif args.command == 'list':
        list_packages(args.category)
    elif args.command in ['categories', 'cat', 'cats']:
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
