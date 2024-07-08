import json
import logging
import os
from configparser import ConfigParser
from typing import Any, Optional

import requests

import config
from data_handler import update_data
from utils.data_tools import separate_with

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
    character_file: str = os.path.join(config.GRP_DATA_DIRECTORY, "PlayableCharacterData.ini")

    if not request or not os.path.exists(character_file):
        return None

    data: list[dict[str, Any]] = json.loads(request.content)
    config_parser: ConfigParser = ConfigParser()
    config_parser.read(character_file)

    for obj in data:
        name: str = separate_with(obj["name"], "_")

        if not config_parser.has_section(f"TextureOverride__{name}__VertexLimitRaise"):
            update_data.update_character(obj["name"], character_file)

    logger.info("Done updating characters")
