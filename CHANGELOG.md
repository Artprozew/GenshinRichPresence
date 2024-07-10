# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-10

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


## [0.1.1-beta] - 2024-05-23

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
