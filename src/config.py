import logging
import logging.config
import os
import tempfile
from typing import Final

import dotenv

from interaction_manager import InteractionManager

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

# Below are configuration constants that the program will be using
# They will take precedence from the environment variables (can be set through a .env file)
# but if not found, it will take a default value, or, if implemented, the program will
# search on the config.ini file or it will allow the configuration directly through an UI

# Path to your 3DMigoto (e.g. C:\3dmigoto\)
GIMI_DIRECTORY: Final[str] = str(
    os.getenv(
        "GIMI_DIRECTORY",
        interactor.get_check_save_ini("SETTINGS", "GIMI_DIRECTORY", "path to your 3DMigoto folder"),
    )
)

# Path to RichPresenceData folder on GIMI Mods directory (e.g. C:\3dmigoto\Mods\Others\RichPresenceData\)
# There's no need to set it anymore, unless any problem is occurring, as the program will try to find that folder through GIMI_DIRECTORY
GRP_DATA_DIRECTORY: Final[str] = str(
    os.getenv(
        "GRP_DATA_DIRECTORY", interactor.find_folder("RichPresenceData", f"{GIMI_DIRECTORY}\\Mods")
    )
)

# Whether or not you want the program to check updates for data about the characters or similar (e.g. newly released characters)
# True (always update) or False. Defaults to True
ALWAYS_CHECK_FOR_UPDATES: Final[bool] = bool(os.getenv("ALWAYS_CHECK_FOR_UPDATES", True))
# Time between Discord's Rich Presence updates; You may get rate limited if this is lower than 15s (or maybe not, it's not entirely clear)
# Time in seconds. Defaults to 15s
RPC_UPDATE_RATE: Final[int] = int(os.getenv("RPC_UPDATE_RATE", 15))
# Time to wait if no new lines is found in the log
# Time in milliseconds. Defaults to 1.5
LOG_TAIL_SLEEP_TIME: Final[float] = float(os.getenv("LOG_TAIL_SLEEP_TIME", 1.5))

# You can change the App ID if you want to use your own application
APP_ID: Final[int] = int(os.getenv("APP_ID", 1234834454569025538))

# Debugging
# Not recommended to activate, unless having any problems with the program
IS_DEBUGGING: Final[bool] = bool(os.getenv("IS_DEBUGGING", False))
