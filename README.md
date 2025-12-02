# lemon package manager 🍋

![version](https://img.shields.io/badge/version-1.1.0-blue) ![status](https://img.shields.io/badge/status-beta-orange) ![license](https://img.shields.io/badge/license-MIT-green)

A simple, command-line package manager for Windows devices, designed to quickly install popular applications from the terminal.

## Features

-   **Install Packages:** Silently installs packages from a predefined list of trusted URLs.
-   **Uninstall Packages:** Silently uninstalls packages.
-   **Run Applications:** Launch installed applications directly from the terminal.
-   **Categorized Package List:** View all available software, neatly grouped by category.
-   **Administrator Check:** Automatically detects if administrator privileges are needed and provides clear instructions.
-   **Simple and Lightweight:** No complex dependencies or configuration required.

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

### `lemon categories` or `lpm categories`

To see a list of all available package categories.

```bash
# Example
lemon categories
```

### `lemon install <package_name>` or `lpm install <package_name>`

To install a package, use the `install` command followed by the package name. The installer will be downloaded and run silently in the background.

```bash
# Example
lpm install notepad++
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

### `lemon uninstall-lpm` or `lpm uninstall-lpm`

To uninstall the lemon package manager itself. This will remove the `lemon` and `lpm` commands from your system.

```bash
# Example
lpm uninstall-lpm
```

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
