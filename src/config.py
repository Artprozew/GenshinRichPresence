import logging
import logging.config
import os
import sys
from typing import Final

import dotenv
import PIL.Image
import pystray

from interaction_manager import InteractionManager
from utils.data_tools import capitalize_dict
from utils.exception_manager import exception_handler
from utils.handle_exit import safe_exit

# Program-related pre-configs #

sys.excepthook = exception_handler

# Changes the program's root/current working directory through env for testing purposes or if any issue occurs
MAIN_DIRECTORY: Final[str] = str(os.getenv("MAIN_DIRECTORY", os.getcwd()))

if os.path.exists("logging.conf"):
    logging.config.fileConfig("logging.conf")
else:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(module)s (%(levelname)s): %(message)s",
    )

dotenv.load_dotenv(override=True)

_tray_icon: pystray.Icon = pystray.Icon(
    "GenshinRichPresence",
    PIL.Image.open(os.path.join(MAIN_DIRECTORY, "app.ico")),
    "GenshinRichPresence",
    (pystray.MenuItem("Quit", safe_exit),),
)

_tray_icon.run_detached()

interactor = InteractionManager(os.path.join(MAIN_DIRECTORY, "config.ini"))

interactor.handle_backup_configs(os.path.join(MAIN_DIRECTORY, "backup_config.ini"))

_VERSION: Final[str] = interactor.get_ini_settings("INTERNAL", "Version")

# External configs #

# Below are configuration constants that the program will be using
# They will take precedence from the environment variables (can be set through a .env file)
# but if not found, it will take a default value, or, if implemented, the program will
# search on the config.ini file or it will allow the configuration directly through an UI

# Path to your 3DMigoto (e.g. C:\3dmigoto\)
# This is the only really required configuration that can be set through the config.ini
GIMI_DIRECTORY: Final[str] = interactor.get_environ_or_ini(
    "SETTINGS", "GIMI_DIRECTORY", check_path="3DMigoto Loader.exe", dirname=True
)

GIMI_LOG_NAME: Final[str] = interactor.get_environ_or_ini(
    "SETTINGS", "GIMI_LOG_NAME", "d3d11_log.txt"
)

# Starts the game and GIMI automatically on initialization
START_GAME_AND_GIMI: Final[bool] = interactor.get_environ_or_ini(
    "SETTINGS", "START_GAME_AND_GIMI", True, type_=bool
)

# Required only if START_GAME_AND_GIMI is True
GAME_EXE_PATH: Final[str] = interactor.get_environ_or_ini(
    "SETTINGS",
    "GAME_EXE_PATH",
    None if START_GAME_AND_GIMI else "",
    check_path=True if START_GAME_AND_GIMI else False,
)

# Game process name
# Could probably be GenshinImpact.exe or YuanShen.exe
GAME_PROCESS_NAME: Final[str] = str(
    interactor.get_environ_or_ini(
        "SETTINGS",
        "GAME_PROCESS_NAME",
        "GenshinImpact.exe" if not START_GAME_AND_GIMI else os.path.basename(GAME_EXE_PATH),
    )
)

# If set to True, the program will copy the .ini data files to the GIMI's Mods folder
COPY_REQUIRED_DATA: Final[bool] = interactor.get_environ_or_ini(
    "SETTINGS", "COPY_REQUIRED_DATA", True, type_=bool
)

# Finds/sets the path to RichPresenceData folder on GIMI Mods directory (e.g. C:\3dmigoto\Mods\Others\RichPresenceData\)
GRP_DATA_DIRECTORY: Final[str] = interactor.get_environ_or_ini(
    "SETTINGS",
    "GRP_DATA_DIRECTORY",
    interactor.set_up_rpc_data_folder(
        "RichPresenceData",
        os.path.join(MAIN_DIRECTORY, "data"),
        os.path.join(GIMI_DIRECTORY, "Mods"),
        COPY_REQUIRED_DATA,
        not interactor.get_ini_settings("INTERNAL", "Updated_data", type_=bool),
    ),
    check_path="PlayableCharacterData.ini",
)

# Whether or not you want the program to check for data updates about characters or similar (e.g. newly released characters)
# True (always update) or False. Defaults to True
ALWAYS_CHECK_FOR_UPDATES: Final[bool] = bool(
    interactor.get_environ_or_ini("SETTINGS", "ALWAYS_CHECK_FOR_UPDATES", True, type_=bool)
)

# Time between Discord's Rich Presence updates; You may get rate limited if this is lower than 15s (or maybe not, it's not entirely clear)
# Time in seconds. Defaults to 15s
RPC_UPDATE_RATE: Final[int] = int(
    interactor.get_environ_or_ini("SETTINGS", "RPC_UPDATE_RATE", 15, type_=int)
)

# Time to wait if no new lines is found in the log
# Time in seconds. Defaults to 1.5s
LOG_TAIL_SLEEP_TIME: Final[float] = float(
    interactor.get_environ_or_ini("SETTINGS", "LOG_TAIL_SLEEP_TIME", 1.5, type_=float)
)

# App ID for the Discord Rich Presence application, can be changed if needed
APP_ID: Final[int] = int(
    interactor.get_environ_or_ini("SETTINGS", "APP_ID", 1234834454569025538, type_=int)
)


# Debugging
# Not recommended to activate, unless having any problems with the program
IS_DEBUGGING: Final[bool] = bool(
    interactor.get_environ_or_ini("SETTINGS", "IS_DEBUGGING", False, type_=bool)
)

# Unit tests
# May disable logging logs
IS_TESTING: Final[bool] = bool(
    interactor.get_environ_or_ini("SETTINGS", "IS_TESTING", "unittest" in sys.modules, type_=bool)
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
configRPC_characters: Final[dict[str, str]] = capitalize_dict(
    interactor.get_environ_or_ini("CHARACTER_IMG", None, {}, type_=dict), delimiter="_", value=False
)

# Region images
configRPC_regions: Final[dict[str, str]] = capitalize_dict(
    interactor.get_environ_or_ini("REGION_IMG", None, {}, type_=dict), delimiter="_", value=False
)


# Additional checks

if START_GAME_AND_GIMI and not os.path.isfile(GAME_EXE_PATH):
    raise RuntimeError(
        'The "GAME_EXE_PATH" must be the path where your game executable is located.'
    )


# Program-related post-configs #

if IS_DEBUGGING:
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("logger.log", "w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(module)s (%(levelname)s): %(message)s")
    )
    logger.addHandler(file_handler)

if IS_TESTING:
    logging.disable(logging.CRITICAL)

interactor.set_ini_option("INTERNAL", "Updated_data", "True")

_program_stop_flag: bool = False
