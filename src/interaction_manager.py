import config
from configparser import ConfigParser
import tempfile
import os


class InteractionManager:
    @classmethod
    def save_ini_file(cls, config_parser: ConfigParser, ini_file: str, game_dir: str) -> None:
        if not os.path.exists(os.path.dirname(ini_file)):
            os.mkdir(os.path.dirname(ini_file))

        if not config_parser.has_section("SETTINGS"):
            config_parser.add_section("SETTINGS")
        config_parser["SETTINGS"]["GIMI_DIRECTORY"] = game_dir

        with open(ini_file, "w") as file:
            config_parser.write(file)

    @classmethod
    def check_gimi_dir(cls) -> str:
        config_parser: ConfigParser = ConfigParser()
        ini_file: str = f"{tempfile.gettempdir()}\\GenshinRichPresence\\config.ini"
        game_dir: str = ""

        if not os.path.exists(ini_file):
            print("\nPlease write here your GIMI directory path")
            game_dir = input(" > ")
            cls.save_ini_file(config_parser, ini_file, game_dir)
            return game_dir

        config_parser.read(ini_file)
        game_dir = config_parser.get("SETTINGS", "GIMI_DIRECTORY")

        print(f"\nGIMI directory found: {game_dir}")
        print("Press ENTER if you wanna keep it. Otherwise, write the new directory")
        response: str = input(" > ")

        if not response:
            config_parser.read(ini_file)
            game_dir = config_parser.get("SETTINGS", "GIMI_DIRECTORY")
        else:
            game_dir = response
            cls.save_ini_file(config_parser, ini_file, game_dir)

        return game_dir
