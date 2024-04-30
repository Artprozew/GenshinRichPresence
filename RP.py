import os
import psutil
import time
import re
from pypresence import Presence
import urllib.request
import json
import requests
import logging
import asyncio
import nest_asyncio
import threading

nest_asyncio.apply()

class GenshinRichPresence():
    def __init__(self) -> None:
        self.rpc = Presence(1234834454569025538, loop=asyncio.new_event_loop())
        self.last_update = time.time()
        self.last_char = None
        self.process = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_process(self) -> psutil.Process:
        self.logger.info("Searching for Process...")
        process = None
        for proc in psutil.process_iter():
            if "GenshinImpact.exe" in proc.name():
                process = proc
            #if "3DMigoto Loader.exe" in proc.name(): # Needs a way to detect if 3DMigoto is also running
            #    self.logger.info("Process found")

        if not process:
            self.logger.info("Process not found. Exiting...")
            os.system("pause")
            os.system("exit")

        return proc
    
    def initialize_data(self) -> dict:
        self.logger.info("Requesting from endpoint API...")

        path = "assets/characters"
        jsonfile = "/data.json"
        data = None

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

        if not os.path.exists(path):
            self.logger.info(f'Directory "{path}" does not exists. Creating one...')
            os.makedirs(path)

        with open(path + jsonfile, "w+") as file:
            self.logger.info("Dumping data to JSON file.")
            json.dump(data, file, ensure_ascii=False, indent=4)

        self.logger.info("Requests complete")
        return data
    
    
    async def tail_file(self, file) -> any:
        file.seek(0, os.SEEK_END)
        while True:
            line = file.readline()
            if not line:
                if (time.time() - self.last_update) > 15: # If there's no new lines, will try to update the last character, otherwise it would be stopped here
                    if self.last_char:
                        self.logger.info(f"Last char atualizado com sucesso apos cooldown {self.last_char[1]} (AFK)")
                        self.rpc.update(start=self.process.create_time(), state=f"Playing as {self.last_char[1]}", large_image="genshin", small_image=self.last_char[0].replace("-", "_"), large_text="Genshin Impact", small_text=self.last_char[1])
                        self.last_char = None
                        self.last_update = time.time()
                await asyncio.sleep(0.4)
                continue
            yield line

    async def handle_log(self, data: dict) -> None:
        os.chdir(r"D:\Programas\3dmigoto")
        self.logger.info("Last char definido")
        logfile = open(os.curdir + r"\d3d11_log.txt")

        async for line in self.tail_file(logfile):
            match = re.match(r"\s+?TextureOverride\\Mods(.+)\\(.+) matched resource with hash=([a-zA-Z0-9_.-]*) type", line)
            if not match:
                if self.last_char: # Didn't update any new character, but there's still one update pending from earlier when it was on cooldown
                    if (time.time() - self.last_update) > 10:
                        self.logger.info(f"Last char atualizado com sucesso apos cooldown {self.last_char[1]}")
                        self.rpc.update(start=self.process.create_time(), state=f"Playing as {self.last_char[1]}", large_image="genshin", small_image=self.last_char[0].replace("-", "_"), large_text="Genshin Impact", small_text=self.last_char[1])
                        self.last_char = None
                        self.last_update = time.time()
                continue

            char = match.group(1).split("\\")[1] # Possible "character", but could be something else
            refactoredchar = char.lower().replace(" ", "-") # Data uses "-" instead of "_"
            for i in data:
                if i.lower().startswith(refactoredchar): # Character confirmed
                    if (time.time() - self.last_update) > 10:
                        self.rpc.update(start=self.process.create_time(), state=f"Playing as {char}", large_image="genshin", small_image=refactoredchar.replace("-", "_"), large_text="Genshin Impact", small_text=char)
                        #last_char = None
                        self.last_update = time.time()
                        print(char)
                        break
                    else:
                        self.last_char = [refactoredchar, char] # Found character, but needs to wait cooldown
                        self.logger.info(f"Last char atualizado {self.last_char[1]}")
                        break


    def main(self) -> None:
        self.process = self.get_process()
        self.logger.info("Process found. Starting RPC...")

        self.logger.info("Connecting and starting handshake...")
        self.rpc.connect()
        self.logger.info("Connected")

        self.logger.info("Initializing data")
        data = self.initialize_data()
        asyncio.get_event_loop().run_until_complete(self.handle_log(data))



def main():
    GRPC = GenshinRichPresence()
    GRPC.main()

if __name__ == '__main__':
    main()