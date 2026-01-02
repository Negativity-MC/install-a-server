# Minecraft Server Setup Utility

A powerful, interactive CLI tool to easily set up PaperMC and PurpurMC servers. This utility handles everything from version selection to downloading, EULA agreement, and creating optimized start scripts with Aikar's flags.

## Features

- **Multi-Software Support**: Choose between [PaperMC](https://papermc.io/) and [PurpurMC](https://purpurmc.org/).
- **Interactive TUI**: User-friendly terminal interface using `rich` and `inquirer` (i am too lazy to learn textual).
- **Automatic Version Fetching**: Queries the official APIs to get the latest available Minecraft versions and builds.
- **Automated Setup**:
  - Downloads the server JAR file.
  - Auto-agrees to the Mojang EULA.
  - Checks for a valid Java Runtime Environment.
- **Optimized Start Script**:
  - Option to generate a `start.sh` script.
  - Pre-configured with **Aikar's Flags** for optimal performance.
  - Customizable RAM allocation.

## Prerequisites

- Python 3.6+
- Java (JRE/JDK) installed and available in your system's PATH (required to run the server).

## Installation

1. Clone or download this repository.
2. Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the utility with Python:

```bash
python3 main.py
```

### Walkthrough

1. **Select Software**: Choose between Paper or Purpur.
2. **Select Version**: Pick the Minecraft version you want to play.
3. **Confirm Download**: The utility will fetch the latest build for that version.
4. **EULA**: Agree to the EULA to proceed.
5. **Java Check**: The tool will verify if Java is installed.
6. **Start Script**: You can choose to create a `start.sh` with Aikar's flags and set your RAM (e.g., `4G`).
7. **Launch**: Start the server immediately or exit and run `start.sh` later.

## License

This project is open-source and available under the MIT License.

## TODO

Abuse something like PyInstaller/Nuitka to package this in to a UNIX exacutable.