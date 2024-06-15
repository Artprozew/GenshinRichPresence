from typing import Final
import os

import dotenv

dotenv.load_dotenv()

# Path to your 3DMigoto (e.g. C:\3dmigoto\)
GIMI_DIRECTORY: os.PathLike = os.getenv("GIMI_DIRECTORY")
# Path to your RichPresenceData in your GIMI Mods folder (e.g. C:\3dmigoto\Mods\Others\RichPresenceData)
GRP_DATA_DIRECTORY: os.PathLike = os.getenv("GRP_DATA_DIRECTORY") 

# Whether or not you want the program to check updates for data about the characters or similar (e.g. newly released characters)
# True (always update) or False. Defaults to True
ALWAYS_CHECK_FOR_UPDATES: Final[bool] = bool(os.getenv("ALWAYS_CHECK_FOR_UPDATES", True))
# Time in seconds between Discord's Rich Presence updates; You may get rate limited if this is lower than 15s (or not, it's not entirely clear)
# Time in seconds. Defaults to 15s
RPC_UPDATE_RATE: Final[int] = int(os.getenv("RPC_UPDATE_RATE", 15))
# Time to wait if no new lines is found in the log
# Time in milliseconds. Defaults to 1.5
LOG_TAIL_SLEEP_TIME: Final[float] = float(os.getenv("LOG_TAIL_SLEEP_TIME", 1.5))

# You can change the App ID if you want to use your own application
APP_ID: Final[int] = int(os.getenv("APP_ID", 1234834454569025538))

# Debugging
# Not recommended to activate, unless having problems with the program
IS_DEBUGGING: Final[bool] = bool(os.getenv("IS_DEBUGGING", False))