from io import TextIOWrapper
from typing import Generator, Any, Final
import os
import time
import config
import logging
from rich_presence import DiscordRichPresence


class LogMonitor:
    def __init__(self, log_dir: str) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)

        if not os.path.exists(log_dir):
            raise FileNotFoundError("Could not find the game log")

        self.rpc: DiscordRichPresence = DiscordRichPresence()

        self._logger.info("Opening log file")
        self._log_file: TextIOWrapper = self.open_log_file(log_dir)

    def start(self) -> None:
        if self.get_file_size() > 5000000:
            self.seek_back_n_bytes_from_end(5000000)

        self._logger.info("Initialize presence activity")
        self.rpc.update_rpc()

        self._logger.info("Running log file tail loop")
        self._logger.info("Your activity will now be updated accordingly")
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
            line: str = self._log_file.readline()

            if line:
                yield line
                continue

            # If there's no new lines, will check for updates, preventing outdated info
            if self.rpc.can_update_rpc():
                self.rpc.update_rpc()

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

            # Examples to be matched: TextureOverride\Mods\Anything\RichPresenceData\WorldData.ini\__Fontaine__LumitoileIB matched (...) OR
            # TextureOverride\Mods\Anything\RichPresenceData\PlayableCharacterData.ini\ClorindeVertexLimitRaise matched (...)
            asset_line: list[str] = line.split("PlayableCharacterData.ini\\")

            # if Asset is a Playable Character
            if len(asset_line) > 1:
                # Ignore everything after "VertexLimitRaise" and keep just the character name
                character: str = asset_line[1].split("VertexLimitRaise")[0]
                if self.rpc.current_character == character:
                    continue

                self.rpc.current_character = character
                self.rpc.updatable = True
                self._logger.debug(f"Updated current_character to {self.rpc.current_character}")
                continue

            # if Asset is not a Playable Character (so it is a region, because currently we only scrape Characters and Regions)
            # Gets the name of the region (between double underscores) after the .ini file name
            region: str = asset_line[0].split("WorldData.ini\\")[1].split("__", 2)[1]
            # Replace single underscore for regions like Sumeru_Forest
            region = region.replace("_", " ")

            if self.rpc.current_region == region:
                continue

            self.rpc.previous_region = self.rpc.current_region
            self.rpc.current_region = region
            self.rpc.updatable = True
            self._logger.debug(
                f"Updated region to {self.rpc.current_region}, "
                f"hash: {asset_line[0].split('hash=')[1].split(' ')[0]}"
            )
