# lemon 🍋

A simple, command-line package manager for Windows devices.

## Features

-   List available software packages.
-   Install packages from a predefined list of direct download URLs.
-   Provides instructions for uninstalling packages.
-   Simple and lightweight.

## Setup

1.  Clone this repository.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The script is run from the command line and has several commands.

### List available packages

To see a list of all packages that can be installed, use the `list` command:

```bash
python lemon.py list
```

### Install a package

To install a package, use the `install` command followed by the package name:

```bash
python lemon.py install notepad++
```

The script will download the installer and simulate running it.

### Uninstall a package

To get instructions on how to uninstall a package, use the `uninstall` command:

```bash
python lemon.py uninstall notepad++
```
This will provide you with the steps to remove the application using the standard Windows "Add or Remove Programs" feature.

## Available Packages

The following packages are currently available for installation:

-   7-zip
-   notepad++
-   vlc
-   greenshot

You can add more packages by editing the `packages.json` file.
