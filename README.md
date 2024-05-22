# GenshinRichPresence

[![pt-br](https://img.shields.io/badge/lang-pt--br-green
)](https://github.com/Artprozew/GenshinRichPresence/blob/main/README.pt-br.md)

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

## Overview

This program lets your friends on Discord see what you're up to in Genshin Impact!

This is a Discord Rich Presence program for Genshin Impact that works by analyzing GIMI's log file in real-time to determine the current game status, updating your Discord game activity accordingly.

![image][example1]
![image][example2]

### Why do it this way?

You're right, accessing game information this way may not be the most elegant solution. Ideally, Genshin Impact would directly share your activity with Discord.
But this method is currently one of the few ways to get in-game information without changing the game files itself. Since it works as expected and doesn't alter the game, it's a practical solution.

### Is it safe?

Yes, this program is considered safe. It just reads a log file generated by GIMI, and does not modify any game files, so there's no risk of harming your game or your computer.

## Required

- [GIMI][GIMI] with mods
- [Python][Python]
- [Poetry][Poetry] is recommended

## Installation

- Download or clone the repository (with `git clone https://github.com/Artprozew/GenshinRichPresence.git`)
- Go inside the project directory, right click on a blank space and click "open Command Prompt"
- Run `python -m pip install -r requirements.txt` OR
- Run `poetry install` if you're using Poetry

## How to use

- You should set the path to your GIMI on the `GIMI_DIRECTORY` environment variable. I suggest that you create a `.env` file in the project's root directory and write the path to your GIMI there. e.g.: `GIMI_DIRECTORY="C:\Programs\3dmigoto"`
- Open GIMI with Genshin Impact
- Open a command prompt on your project's root directory.
- Run the `main.py` file inside the `src` folder (`python src/main.py`)
- Your activity must now be visible on your Discord profile, have fun!

## Known issues

Although still under development, this method is not perfect and may have limitations. But keep in mind that it does work as expected **most of the time**.
Some of the issues listed below may be fixed or worked around in the future. The problems observed are:

- When you first launch the program, it might not detect your current character/region until you switch your character or walk/teleport to another place.
- Occasionally, especially during teleports, the program might display an incorrect character. This issue can also be fixed when you switch characters.
- When there's more than one playable character on screen, the program can also struggle to detect your character (e.g.: Multiplayer or cutscenes).
- Some regions might not be displayed correctly.
- Due to the program relying on analyzing hashes, some information might be incorrect at times. These hashes may be wrong or outdated.
- Character mods for GIMI are currently required for the program to detect your characters.

### Credits

The region data/hashes was extracted from [golanah921's][golanah921] Region.ini

[example1]: https://github.com/Artprozew/GenshinRichPresence/assets/33605982/1f428371-d880-4783-802d-93f9526af002
[example2]: https://github.com/Artprozew/GenshinRichPresence/assets/33605982/1a78f6af-5cda-48e2-849a-da2f7b75c113
[GIMI]: https://github.com/SilentNightSound/GI-Model-Importer
[Python]: https://www.python.org/downloads/release/python-3123
[Poetry]: https://python-poetry.org/docs/#installing-with-the-official-installer
[golanah921]: https://gamebanana.com/tools/15459
