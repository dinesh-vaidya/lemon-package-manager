# lemon package manager 🍋

![version](https://img.shields.io/badge/version-1.0.0-blue) ![status](https://img.shields.io/badge/status-beta-orange)

A simple, command-line package manager for Windows devices.

## Status

This project is currently in **Beta**. It is functional but may contain bugs and is undergoing active development.

## Features

-   List available software packages.
-   Install packages from a predefined list of direct download URLs.
-   Provides instructions for uninstalling packages.
-   Simple and lightweight.

## Setup

### Prerequisites

-   **Python**: You must have Python installed on your system to use this tool. The `pip` command is included with modern Python installations. You can download Python from [python.org](https://www.python.org/downloads/).

### Installation

1.  Clone this repository.
2.  Navigate to the project directory.
3.  Install the package using pip:
    ```bash
    pip install .
    ```
    This will install the necessary dependencies and add the `lemon` command to your system's PATH.

## Usage

Once installed, you can use the `lemon` command from anywhere in your terminal.

### List available packages

To see a list of all packages that can be installed, use the `list` command:

```bash
lemon list
```

### Install a package

To install a package, use the `install` command followed by the package name:

```bash
lemon install notepad++
```

The script will download the installer and simulate running it.

### Uninstall a package

To get instructions on how to uninstall a package, use the `uninstall` command:

```bash
lemon uninstall notepad++
```
This will provide you with the steps to remove the application using the standard Windows "Add or Remove Programs" feature.

## Available Packages

The following packages are currently available for installation, grouped by category:

### Browsers
-   chrome
-   firefox
-   opera

### Communication
-   discord
-   slack
-   telegram
-   zoom

### Development
-   vscode
-   git
-   jdk
-   notepad++

### Gaming
-   epic-games-launcher
-   minecraft-launcher

### Media & Creativity
-   vlc
-   gimp
-   obs-studio
-   audacity
-   blender
-   spotify

### Productivity
-   libreoffice
-   notion

### Utilities
-   7-zip
-   winrar
-   greenshot
-   cpu-z
-   qbittorrent

### Virtualization
-   virtualbox

You can add more packages by editing the `packages.json` file.
