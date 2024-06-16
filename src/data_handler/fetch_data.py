import os
import json
import logging
from configparser import ConfigParser

import requests

import config
from data_handler import update_data


def fetch_all_data() -> dict[str, list[str, str]]:
    """Fetches character and/or world data

    Checks updates for the latest character data from an API if necessary and opted-in

    Returns:
        dict: A dictionary containing world data in this form:
            key (str): Texture override name\n
            value (list): A list with two elements:\n
                - texture hash (str)
                - region name (str)
    """
    logger = logging.getLogger(__name__)
    logger.info("Requesting data from API endpoint")

    world_data: dict[str, str] = {}
    request: requests.Response

    if config.ALWAYS_CHECK_FOR_UPDATES:
        response_error: bool = False
        logger.info("Checking for the latest added characters")

        try:
            # Get the latest characters from the GI-Model-Importer-Assets repository as they add new characters early
            request = requests.get("https://api.github.com/repos/SilentNightSound/GI-Model-Importer-Assets/contents/PlayerCharacterData")
        except requests.exceptions.RequestException:
            response_error = True

        if response_error or (request.status_code < 200 and request.status_code > 299):
            logger.warning("Could not request data from the repository")

        if not response_error:
            character_file: os.PathLike = f"{config.GRP_DATA_DIRECTORY}\\PlayableCharacterData.ini"
            data: list[str] = json.loads(request.content)

            if os.path.exists(character_file):
                config_parser = ConfigParser()
                config_parser.read(character_file)

                for object in data:
                    if not config_parser.has_section(f"TextureOverride{object["name"]}VertexLimitRaise"):
                        while True:
                            print(f"\nSeems like the character {object["name"]} was recently added to the game")
                            update_confirm = input("Would you like to update its data? (Y/N) > ").lower()
                            
                            if update_confirm == "y" or update_confirm == "yes":
                                update_data.update_character(object["name"])
                                break
                            elif update_confirm == "n" or update_confirm == "no":
                                break

    json_file: os.PathLike = os.path.join("data", "world", "world_data.json")
    if os.path.exists(json_file):
        with open(json_file, "r+") as file:
            world_data = json.load(file)
    else:
        raise(FileNotFoundError(f'File {json_file} does not exists!'))


    logger.info("Requests complete")
    return world_data
