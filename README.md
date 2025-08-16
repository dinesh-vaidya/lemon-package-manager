# lemon 🍋

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

The following packages are currently available for installation:

-   7-zip
-   audacity
-   blender
-   chrome
-   cpu-z
-   discord
-   epic-games-launcher
-   firefox
-   gimp
-   git
-   greenshot
-   jdk
-   libreoffice
-   minecraft-launcher
-   notepad++
-   obs-studio
-   qbittorrent
-   slack
-   spotify
-   telegram
-   vlc
-   vscode
-   winrar
-   zoom

You can add more packages by editing the `packages.json` file.
