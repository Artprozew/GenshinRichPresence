# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1.1] - 2024-07-27

Quick patch fix as the images for the characters with spaces in their names was not working properly.

### Fixes:

- Images for the characters with spaces in their names will now work properly.

## [v1.1.0] - 2024-07-26

### Fixes:

- Encoding exceptions, UTF-8 will now be used, while also ignoring possible encoding errors on the log file.
- Add/Improve validations for the `config.ini` paths.
- Character with skins will now be displayed correctly.
- Wrong/missing character data (Childe and Sigewinne, Kirara and Nilou skins). Ayaka skin will still be missing for now.

### Added

- NSIS-based installer with a custom behavior for easy program installation.
- The program can now apply the settings from a `backup_config.ini` file (the installer creates that) to the `config.ini` file, if that backup file exists.

## [v1.0.2] - 2024-07-20

### Fixed

- `PipeClosed` exceptions from RPC/Pypresence
- Possible `IndexError: list index out of range` exceptions, the cause is still unknown
- Incorrect character names when adding new character data to the `.ini` file
- New data from newer versions of the progam will now take priority and will replace existing ones
- ConfigParser can now keep comments when writing to `.ini` files

### Changed

- Assure `separate_with()` function correct behavior
- Remove unused InteractionManager method
- Quick fix/workaround for standalone version of `update_data`

## [v1.0.1] - 2024-07-11

### Fixed

- Wrong encoding when reading `.ini` files which was causing issues if any directory had accents, UTF-8 is now preferred.
- If `START_GAME_AND_GIMI` is set to True, checks if the `GAME_EXE_PATH` is an executable file.

## [v1.0.0] - 2024-07-10

First full release!

This release is a fully refactored and more modular codebase that introduces even more features.

### Added

- Datas from `.ini` mod files can be added to GIMI Mods folder automatically
- Option to start the game and GIMI automatically on program startup ([#7](https://github.com/Artprozew/GenshinRichPresence/issues/7))
- System tray icon ([#6](https://github.com/Artprozew/GenshinRichPresence/issues/6))
- Fully customizable settings and Rich Presence through `.ini` file ([#18](https://github.com/Artprozew/GenshinRichPresence/issues/18), [#11](https://github.com/Artprozew/GenshinRichPresence/issues/11))
- Regular expressions on the core loop have been replaced by the `split()` function that might perform a lot better ([#13](https://github.com/Artprozew/GenshinRichPresence/issues/13))
- Characters that do not have a mod on GIMI can now also be detected ([#22](https://github.com/Artprozew/GenshinRichPresence/issues/22))
- New released characters can be added automatically to the character data


## [v0.1.1-beta] - 2024-05-23

Initial pre-release!
This pre-release introduces the basic core functionality: Character, Region and Inactivity statuses.

### Added

- Character and region status information ([#14](https://github.com/Artprozew/GenshinRichPresence/issues/14))
- Inactive or in-game statuses ([#4](https://github.com/Artprozew/GenshinRichPresence/issues/4))
- Constants for timed delays ([#15](https://github.com/Artprozew/GenshinRichPresence/issues/15))
- Simple .ini configuration file with user input for GIMI directory
- New separate module for data handling
- Exception handler and logger
- JSON data files for characters and regions
- Project-related files and dependencies

### Fixed

- Presence not initializing correctly ([#16](https://github.com/Artprozew/GenshinRichPresence/issues/16))
