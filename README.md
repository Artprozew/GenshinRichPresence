# GenshinRichPresence

![GitHub top language](https://img.shields.io/github/languages/top/Artprozew/GenshinRichPresence?style=for-the-badge)
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)
![GitHub branch check runs](https://img.shields.io/github/check-runs/Artprozew/GenshinRichPresence/master?style=for-the-badge)

## Overview

**Show your friends on Discord what you're up to in Genshin Impact!**

This is a **Discord Rich Presence** program for **Genshin Impact** that works by analyzing **GIMI**'s log file in real-time to determine the current game status, **updating your Discord game activity accordingly**.

![image][example1]
![image][example2]

### Why do it this way?

You're right, accessing game information through GIMI's log file might not be the **most** elegant solution. Ideally, the game would directly share your activity with Discord.
But this method is currently **one of the few ways** to get in-game information like this **without changing the game files** itself. Additionally, this method **doesn't use OCR** (Optical Character Recognition) at all, which makes it potentially even **more performant**.

### Is it safe?

Yes, this program is considered safe. It just reads a log file generated by GIMI, and **does not modify any game files**, so there's no risk of harming your game or your computer.

## Running the Executable

The pre-built executable is a convenient option for **users** who want to **avoid installing Python**.
However, anti-virus **might** flag the .exe incorrectly as a "virus", you can check the [Anti-Virus Disclaimer](#anti-virus-disclaimer) and [Virus Total][Virus Total].

### Prerequisites

- Download and extract the zipped file from [Releases][releases].
- Have [GIMI][GIMI] set-up.

### Instructions

1. Open the `config.ini` file on the project root folder and set the required paths on the **Essential Settings** section.
2. Run the executable, and if anything goes right, an icon will appear on your **system tray**.
3. Your activity must now be visible on your Discord profile, have fun!

## Running from Source Code

This method is suitable for users **familiar with Python** or **encountering issues with the executable**.

### Prerequisites

- Have [GIMI][GIMI] set-up.
- [Python 3.9+][Python] (Python already comes with [pip][pip] installed, but [Poetry][Poetry] is recommended).

### Installation

> [!TIP]
> (Optional) If you want to install the developer dependencies, you can append `--group=dev` to the `poetry install` command.

1. [Download][GH Download] and extract the repository (or just [clone][GH Clone] it).
2. Open the project folder, right click on a blank space and click "open Command Prompt/Terminal".
3. **Install dependencies** using the command for either pip (`python -m pip install -r requirements.txt`) or Poetry (`poetry install`).

### Instructions

See above [Instructions](#instructions), for step 2 you can instead:
- Open a command prompt on the project root directory and run the command `pythonw src/main.py`. You could also save a `.bat` file with that command if you want.
- Alternatively, you can run the `main.py` file inside the `src` folder by double-clicking, but it will also bring up the unwanted **command prompt**, rename the `main.py` to `main.pyw` if you don't want that to happen.

## Common Knowledge

When the program starts, it will **stay hidden** on your **system tray**, and will wait your game to open **within 60 seconds**, if it doesn't find it or if you close your game, the **program will also close itself**.

If any **error** occurs, the program may exit by itself, and will write the error on the `traceback.txt` file.

## Known issues

Although still under development, this method is not perfect and may have limitations. But keep in mind that it does work as expected **most of the time**.
Some of the issues described here may be fixed or worked around in the future. The problems observed are:

- When you start the game, it might not detect your current character/region **until you switch your character** or **walk/teleport** to another place.
- Occasionally, especially during **teleports**, the program might display an incorrect character. This issue can also be fixed when you switch characters. ([#17][#17])
- When there's **more than one playable character** on screen, the program can also struggle to detect your character correctly (e.g.: Multiplayer or cutscenes).
- Due to the program relying on analyzing **hashes**, some information might be incorrect at times. These hashes may be wrong or outdated. ([#27][#27])

## Disclaimer

GenshinRichPresence is an **unofficial third-party** application and is not affiliated with HoYoverse in any way. It is developed and maintained independently.

### Anti-Virus Disclaimer

Some anti-virus software (Windows Defender or similar) might flag the executable as a potential threat due to overly cautious heuristics. This is a known issue called **"false positive"**, especially considering the program is built from **Python** code.

Python is a widely used and well-established programming language known for its security. However, anti-virus software might sometimes **misinterpret** the behavior of programs created with Python. See: [Windows Defender false positives][Windows Defender]

If you're confident the program is safe, you can [add an exclusion][WinDefender Exclusion] for the program's executable file in your anti-virus software settings. This will **prevent** it from being flagged in the future.

We assure you that the program is **entirely safe** and does not contain any malicious code. If you encounter any issues running the program from the downloaded executable file, you can try [running from source code](#running-from-source-code)

## Contributing

There's still a lot to do, if you want to contribute, fork the repo, submit pull requests, or share any bug fixes or feature ideas you have, **you're much welcome!**

## Licensing

This project is licensed under MIT license; Refer to: [LICENSE][LICENSE]

## Credits

- Region data/hashes extracted from [golanah921's][golanah921] Region.ini
- Temporary app icon image (used as a placeholder icon) by [@KisekiHikari][KisekiHikari] on Twitter

[example1]: https://github.com/Artprozew/GenshinRichPresence/assets/33605982/08c95c5a-fb3f-44b1-9b19-f5dadb1e7bbb
[example2]: https://github.com/Artprozew/GenshinRichPresence/assets/33605982/dd0f965b-8c63-4210-a9c0-74097e68c612

[releases]: https://github.com/Artprozew/GenshinRichPresence/releases
[Virus Total]: https://www.virustotal.com/gui/file/c7d8a13a40c789618c9fe1dbb0bd25b6f46b66be19fc37b1b48dcb64beb496c7

[GIMI]: https://github.com/SilentNightSound/GI-Model-Importer
[Region.ini]: https://github.com/leotorrez/LeoTools/blob/main/releases/Region.ini
[Python]: https://www.python.org/downloads/release/python-3123
[pip]: https://pip.pypa.io/en/stable/installation/
[Poetry]: https://python-poetry.org/docs/#installing-with-the-official-installer
[GH Download]: https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives
[GH Clone]: https://docs.github.com/pt/repositories/creating-and-managing-repositories/cloning-a-repository?platform=windows

[golanah921]: https://gamebanana.com/tools/15459
[KisekiHikari]: https://x.com/KisekiHikari

[#17]: https://github.com/Artprozew/GenshinRichPresence/issues/17
[#27]: https://github.com/Artprozew/GenshinRichPresence/issues/27

[Windows Defender]: https://www.reddit.com/r/techsupport/comments/of8vph/windows_defender_identified_my_own_program_as/
[WinDefender Exclusion]: https://support.microsoft.com/en-us/windows/add-an-exclusion-to-windows-security-811816c0-4dfd-af4a-47e4-c301afe13b26

[LICENSE]: https://github.com/Artprozew/GenshinRichPresence/blob/master/LICENSE
