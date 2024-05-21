import os
import json
import logging
from typing import Dict

import requests

logger = logging.getLogger(__name__)

def fetch_all_data() -> tuple[list[str], Dict[str, str]]:
    logger.info("Requesting data from API endpoint...")

    json_file: os.PathLike = "data.json"
    data: list[str] = []
    world_data: Dict[str, str] = {}
    request: requests.Response

    path: os.PathLike = "assets/characters"
    do_request: bool = True

    try:
        request = requests.get("https://genshin.jmp.blue/characters/") # Tries to get the latest data from API
    except requests.exceptions.RequestException:
        do_request = False

    if not os.path.exists(path):
        logger.info(f'Directory "{path}" does not exists. Creating one...')
        os.makedirs(path)

    if not do_request:
        logger.info("Couldn't request data from API, getting from already existing file")
        if os.path.exists(os.path.join(path, json_file)):
            with open(os.path.join(path, json_file), "r+") as file:
                data = json.load(file)
        else:
            raise(RuntimeError("Couldn't get/request any data!"))
    else:
        data = json.loads(request.content)

    if "arataki-itto" in data:
        data.remove("arataki-itto")
        data.append("itto")
    if "hu-tao" in data:
        data.remove("hu-tao")
        data.append("hutao")

    with open(os.path.join(path, json_file), "w+") as file:
        logger.info("Dumping data to JSON file") # Saving latest data to JSON file
        json.dump(data, file, ensure_ascii=False, indent=4)


    path = "assets/world"
    if os.path.exists(os.path.join(path, json_file)):
        with open(os.path.join(path, json_file), "r+") as file:
            world_data = json.load(file)
    else:
        raise(FileNotFoundError(f'File {os.path.join(path, json_file)} does not exists!'))

    logger.info("Requests complete")
    return data, world_data