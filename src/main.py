import logging.config
from log_monitor import LogMonitor
from interaction_manager import InteractionManager
from utils.exception_manager import exception_handler
import sys
from game_monitor import GameMonitor
import config
import os
import logging


if os.path.exists("logging.conf"):
    logging.config.fileConfig("logging.conf")
else:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(module)s (%(levelname)s): %(message)s",
    )

logger = logging.getLogger(__name__)


class GenshinRichPresence:
    def __init__(self) -> None:

        self.interaction_manager = config.interactor
        self._game_monitor = GameMonitor()
        self._rich_presence = DiscordRichPresence(self._game_monitor)
        self._log_monitor = LogMonitor(self._rich_presence)

    def start(self) -> None:
        self._game_monitor.wait_for_game()
        self._rich_presence.connect()
        self._log_monitor.start(os.path.join(config.GIMI_DIRECTORY, "d3d11_log.txt"))


if __name__ == "__main__":
    sys.excepthook = exception_handler
    GenshinRichPresence().start()
