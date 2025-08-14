# lemon 🍋

A simple, command-line package manager for Windows devices.

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
-   notepad++
-   vlc
-   greenshot

You can add more packages by editing the `packages.json` file.
