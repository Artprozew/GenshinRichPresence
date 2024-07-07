import logging
import logging.config
import os
from typing import Any

import config
from game_monitor import GameMonitor
from log_monitor import LogMonitor
from rich_presence import DiscordRichPresence
from utils.handle_exit import safe_exit


class GenshinRichPresence:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

        GameMonitor.wait_for_game(config.GAME_PROCESS_NAME)

        self.interaction_manager = config.interactor
        self._game_monitor = GameMonitor()
        self._rich_presence = DiscordRichPresence(self._game_monitor)
        self._log_monitor = LogMonitor(self._rich_presence)

    def start(self) -> None:
        self._rich_presence.connect()
        self._log_monitor.start(os.path.join(config.GIMI_DIRECTORY, "d3d11_log.txt"))

        safe_exit()


if __name__ == "__main__":
    GenshinRichPresence().start()
