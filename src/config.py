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

# Configs #

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
# There's no need to set it anymore, unless any problem is occurring, as the program will try to find that folder automatically through GIMI_DIRECTORY
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
# Game process name
# Defaults to GenshinImpact.exe
GAME_PROCESS_NAME: Final[str] = str(os.getenv("GAME_PROCESS_NAME", "GenshinImpact.exe"))

# Debugging
# Not recommended to activate, unless having any problems with the program
IS_DEBUGGING: Final[bool] = bool(os.getenv("IS_DEBUGGING", False))
# Unit tests
# May disable logging logs
IS_TESTING: Final[bool] = bool(os.getenv("IS_TESTING", "unittest" in sys.modules))

if IS_DEBUGGING:
    logging.getLogger(__name__).setLevel(logging.DEBUG)

if IS_TESTING:
    logging.disable(logging.CRITICAL)


configRPC_configs: Final[dict[str, str]] = {
    "large_image": r"%(character_image)",
    "large_text": r"%(character)",
    "small_image": r"%(region_image)",
    "small_text": r"Exploring %(region)",

    "details": r"Playing as %(character)",
    "state": r"Exploring %(region), %(user_activity)",
}

configRPC_characters: Final[dict[str, str]] = {
    "Wanderer": "https://i.makeagif.com/media/12-17-2023/ed-2A5.gif",
    "Faruzan": "https://media1.tenor.com/m/CXr2pvyBxl4AAAAC/genshin.gif",
    "Clorinde": "https://64.media.tumblr.com/e28279e5cbfdfaec1be5cacd8df32fd8/276f74c51d8ec863-c7/s1280x1920/d6387f611c68cfaf92e6b44fe5f813292793eacb.gif"
}

configRPC_regions: Final[dict[str, str]] = {
    "Mondstadt": "https://static.wikia.nocookie.net/gensin-impact/images/c/ce/Mondstadt_Emblem_Night.png/revision/latest?cb=20231103102409",
    "Liyue": "https://static.wikia.nocookie.net/gensin-impact/images/c/c3/Liyue_Emblem_Night.png/revision/latest?cb=20231103102407",
    "Inazuma": "https://static.wikia.nocookie.net/gensin-impact/images/a/a5/Inazuma_Emblem_Night.png/revision/latest?cb=20231103102405",
    "Sumeru Forest": "https://static.wikia.nocookie.net/gensin-impact/images/6/6a/Emblem_Sumeru_White.png/revision/latest?cb=20220718184158",
    "Sumeru Desert": "https://static.wikia.nocookie.net/gensin-impact/images/7/74/Emblem_Great_Red_Sand_White.png/revision/latest/scale-to-width-down/1000?cb=20221001152345",
    "Fontaine": "https://static.wikia.nocookie.net/gensin-impact/images/7/7b/Emblem_Fontaine_White.png/revision/latest?cb=20230807032406",
    "The Chasm": "https://static.wikia.nocookie.net/gensin-impact/images/a/a5/Emblem_The_Chasm_White.png/revision/latest?cb=20220330185618",
    "Chenyu": "https://static.wikia.nocookie.net/gensin-impact/images/6/68/Emblem_Chenyu_Vale_White.png/revision/latest?cb=20240131053952",
    "Enkanomiya": "https://static.wikia.nocookie.net/gensin-impact/images/6/65/Enkanomiya_Emblem_Night.png/revision/latest?cb=20231103102358",
    "Teapot": "https://static.wikia.nocookie.net/gensin-impact/images/5/56/Emblem_Serenitea_Pot.png/revision/latest?cb=20210615025730",
    "Domain": "https://static.wikia.nocookie.net/gensin-impact/images/b/b1/Emblem_Domains.png/revision/latest?cb=20210615025731",
}
