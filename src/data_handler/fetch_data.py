import os
import json
import logging
from configparser import ConfigParser
from typing import Optional, Any

import requests

import config
from data_handler import update_data

logger: logging.Logger = logging.getLogger(__name__)


def request_characters_update() -> Optional[requests.Response]:
    response_error: bool = False
    logger.info("Checking for the latest added characters")

    try:
        # Get the latest characters from the GI-Model-Importer-Assets repository as they add new characters early
        request = requests.get(
            "https://api.github.com/repos/SilentNightSound/GI-Model-Importer-Assets/contents/PlayerCharacterData"
        )
    except requests.exceptions.RequestException:
        response_error = True

    if response_error or not request or (request.status_code < 200 or request.status_code > 299):
        logger.warning("Could not request data from the repository")
        return None

    return request


def check_characters_updates() -> None:
    request: Optional[requests.Response] = request_characters_update()
    character_file: str = f"{config.GRP_DATA_DIRECTORY}\\PlayableCharacterData.ini"

    if not request or not os.path.exists(character_file):
        return None

    data: list[dict[str, Any]] = json.loads(request.content)
    config_parser = ConfigParser()
    config_parser.read(character_file)

    for obj in data:
        if config_parser.has_section(f"TextureOverride{obj['name']}VertexLimitRaise"):
            continue

        while True:
            print(f"\nSeems like the character {obj['name']} was recently added to the game")
            print("Would you like to update its data? (Y/N)")
            update_confirm = input(" > ").lower()

            if update_confirm == "y" or update_confirm == "yes":
                update_data.update_character(obj["name"])
                break
            elif update_confirm == "n" or update_confirm == "no":
                break


def fetch_all_data() -> None:
    """Fetches character and/or world data

    Checks updates for the latest character data from an API if necessary and opted-in

    Returns:
        dict: A dictionary containing world data in this form:
            key (str): Texture override name\n
            value (list): A list with two elements:\n
                - texture hash (str)
                - region name (str)
    """
    logger.info("Requesting data from API endpoint")

    if config.ALWAYS_CHECK_FOR_UPDATES:
        check_characters_updates()

    logger.info("Requests complete")
