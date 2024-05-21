import asyncio
import logging
import os
import re
import time
from typing import Optional, AsyncGenerator, Final, Dict, List

import dotenv
import nest_asyncio
import psutil
from pypresence import Presence
import win32gui

from data_handler import fetch_data

dotenv.load_dotenv()
nest_asyncio.apply()

class GenshinRichPresence():
    GIMI_DIRECTORY: Final[os.PathLike] = os.getenv("GIMI_DIRECTORY")
    RPC_UPDATE_RATE: Final[int] = 15 # Can have problems with Discord updating it if its < 15; Time in milliseconds
    FOCUS_CHANGE_CHECK_RATE: Final[float] = 10.0
    LOG_TAIL_SLEEP_TIME: Final[float] = 0.4

    def __init__(self) -> None:
        if not self.GIMI_DIRECTORY:
            raise(RuntimeError("You should set the GIMI_DIRECTORY path! (How to)"))

        self.logger: logging.Logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(module)s (%(levelname)s): %(message)s")

        self.rpc: Presence = Presence(os.getenv("APP_ID") or 1234834454569025538, loop=asyncio.new_event_loop())
        self.process: Optional[psutil.Process] = None

        self.last_char: List[str, str] = ["", "Unknown"]
        self.region: Optional[str] = None
        self.previous_region: Optional[str] = None
        self.last_region: List[Optional[str], Optional[str]] = [None, None]
        
        self.last_update: float = time.time() + self.RPC_UPDATE_RATE
        self.updatable: bool = True
        self.inactive: bool = True
        
        self.details: Optional[str] = None
        self.small_image: str = "unknown"

        self.data: List[str]
        self.world_data: Dict[str, str]


    def can_update_rpc(self) -> bool:
        return (time.time() - self.last_update) > self.RPC_UPDATE_RATE and self.updatable

    def set_last_update(self) -> None:
        self.last_update = time.time()

    def has_changed_focus(self) -> bool:
        changed = self.inactive

        if (win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Genshin Impact"):
            self.inactive = False
            self.logger.debug("Set status as in-game")
        else:
            self.inactive = True
            self.logger.debug("Set status as inactive")

        return changed != self.inactive

    def get_process(self) -> psutil.Process | None:
        self.logger.info("Searching for Process...")

        for proc in psutil.process_iter():
            if "GenshinImpact.exe" in proc.name():
                return proc
                
        return None

    def parse_match(self, match: re.Match) -> tuple[str, str, str]:
        character = match.group(1).split("\\")[1] # Possible "character", but could be something else
        refactoredchar = character.lower().replace(" ", "-") # Data uses "-" instead of "_"
        asset = f"TextureOverride{match.group(1).split('\\')[3]}"
        
        self.logger.debug(f"POSSIBLE CHARACTER: {character}, {refactoredchar}, {match.group(0)}")
        return character, refactoredchar, asset

    def search_character(self, character: str, refactoredchar: str) -> None:
        for name in self.data:
            if name.lower().startswith(refactoredchar): # Character confirmed
                if self.last_char[0] != refactoredchar: # Check if it's not the current character
                    self.last_char = [refactoredchar, character]
                    self.updatable = True # FIXME Do not update instantly, wait if the character will change (Issue #17)
                    self.logger.debug(f"Updated last_char {self.last_char[1]}")
                    break

    def search_region(self, asset: str) -> None:
        for texture, value in self.world_data.items():
            if texture == asset:
                if self.previous_region != self.region:
                    self.previous_region = self.region
                self.region = value[1]
                self.updatable = True
                self.logger.debug(f"Updated region to {value[1]}, hash: {value[0]}")
                break

    def parse_region(self) -> str:
        region = self.region
        region = region.capitalize()

        tmp = []
        for word in region.split("_"):
            tmp.append(word.capitalize())

        return ' '.join(tmp)


    def update_rpc_details(self) -> None:
        if not self.details or not self.region:
            self.details = "On Menus"
            return

        if self.region == "liyue" and self.previous_region == "the_chasm":
            # Workaround: ensure the player's region is set to "The Chasm"  instead of "Liyue"
            # But, it will still report "The Chasm" if the player teleports FROM The Chasm to Liyue.
            self.logger.debug("Setting region as the_chasm because of previous region")
            self.region = "the_chasm"
        
        if self.region != self.last_region[0]: # If the parsed region name is not already saved in memory
            parsed_region = self.parse_region()
            self.last_region = [self.region, parsed_region]

        self.details = f"Currently on: {self.last_region[1]}, {'inactive' if self.inactive else 'in-game'}"

    async def update_rpc(self) -> None:
        self.has_changed_focus()
        self.update_rpc_details()

        if self.last_char[0]:
            self.small_image = self.last_char[0].replace("-", "_")

        self.rpc.update(
            start=self.process.create_time(),
            state=f"Playing as {self.last_char[1]}",
            details=self.details,
            large_image="genshin",
            small_image=self.small_image,
            large_text="Genshin Impact",
            small_text=self.last_char[1]
            )

        self.set_last_update()
        self.updatable = False
        self.logger.debug("RPC Updated")


    async def tail_file(self, file) -> AsyncGenerator[str, None]:
        focus_check: float = time.time()
        self.logger.info("Running log tail loop")
        file.seek(0, os.SEEK_END)

        while True:
            line = file.readline()

            if not line:
                if (time.time() - focus_check) > self.FOCUS_CHANGE_CHECK_RATE: # Not working as expected? Updating too frequently?
                    if self.has_changed_focus(): # Need to periodically check if user isn't alt-tabbed
                        self.updatable = True
                    focus_check = time.time()

                if self.can_update_rpc(): # If there's no new lines, will try to update the last character after 15s, otherwise it would be stopped here
                    await self.update_rpc()
                await asyncio.sleep(self.LOG_TAIL_SLEEP_TIME)
                continue
            
            yield line

    async def handle_log(self) -> None:
        self.logger.info("Updating presence")
        await self.update_rpc()

        self.logger.info("Opening log file")
        if not os.path.exists(os.path.join(self.GIMI_DIRECTORY, "d3d11_log.txt")):
            raise(FileNotFoundError(f'The file "{os.path.join(self.GIMI_DIRECTORY, "d3d11_log.txt")}" could not be found'))
        logfile = open(os.path.join(self.GIMI_DIRECTORY, "d3d11_log.txt"))

        self.logger.info("Log file opened, the loop will now run")
        async for line in self.tail_file(logfile):
            match = re.search(r"TextureOverride\\Mods(.+) matched resource with hash=([a-zA-Z0-9_.-]*)", line)
            if not match: continue

            character, refactoredchar, asset = self.parse_match(match)
            self.search_character(character, refactoredchar)
            self.search_region(asset)


    def main(self) -> None:
        self.process = self.get_process()
        if not self.process:
            self.logger.info("Process not found. Exiting...")
            os.system("pause")
            return
        
        self.logger.info("Process found. Starting RPC...")

        self.logger.info("Connecting and starting handshake...")
        self.rpc.connect()
        self.logger.info("Connected")

        self.data, self.world_data = fetch_data.fetch_all_data()
        asyncio.get_event_loop().run_until_complete(self.handle_log())


if __name__ == '__main__':
    GenshinRichPresence().main()