import logging
import logging.config
import os
import sys
from typing import Final

import dotenv

from interaction_manager import InteractionManager

# Pre configs #

dotenv.load_dotenv()

if os.path.exists("logging.conf"):
    logging.config.fileConfig("logging.conf")
else:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(module)s (%(levelname)s): %(message)s",
    )

interactor = InteractionManager(
    f"{tempfile.gettempdir()}\\GenshinRichPresence\\config.ini", "d3d11_log.txt"
)

# External configs #

# Below are configuration constants that the program will be using
# They will take precedence from the environment variables (can be set through a .env file)
# but if not found, it will take a default value, or, if implemented, the program will
# search on the config.ini file or it will allow the configuration directly through an UI

# Path to your 3DMigoto (e.g. C:\3dmigoto\)
# This is the only really required configuration that can be set through the config.ini
GIMI_DIRECTORY: Final[str] = interactor.get_environ_or_ini(
    "SETTINGS", "GIMI_DIRECTORY", check_file=True
)

# Path to RichPresenceData folder on GIMI Mods directory (e.g. C:\3dmigoto\Mods\Others\RichPresenceData\)
# There's no need to set it anymore, unless any problem is occurring, as the program will try to find that folder automatically through GIMI_DIRECTORY
GRP_DATA_DIRECTORY: Final[str] = interactor.get_environ_or_ini(
    "SETTINGS",
    "GRP_DATA_DIRECTORY",
    interactor.find_folder("RichPresenceData", os.path.join(GIMI_DIRECTORY, "Mods")),
)

# Whether or not you want the program to check updates for data about the characters or similar (e.g. newly released characters)
# True (always update) or False. Defaults to True
ALWAYS_CHECK_FOR_UPDATES: Final[bool] = bool(
    interactor.get_environ_or_ini("SETTINGS", "ALWAYS_CHECK_FOR_UPDATES", True)
)
# Time between Discord's Rich Presence updates; You may get rate limited if this is lower than 15s (or maybe not, it's not entirely clear)
# Time in seconds. Defaults to 15s
RPC_UPDATE_RATE: Final[int] = int(interactor.get_environ_or_ini("SETTINGS", "RPC_UPDATE_RATE", 15))
# Time to wait if no new lines is found in the log
# Time in milliseconds. Defaults to 1.5
LOG_TAIL_SLEEP_TIME: Final[float] = float(
    interactor.get_environ_or_ini("SETTINGS", "LOG_TAIL_SLEEP_TIME", 1.5)
)

# You can change the App ID if you want to use your own application
APP_ID: Final[int] = int(interactor.get_environ_or_ini("SETTINGS", "APP_ID", 1234834454569025538))
# Game process name
# Defaults to GenshinImpact.exe
GAME_PROCESS_NAME: Final[str] = str(
    interactor.get_environ_or_ini("SETTINGS", "GAME_PROCESS_NAME", "GenshinImpact.exe")
)

# Debugging
# Not recommended to activate, unless having any problems with the program
IS_DEBUGGING: Final[bool] = bool(interactor.get_environ_or_ini("SETTINGS", "IS_DEBUGGING", False))
# Unit tests
# May disable logging logs
IS_TESTING: Final[bool] = bool(
    interactor.get_environ_or_ini("SETTINGS", "IS_TESTING", "unittest" in sys.modules)
)


# Rich Presence activity configs
configRPC_configs: Final[dict[str, str]] = {
    "large_image": interactor.get_environ_or_ini("ACTIVITY", "large_image", "%(character_image)"),
    "large_text": interactor.get_environ_or_ini("ACTIVITY", "large_text", "%(character)"),
    "small_image": interactor.get_environ_or_ini("ACTIVITY", "small_image", "%(region_image)"),
    "small_text": interactor.get_environ_or_ini("ACTIVITY", "small_text", "Exploring %(region)"),
    "details": interactor.get_environ_or_ini("ACTIVITY", "details", "Playing as %(character)"),
    "state": interactor.get_environ_or_ini("ACTIVITY", "state", "Exploring %(region)"),
}

# Character images
configRPC_characters: Final[dict[str, str]] = interactor.capitalize_dict(
    interactor.get_environ_or_ini("CHARACTER_IMG", None, {}), delimiter="_", value=False
)

# Region images
configRPC_regions: Final[dict[str, str]] = interactor.capitalize_dict(
    interactor.get_environ_or_ini("REGION_IMG", None, {}), delimiter="_", value=False
)


# Program-related post-configs #

if IS_DEBUGGING:
    logging.getLogger(__name__).setLevel(logging.DEBUG)

if IS_TESTING:
    logging.disable(logging.CRITICAL)

_program_stop_flag: bool = False
