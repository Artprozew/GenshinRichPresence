import logging
import os
import time
from io import TextIOWrapper
from types import FrameType
from typing import Any, Final, Generator, Optional

import config
from rich_presence import DiscordRichPresence
from utils import handle_exit


class LogMonitor:
    def __init__(self, rpc: DiscordRichPresence) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)

        self.rpc: DiscordRichPresence = rpc

        handle_exit.handle_exit_hook(self._teardown, 0, None)

    def _teardown(self, _signal_number: int, _stack_frame: Optional[FrameType]) -> None:
        config._program_stop_flag = True

        if hasattr(self, "_log_file") and self._log_file is not None and not self._log_file.closed:
            self._logger.warning("Closing log file and shutting down")
            self._log_file.close()

    def start(self) -> None:
        if config.START_GAME_AND_GIMI:
            self._logger.debug("Waiting for log creation")
            tries = 0

            while not os.path.exists(os.path.join(config.GIMI_DIRECTORY, config.GIMI_LOG_NAME)):
                if tries >= 60 or config._program_stop_flag:
                    self._logger.debug("Log was not found. exiting")
                    return

                tries += 1
                time.sleep(1)

        self._logger.info("Opening log file")
        self._log_file: TextIOWrapper = self.open_log_file(
            os.path.join(config.GIMI_DIRECTORY, config.GIMI_LOG_NAME)
        )

        if self.get_file_size() > 5000000:
            self.seek_back_n_bytes_from_end(5000000)

        self._logger.info("Running log file tail loop")
        self._logger.info("\n\nYour activity will now be updated accordingly\n")
        self.handle_log()

    def get_file_size(self) -> int:
        current_cursor_position: Final[int] = self._log_file.tell()
        self._log_file.seek(os.SEEK_SET, os.SEEK_END)

        size: Final[int] = self._log_file.tell()
        self._log_file.seek(current_cursor_position)

        return size

    def seek_back_n_bytes_from_end(self, n_bytes: int) -> None:
        self._log_file.seek(self.get_file_size() - n_bytes, os.SEEK_SET)

    def open_log_file(self, log_dir: str) -> TextIOWrapper:
        if not os.path.exists(log_dir):
            raise FileNotFoundError(f'The file "{log_dir}" could not be found')

        return open(log_dir, "r")

    def tail_file(self) -> Generator[str, Any, None]:
        while True:
            if config._program_stop_flag:
                break

            line: str = self._log_file.readline()

            if line:
                yield line
                continue

            # If there's no new lines, will check for updates, preventing outdated info
            if self.rpc.can_update_rpc():
                self.rpc.update_rpc()

            if not self.rpc.game_monitor.is_process_running():
                self._logger.debug("Game proccess is not running, exiting...")
                handle_exit.safe_exit()

            time.sleep(config.LOG_TAIL_SLEEP_TIME)

    def handle_log(self) -> None:
        line: str
        for line in self.tail_file():
            # Ignore lines we do not need
            if (
                "TextureOverride" not in line
                or "\\RichPresenceData\\" not in line
                or line.endswith("]\n")
            ):
                continue

            # Example lines from the log and their expected output:
            # "TextureOverride\Mods\Anything\RichPresenceData\WorldData.ini\__Fontaine__LumitoileIB (...)" as "Fontaine" OR
            # "TextureOverride\Mods\Anything\RichPresenceData\PlayableCharacterData.ini\__Hu_Tao__VertexLimitRaise (...)" as "Hu Tao"
            ini_name: str
            asset_name: str
            ini_name, asset_name = line.split("RichPresenceData\\")[1].split("\\", 2)

            # Gets only the asset name e.g. "__Sumeru_Forest__(...)" as "Sumeru Forest"
            asset_name = asset_name.split("__", 2)[1].replace("_", " ")

            if ini_name == "PlayableCharacterData.ini":
                if self.rpc.current_character == asset_name:
                    continue

                self.rpc.current_character = asset_name
                self.rpc.updatable = True
                self._logger.debug(f"Updated current_character to {self.rpc.current_character}")
            else:
                # WorldData.ini
                if self.rpc.current_region == asset_name:
                    continue

                self.rpc.previous_region = self.rpc.current_region
                self.rpc.current_region = asset_name
                self.rpc.updatable = True
                self._logger.debug(
                    f"Updated region to {self.rpc.current_region}, "
                    f"hash: {line.split('hash=')[1].split(' ')[0]}"
                )
