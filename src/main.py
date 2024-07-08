import logging
import logging.config
import threading

import config
from data_handler import fetch_data
from game_monitor import GameMonitor
from interaction_manager import InteractionManager
from log_monitor import LogMonitor
from rich_presence import DiscordRichPresence
from utils.handle_exit import safe_exit


class GenshinRichPresence:
    def __init__(self) -> None:
        self._logger: logging.Logger = logging.getLogger()

        self.interaction_manager: InteractionManager = config.interactor
        self._game_monitor: GameMonitor = GameMonitor()

        if config.START_GAME_AND_GIMI:
            threading.Thread(target=self._game_monitor.run_game_and_gimi).start()

        if config.ALWAYS_CHECK_FOR_UPDATES:
            fetch_data.check_characters_updates()

        self._rich_presence: DiscordRichPresence = DiscordRichPresence(self._game_monitor)
        self._log_monitor: LogMonitor = LogMonitor(self._rich_presence)

    def start(self) -> None:
        if not self._game_monitor.wait_for_game(config.GAME_PROCESS_NAME):
            return

        self._game_monitor.set_game_process()

        self._rich_presence.connect()
        self._log_monitor.start()

        safe_exit()


if __name__ == "__main__":
    GenshinRichPresence().start()
