import json
import os
import sys
from configparser import ConfigParser
from typing import Any, Optional

import requests

try:
    import config
except ImportError:
    pass


def update_character(name: str) -> bool:
    """Gets the latest character data from GI-Model-Importer-Assets repository and writes it in the .ini file.

    Parameters:
        name (str): The name of the character to get data from

    Returns:
        bool: Returns False if anything fails, True otherwise
    """
    request = requests.get(
        f"https://raw.githubusercontent.com/SilentNightSound/GI-Model-Importer-Assets/main/PlayerCharacterData/{name}/hash.json"
    )

    if request.status_code != 200:
        print(f"Something went wrong!\nStatus code: {request.status_code}: {request.reason}")
        os.system("pause")
        return False

    if config.GRP_DATA_DIRECTORY:
        ini_file = f"{config.GRP_DATA_DIRECTORY}\\PlayableCharacterData.ini"
        config_parser = ConfigParser()
        config_parser.read(ini_file)

        texture_name = f"TextureOverride{name}VertexLimitRaise"
        if config_parser.has_section(texture_name):
            print(f"The character {name} is already added!")

            os.system("pause")
            return False

        try:
            hash = json.loads(request.content)[0]["draw_vb"]
            config_parser.add_section(texture_name)
            config_parser[texture_name]["hash"] = hash

            with open(ini_file, "w") as file:
                config_parser.write(file)
        except Exception:
            import traceback

            print(f"Could not add {name} character! Here is the stack trace:")
            traceback.print_exc()

            os.system("pause")
            return False

    print(f'Character "{name}" added')
    return True


def main() -> None:
    """Used as standalone script to update EVERY character data in the RichPresenceData.ini file.

    ## This function will erase and rewrite all existing data in the file.
    """
    grp_dir: str = ""

    if "config" in sys.modules:
        grp_dir = config.GRP_DATA_DIRECTORY

    if not grp_dir:
        print("\nPlease write here the path to the RichPresenceData in your GIMI Mods folder")
        grp_dir = input(" > ")

    if os.path.exists(f"{grp_dir}\\RichPresenceData"):
        grp_dir += f"{grp_dir}\\RichPresenceData"

    if not os.path.exists(grp_dir):
        print("Could not locate the folder")
        os.system("pause")
        return None

    while True:
        print("\nThis will completely erase and rewrite your .ini file with the most recent data.")
        print("It may also take a while (~3 min). Would you like to proceed? (Y/N)")
        response = input(" > ").lower()
        if response == "n" or response == "no":
            return None
        elif response == "y" or response == "yes":
            break

    ini_file: str = f"{grp_dir}\\PlayableCharacterData.ini"

    if os.path.isfile(ini_file):
        os.remove(ini_file)

    request = requests.get(
        "https://api.github.com/repos/SilentNightSound/GI-Model-Importer-Assets/contents/PlayerCharacterData"
    )

    if request.status_code != 200:
        print(f"Something went wrong!\nStatus code: {request.status_code}: {request.reason}")
        os.system("pause")
        return None

    data = json.loads(request.content)

    for object in data:
        update_character(object["name"])

    return None


# If used as standalone script
if __name__ == "__main__":
    main()
