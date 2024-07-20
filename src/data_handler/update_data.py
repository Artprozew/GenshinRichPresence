import json
import os
import sys
import time
from configparser import ConfigParser
from typing import Any, Optional

import requests

try:
    import config
    from utils.data_tools import separate_with
except ImportError:
    # Work-around: Duplicate code from utils.data_tools
    def separate_with(string: str, separator: str) -> str:
        names: list[str] = []
        lowercases: str = ""
        uppercase: str = ""

        for idx, char in enumerate(string):
            if char.isupper():
                if idx != 0 and string[idx - 1] == uppercase:
                    lowercases += char
                    continue

                if lowercases:
                    names.append(f"{uppercase}{lowercases}")

                lowercases = ""
                uppercase = char
            else:
                lowercases += char

        names.append(f"{uppercase}{lowercases}")
        string = separator.join(names)

        return string


def update_character(name: str, ini_file: str) -> bool:
    """Gets the latest character data from GI-Model-Importer-Assets repository and writes it in the .ini file.

    Parameters:
        name (str): The name of the character to get data from
        ini_file (str): Path to the .ini file where it will store the data

    Returns:
        bool: Returns False if anything fails, True otherwise
    """
    url: str = (
        f"https://raw.githubusercontent.com/SilentNightSound/GI-Model-Importer-Assets/main/PlayerCharacterData/{name}/hash.json"
    )
    response_error: bool = False

    try:
        request: requests.Response = requests.get(url)
    except requests.exceptions.RequestException:
        response_error = True

    if response_error or not request or (request.status_code < 200 or request.status_code > 299):
        print(f"Could not request data from {url}")
        print(f"Status code: {request.status_code}: {request.reason}")
        return False

    config_parser: ConfigParser = ConfigParser()
    config_parser.read(ini_file)

    name = separate_with(name, "_")

    texture_name: str = f"TextureOverride__{name}__VertexLimitRaise"

    if config_parser.has_section(texture_name):
        print(f"The character {name} is already added. Skipping...")

        time.sleep(2)
        return False

    try:
        vb_hash = json.loads(request.content)[0]["draw_vb"]
        config_parser.add_section(texture_name)
        config_parser[texture_name]["hash"] = vb_hash

        with open(ini_file, "w") as file:
            config_parser.write(file)
    except Exception:
        import traceback

        print(f"Could not add the character {name}\nStack trace:")
        traceback.print_exc()

        time.sleep(2)
        return False

    print(f'The character "{name}" was added')
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

    if os.path.exists(os.path.join(grp_dir, "RichPresenceData")):
        grp_dir = os.path.join(grp_dir, "RichPresenceData")

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

    print("\nFinding characters to add\n")
    ini_file = os.path.join(grp_dir, "PlayableCharacterData.ini")

    if os.path.isfile(ini_file):
        os.remove(ini_file)

    data = get_data(
        "https://api.github.com/repos/SilentNightSound/GI-Model-Importer-Assets/contents/PlayerCharacterData"
    )

    if not data:
        return

    for obj in data:
        update_character(obj["name"], ini_file)

    print("Done")


def get_data(url: str) -> Optional[Any]:
    response_error: bool = False

    try:
        request = requests.get(url)
    except requests.exceptions.RequestException:
        response_error = True

    if response_error or not request or (request.status_code < 200 or request.status_code > 299):
        print(f"Could not request data from {url}")
        print(f"Status code: {request.status_code}: {request.reason}")
        return None

    try:
        data: Any = json.loads(request.content)
    except ValueError:
        print(f"Error deserializing json for {url}")
        return None

    return data


# If used as standalone script
if __name__ == "__main__":
    main()
