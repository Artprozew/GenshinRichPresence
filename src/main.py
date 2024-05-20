import os
import time
import re
import json
import logging
import asyncio
from typing import Optional, AsyncGenerator, Any

from pypresence import Presence
import requests
import win32gui
import psutil
import nest_asyncio

nest_asyncio.apply()

class GenshinRichPresence():
    RPC_UPDATE_RATE = 15 # Can have problems with Discord updating if its < 15; Time in milliseconds
    FOCUS_CHANGE_CHECK_RATE = 10

    def __init__(self) -> None:
        self.rpc: Presence = Presence(1234834454569025538, loop=asyncio.new_event_loop())
        self.last_update: float = time.time() + GenshinRichPresence.RPC_UPDATE_RATE
        self.last_char: list[str, str] = ["", "Unknown"]
        self.region: Optional[str] = None
        self.previous_region: Optional[str] = None
        self.last_region = [None, None]
        self.process: psutil.Process = None
        self.updatable: bool = True
        self.inactive: bool = True
        self.details: str | None = None
        self.small_image: str = "unknown"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s")


    def can_update_rpc(self) -> bool:
        return (time.time() - self.last_update) > GenshinRichPresence.RPC_UPDATE_RATE and self.updatable

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

    def get_process(self) -> psutil.Process:
        self.logger.info("Searching for Process...")
        process = None
        for proc in psutil.process_iter():
            if "GenshinImpact.exe" in proc.name():
                process = proc

        if not process:
            self.logger.info("Process not found. Exiting...")
            os.system("pause")
            os.system("exit")

        return proc

    def initialize_data(self) -> tuple:
        self.logger.info("Requesting from endpoint API...")

        path = "assets/characters"
        jsonfile = "/data.json"
        data = None
        world_data = {}

        try:
            req = requests.get("https://genshin.jmp.blue/characters/")
        except requests.exceptions.RequestException:
            if os.path.exists(path + jsonfile):
                with open(path + jsonfile, "r+") as file:
                    data = json.load(file)
        else:
            data = json.loads(req.content)

        if "arlecchino" not in data:
            data.append("arlecchino")
        if "chiori" not in data:
            data.append("chiori")
        if "arataki-itto" in data:
            data.remove("arataki-itto")
            data.append("itto")
        if "hu-tao" in data:
            data.remove("hu-tao")
            data.append("hutao")

        if not os.path.exists(path):
            self.logger.info(f'Directory "{path}" does not exists. Creating one...')
            os.makedirs(path)

        with open(path + jsonfile, "w+") as file:
            self.logger.info("Dumping data to JSON file")
            json.dump(data, file, ensure_ascii=False, indent=4)

        path = "assets/world" # Needs to add validations, etc.
        if os.path.exists(path + jsonfile):
                with open(path + jsonfile, "r+") as file:
                    world_data = json.load(file)

        self.logger.info("Requests complete")
        return data, world_data

    def parse_region(self) -> str:
        tmp = self.region
        tmp = tmp.capitalize()
        tmp = tmp.split('_')
        if len(tmp) == 2:
            tmp[1] = tmp[1].capitalize()
        tmp = ' '.join(tmp)
        return tmp


    async def update_rpc(self) -> None:
        #if not self.can_update_rpc(): return # redundancy
        self.has_changed_focus()

        if not self.details:
            self.details = "On Menus"
        else:
            if self.region:
                if self.region != self.last_region[0]: # If the parsed region name is not in memory
                    if self.region == "liyue" and self.previous_region == "the_chasm": # Assert the chasm gets higher priority
                        self.region = "the_chasm"
                        self.last_region = [self.region, "The Chasm"]

                    parsed_region = self.parse_region()
                    self.details = f"Currently on: {parsed_region}, {'inactive' if self.inactive else 'in-game'}"
                    self.last_region = [self.region, parsed_region]
                else:
                    if self.region == "liyue" and self.previous_region == "the_chasm": # Assert the chasm gets higher priority
                        self.region = "the_chasm"
                        self.last_region = [self.region, "The Chasm"]

                    self.details = f"Currently on: {self.last_region[1]}, {'inactive' if self.inactive else 'in-game'}"

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


    async def tail_file(self, file) -> AsyncGenerator[str, Any]:
        file.seek(0, os.SEEK_END)
        focus_check = time.time()
        while True:
            line = file.readline()
            if not line:
                if (time.time() - focus_check) > GenshinRichPresence.FOCUS_CHANGE_CHECK_RATE: # Not working as expected? Updating too frequently?
                    if self.has_changed_focus(): # Need to periodically check if user isn't alt-tabbed
                        self.updatable = True
                    focus_check = time.time()
                if self.can_update_rpc(): # If there's no new lines, will try to update the last character after 15s, otherwise it would be stopped here
                    await self.update_rpc()
                await asyncio.sleep(0.4)
                continue
            yield line

    async def handle_log(self, data: list, world_data: dict) -> None:
        self.logger.info("Updating presence")
        await self.update_rpc()

        self.logger.info("Opening log file")
        os.chdir(r"D:\Programas\3dmigoto")
        logfile = open(os.curdir + r"\d3d11_log.txt")
        self.logger.info("Log file opened, the loop is now running")

        async for line in self.tail_file(logfile):
            match = re.search(r"TextureOverride\\Mods(.+) matched resource with hash=([a-zA-Z0-9_.-]*)", line)
            if not match: continue

            character = match.group(1).split("\\")[1] # Possible "character", but could be something else
            asset = f"TextureOverride{match.group(1).split('\\')[3]}"
            refactoredchar = character.lower().replace(" ", "-") # Data uses "-" instead of "_"
            self.logger.debug(f"POSSIBLE CHARACTER: {character}, {refactoredchar}, {match.group(0)}")

            for name in data:
                if name.lower().startswith(refactoredchar): # Character confirmed
                    if self.last_char[0] != refactoredchar: # Check if it's not the current character
                        self.last_char = [refactoredchar, character]
                        self.updatable = True
                        self.logger.debug(f"Updated last_char {self.last_char[1]}")
                        break

            for texture, value in world_data.items():
                if texture == asset:
                    if self.previous_region != self.region:
                        self.previous_region = self.region
                    self.region = value[1]
                    self.updatable = True
                    self.logger.debug(f"Updated region to {value[1]}, hash: {value[0]}")
                    break


    def main(self) -> None:
        self.process = self.get_process()
        self.logger.info("Process found. Starting RPC...")

        self.logger.info("Connecting and starting handshake...")
        self.rpc.connect()
        self.logger.info("Connected")

        self.logger.info("Initializing data")
        data, world_data = self.initialize_data()
        self.logger.info("Running Log tail loop")
        asyncio.get_event_loop().run_until_complete(self.handle_log(data, world_data))


def main() -> None:
    GRPC = GenshinRichPresence()
    GRPC.main()

if __name__ == '__main__':
    main()