# lemon package manager 🍋

![version](https://img.shields.io/badge/version-1.1.2-blue) ![status](https://img.shields.io/badge/status-beta-orange) ![license](https://img.shields.io/badge/license-MIT-green)

A simple, command-line package manager for Windows devices, designed to quickly install popular applications from the terminal.

## Features

-   **Install Packages:** Silently installs packages from a predefined list of trusted URLs. Supports EXE, MSI, MSIX, and Portable applications.
-   **Uninstall Packages:** Silently uninstalls packages using robust, version-agnostic methods.
-   **Run Applications:** Launch installed applications directly from the terminal.
-   **Categorized Package List:** View all available software, neatly grouped by category, with real-time installation status.
-   **AI Tools Support:** Native support for modern AI tools like Claude, GPT4All, and Jan.
-   **AI Chat Assistant:** Manage packages using natural language with built-in smart suggestions, fuzzy search, and a friendly personality.
-   **Software Detection:** Automatically detects software already installed on your system, even if not installed via LPM.
-   **External Management:** LPM can 'adopt' manually installed software to handle future upgrades and uninstalls.
-   **Administrator Check:** Automatically detects if administrator privileges are needed and provides clear instructions.
-   **Simple and Lightweight:** No complex dependencies or configuration required.

## Development Note (Sandbox Context)

The Lemon Package Manager is currently being developed in a **May 2026** sandbox environment. As such, software versions and download URLs in `packages.json` reflect the verified stable releases available as of May 2026 (e.g., Python 3.14.5, 7-Zip 26.01, VLC 3.0.23). These "futuristic" versions are intentionally included for development and testing within this timeframe.

## Installation

### Prerequisites

-   **Python**: You must have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
-   **Administrator Privileges**: To install and uninstall software, you must run the `lemon` (or `lpm`) command from a terminal with administrator privileges (e.g., Command Prompt or PowerShell run as Administrator).

### Steps

1.  Clone this repository.
2.  Navigate to the project directory.
3.  Run the `install.bat` script by double-clicking it or running it from your terminal.
    ```bash
    install.bat
    ```
    This will install the necessary dependencies and add the `lemon` and `lpm` commands to your system's PATH.

## Usage

Once installed, you can use the `lemon` (or `lpm`) command from anywhere in your terminal. Both commands are interchangeable. For `install` and `uninstall` commands, ensure you are running your terminal as an Administrator.

---

### `lemon list [category]` or `lpm list [category]`

To see a list of all packages. You can optionally filter the list by providing a category name.

```bash
# Show all packages
lemon list

# Show only packages in the 'Development' category
lpm list Development
```

### `lemon categories` or `lpm categories` (Aliases: `cat`, `cats`)

To see a list of all available package categories.

```bash
# Example
lemon categories

# Using aliases
lpm cat
lpm cats
```

### `lemon install <package_name>[@version]` or `lpm install <package_name>[@version]`

To install a package, use the `install` command. You can optionally specify a version using the `@version` syntax. If no version is specified, the latest available version will be installed.

```bash
# Install the latest version
lpm install notepad++

# Install a specific version
lpm install notepad++@8.8.4
```

### `lemon check` or `lpm check`

Checks all your tracked packages against the archive list and displays a table of available updates.

```bash
# Check for updates
lpm check
```

### `lemon upgrade [package_name]` or `lpm upgrade [package_name]`

To upgrade your installed packages to the latest available versions. Running `upgrade` without a package name will show a summary of all available updates and prompt you to upgrade "All", a "Specific" package, or "None".

```bash
# Interactive bulk upgrade
lemon upgrade

# Directly upgrade a specific package
lpm upgrade vlc
```

### `lemon update` or `lpm update`

Syncs your local package archive with the remote repository efficiently using HTTP caching headers (only downloads if changed).

```bash
# Sync package archive
lemon update
```

### `lemon self-update` or `lpm self-update`

Efficiently updates the Lemon Package Manager tool itself by downloading and replacing core source files only if they have changed.

```bash
# Update the package manager
lemon self-update
```

### `lemon uninstall <package_name>` or `lpm uninstall <package_name>`

To uninstall a package, use the `uninstall` command.

```bash
# Example
lemon uninstall notepad++
```

### `lemon run <package_name>` or `lpm run <package_name>`

To launch an installed application, use the `run` command. This will start the application's main executable.

*Note: This command relies on finding the executable in the standard installation path and may not work for all packages.*

```bash
# Example
lpm run notepad++
```

### `lemon version` or `lpm version`

To see the current version of the `lemon-pm` tool.

```bash
# Example
lemon version
# Output: Lemon Package Manager version 1.1.2 (status: beta)
```

### `lemon help` or `lpm help`

To see the list of all available commands and their descriptions.

```bash
# Example
lpm help
```

### `lemon demo` or `lpm demo`

To see a live demonstration of all the available commands. This command provides a guided tour of the package manager's features with animated text and tables.

```bash
# Example
lpm demo
```

### `lemon chat` or `lpm chat`

Starts an interactive chat session with an AI assistant to help you manage packages. The chat interface is colorful and easy to use, with a typewriter effect for the assistant's messages.

You can use the following commands in the chat:
- `list`: Show all available packages.
- `search <package_name>`: Search for a specific package.
- `install <package_name>[@version]`: Install a specific version.
- `check`: Check for available updates.
- `upgrade [package_name]`: Upgrade a specific or all packages.
- `update`: Sync the package archive with remote repository.
- `info <package_name>`: Get more information about a package.
- `uninstall <package_name>`: Uninstall a package.
- `exit`: Close the chat session.

The assistant also has some smart features:
- **Smart Suggestions**: If you ask for a category (e.g., "browser" or "AI"), the assistant will suggest relevant packages from that category.
- **Fuzzy Search & Command Aliases**: Understands natural language variations like "get", "add", "find", and "remove", and catches common misspellings.
- **Help System**: Type "help" within the chat to see a structured overview of available features.
- **Package Count**: You can ask "how many packages are there?" to get the total count.
- **Conversational**: Responds politely to greetings and affirmations with a friendly personality.

```bash
# Example
lpm chat
```

### `lemon uninstall-lpm` or `lpm uninstall-lpm`

To uninstall the lemon package manager itself. This will remove the `lemon` and `lpm` commands from your system.

```bash
# Example
lpm uninstall-lpm
```

## Supported Package Types

Lemon Package Manager supports several types of Windows applications:
-   **EXE (Inno Setup, NSIS, etc.)**: Standard installers with silent flags.
-   **MSI**: Windows Installer packages.
-   **MSIX / MSIXBUNDLE**: Modern Windows application packages.
-   **Portable**: Single-executable or ZIP-archived applications that don't require formal installation.

## Available Packages

To see a full, categorized list of all available packages, use the `list` command:
```bash
lemon list
```
You can add more packages by editing the `lemon_pm/packages.json` file in the source code.

---

## License

This project is licensed under the MIT License.

**MIT License**

Copyright (c) 2025 Priyanka

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
