import logging
import logging.config
import os
import sys

import config
from game_monitor import GameMonitor
from log_monitor import LogMonitor
from rich_presence import DiscordRichPresence
from utils.exception_manager import exception_handler


class GenshinRichPresence:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

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
