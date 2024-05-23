import os
import json
import logging
from typing import Dict

import requests


def fetch_all_data() -> tuple[list[str], Dict[str, str]]:
    logger = logging.getLogger(__name__)
    logger.info("Requesting data from API endpoint...")

    data: list[str] = []
    world_data: Dict[str, str] = {}

    root_dir: os.PathLike = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir: os.PathLike = os.path.join(root_dir, "data")
    characters_dir: os.PathLike = os.path.join(data_dir, "characters")
    world_dir: os.PathLike = os.path.join(data_dir, "world")

    json_file: os.PathLike = os.path.join(characters_dir, "characters_data.json")
    request: requests.Response
    do_request: bool = True

    try:
        request = requests.get("https://genshin.jmp.blue/characters/") # Tries to get the latest data from API
    except requests.exceptions.RequestException:
        do_request = False

    if not os.path.exists(characters_dir):
        logger.info(f'Directory "{characters_dir}" does not exists. Creating one...')
        os.makedirs(characters_dir)

    if not do_request: # Backup that may be outdated
        logger.info("Couldn't request data from API, getting from already existing file")
        if os.path.exists(json_file):
            with open(json_file, "r+") as file:
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

    with open(json_file, "w+") as file: # May break with auto-py-to-exe?
        logger.info("Dumping data to JSON file") # Saving latest data to JSON file
        json.dump(data, file, ensure_ascii=False, indent=4)


    json_file: os.PathLike = os.path.join(world_dir, "world_data.json")
    if os.path.exists(json_file):
        with open(json_file, "r+") as file:
            world_data = json.load(file)
    else:
        raise(FileNotFoundError(f'File {json_file} does not exists!'))

    logger.info("Requests complete")
    return data, world_data