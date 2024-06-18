import asyncio
import logging
import logging.config
import os
import sys
import tempfile
import time
from configparser import ConfigParser
from io import TextIOWrapper
from typing import Optional, AsyncGenerator, Any

import nest_asyncio
import psutil
from pypresence import Presence

import config
from data_handler import fetch_data

try:
    import win32gui
except ImportError:
    pass

nest_asyncio.apply()


class GenshinRichPresence:
    def __init__(self) -> None:
        if os.path.exists("logging.conf"):
            logging.config.fileConfig("logging.conf")
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(asctime)s] %(module)s (%(levelname)s): %(message)s",
            )

        self.logger: logging.Logger = logging.getLogger(__name__)

        self.rpc: Presence = Presence(
            config.APP_ID,
            loop=asyncio.new_event_loop(),
        )
        self.process: Optional[psutil.Process] = None

        self.current_character: str = "Unknown"
        self.current_region: Optional[str] = None
        self.previous_region: Optional[str] = None

        self.last_update: float = time.time() + config.RPC_UPDATE_RATE
        self.updatable: bool = True
        self.is_inactive: bool = True

        self.details: Optional[str] = None
        self.small_image: str = "unknown"

        self.world_data: dict[str, str]

    def can_update_rpc(self) -> bool:
        if (time.time() - self.last_update) > config.RPC_UPDATE_RATE:
            self.check_changed_focus()
            return self.updatable

        return False

    def set_last_update(self) -> None:
        self.last_update = time.time()

    def check_changed_focus(self) -> bool:
        changed: bool = self.is_inactive

        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Genshin Impact":
            self.is_inactive = False
        else:
            self.is_inactive = True

        changed = changed != self.is_inactive
        if changed:
            self.updatable = True
            self.logger.debug(f"Changed inactive status to {self.is_inactive}")

        return changed

    def get_process(self) -> Optional[psutil.Process]:
        self.logger.info("Searching for process")

        for proc in psutil.process_iter():
            if "GenshinImpact.exe" in proc.name():
                return proc

        return None

    def handle_exceptions(self, exc_type: Any, exc_value: Any, tb: Any) -> None:
        import traceback

        with open(f"{tempfile.gettempdir()}\\GenshinRichPresence\\traceback.txt", "w") as file:
            for line in traceback.format_exception(exc_type, exc_value, tb):
                file.writelines(line)

        traceback.print_exception(exc_type, exc_value, tb)
        os.system("pause")
        sys.exit(-1)

    def open_log_file(self) -> TextIOWrapper:
        self.logger.info("Opening log file")

        log_file = os.path.join(config.GIMI_DIRECTORY, "d3d11_log.txt")
        if not os.path.exists(log_file):
            raise FileNotFoundError(f'The file "{log_file}" could not be found')

        wrapper: TextIOWrapper = open(log_file, "r")
        return wrapper

    def save_ini_file(self, config_parser: ConfigParser, ini_file: str) -> None:
        if not os.path.exists(os.path.dirname(ini_file)):
            os.mkdir(os.path.dirname(ini_file))

        if not config_parser.has_section("SETTINGS"):
            config_parser.add_section("SETTINGS")
        config_parser["SETTINGS"]["GIMI_DIRECTORY"] = config.GIMI_DIRECTORY

        with open(ini_file, "w") as file:
            config_parser.write(file)

    def check_gimi_dir(self) -> None:
        config_parser = ConfigParser()
        ini_file: str = f"{tempfile.gettempdir()}\\GenshinRichPresence\\config.ini"

        if not os.path.exists(ini_file):
            print("\nPlease write here your GIMI directory path")
            config.GIMI_DIRECTORY = input("Path > ")
            self.save_ini_file(config_parser, ini_file)
        else:
            config_parser.read(ini_file)
            config.GIMI_DIRECTORY = config_parser.get("SETTINGS", "GIMI_DIRECTORY")

            print(
                f"\nGIMI directory found: {config.GIMI_DIRECTORY}\n\
                    Press ENTER if you wanna keep it. Otherwise, write the new directory"
            )
            answer = input(" > ")

            if not answer:
                config_parser.read(ini_file)
                config.GIMI_DIRECTORY = config_parser.get("SETTINGS", "GIMI_DIRECTORY")
            else:
                config.GIMI_DIRECTORY = answer
                self.save_ini_file(config_parser, ini_file)

        if not config.GIMI_DIRECTORY:
            raise RuntimeError("You should set the GIMI_DIRECTORY path!")

    def update_rpc_details(self) -> None:
        if not self.details or not self.current_region:
            self.details = "On Menus"
            return None

        # Workaround: Fixes the incorrect displayed region as Liyue when the player is on The Chasm
        # Issue #27: https://github.com/Artprozew/GenshinRichPresence/issues/27
        if self.current_region == "liyue" and self.previous_region == "the_chasm":
            self.logger.debug("Setting region as the_chasm instead of liyue to workaround #27")
            self.current_region = "the_chasm"

        # Capitalize and remove underscore from the region name
        # If this gets too frequent, it's probably better to save it in memory for later use
        current_region_name: str = " ".join(
            [word.capitalize() for word in self.current_region.split("_")]
        )
        player_is_inactive = "Inactive" if self.is_inactive else "In-game"

        self.details = f"{player_is_inactive}. Exploring {current_region_name}"
        return None

    async def update_rpc(self) -> None:
        self.check_changed_focus()
        self.update_rpc_details()

        self.rpc.update(
            start=self.process.create_time(),  # type: ignore # Needs rework of class and better logic with None
            state=f"Playing as {self.current_character}",
            details=self.details,
            large_image="genshin",
            small_image=self.small_image,
            large_text="Genshin Impact",
            small_text=self.current_character,
        )

        self.set_last_update()
        self.updatable = False
        self.logger.debug("RPC Updated")

    async def tail_file(self, file: TextIOWrapper) -> AsyncGenerator[str, None]:
        # Gets the size of the log file
        size: int = os.stat(os.path.join(config.GIMI_DIRECTORY, "d3d11_log.txt")).st_size

        # Sets the cursor to read the latest 5MB of data
        file.seek(os.SEEK_SET)
        if size > 5000000:
            file.seek(size - 5000000, os.SEEK_SET)

        last_position: int = file.tell()
        line: str = ""

        self.logger.info("Running log file tail loop")
        self.logger.info("Your activity will now be updated accordingly")

        while True:
            file.seek(last_position)
            line = file.readline()

            if line:
                last_position = file.tell()
                yield line
                continue

            # If there's no new lines, will check for updates, preventing outdated info
            if self.can_update_rpc():
                await self.update_rpc()

            await asyncio.sleep(config.LOG_TAIL_SLEEP_TIME)

    async def handle_log(self) -> None:
        self.logger.info("Initialize presence activity")
        await self.update_rpc()

        log_text_wrapper: TextIOWrapper = self.open_log_file()

        async for line in self.tail_file(log_text_wrapper):
            # Ignore lines we do not need
            if "TextureOverride" not in line or "\\RichPresenceData\\" not in line:
                continue

            # Examples to be matched: TextureOverride\Mods\Anything\RichPresenceData\WorldData.ini\LumitoileIB matched (...) OR
            # TextureOverride\Mods\Anything\RichPresenceData\PlayableCharacterData.ini\ClorindeVertexLimitRaise matched (...)
            line_match_list: list[str] = line.split("PlayableCharacterData.ini\\")

            # Check if line references a character OR world .ini file
            if len(line_match_list) > 1:
                # Ignore everything after "VertexLimitRaise" and keep just the character name
                character: str = line_match_list[1].split("VertexLimitRaise")[0]

                if self.current_character != character:
                    self.current_character = character
                    self.updatable = True
                    self.logger.debug(f"Updated current_character to {self.current_character}")
            else:
                # Get and concatenate just the texture text after the .ini file
                asset: str = line_match_list[0].split("WorldData.ini\\")[1].split(" ")[0]
                asset = f"TextureOverride{asset}"
                new_region: str = self.world_data[asset][1]

                if self.current_region != new_region:
                    # Store the "current" region into the previous_region
                    self.previous_region = self.current_region

                    self.current_region = new_region
                    self.updatable = True
                    self.logger.debug(
                        f"Updated region to {self.current_region}, hash: {self.world_data[asset][0]}"
                    )

    def main(self) -> None:
        sys.excepthook = self.handle_exceptions

        self.check_gimi_dir()

        self.process = self.get_process()
        if not self.process:
            self.logger.warning("Process not found. Exiting")
            os.system("pause")
            return None

        self.logger.info(f"Process {self.process.pid} found. Starting RPC")

        self.logger.info("Connecting and starting handshake")
        self.rpc.connect()
        self.logger.info("Connected")

        self.logger.info("Fetching data")
        self.world_data = fetch_data.fetch_all_data()
        asyncio.get_event_loop().run_until_complete(self.handle_log())

        return None


if __name__ == "__main__":
    GenshinRichPresence().main()
