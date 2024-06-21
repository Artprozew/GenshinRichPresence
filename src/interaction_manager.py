import config
from configparser import ConfigParser
import tempfile
import os


class InteractionManager:
    def save_ini_file(self, config_parser: ConfigParser, ini_file: str) -> None:
        if not os.path.exists(os.path.dirname(ini_file)):
            os.mkdir(os.path.dirname(ini_file))

        if not config_parser.has_section("SETTINGS"):
            config_parser.add_section("SETTINGS")
        config_parser["SETTINGS"]["GIMI_DIRECTORY"] = config.GIMI_DIRECTORY

        with open(ini_file, "w") as file:
            config_parser.write(file)

    @classmethod
    def check_gimi_dir(cls) -> None:
        config_parser = ConfigParser()
        ini_file: str = f"{tempfile.gettempdir()}\\GenshinRichPresence\\config.ini"

        if not os.path.exists(ini_file):
            print("\nPlease write here your GIMI directory path")
            config.GIMI_DIRECTORY = input(" > ")
            cls.save_ini_file(config_parser, ini_file)
            return
        
        config_parser.read(ini_file)
        config.GIMI_DIRECTORY = config_parser.get("SETTINGS", "GIMI_DIRECTORY")

        print(f"\nGIMI directory found: {config.GIMI_DIRECTORY}")
        print("Press ENTER if you wanna keep it. Otherwise, write the new directory")
        answer = input(" > ")

        if not answer:
            config_parser.read(ini_file)
            config.GIMI_DIRECTORY = config_parser.get("SETTINGS", "GIMI_DIRECTORY")
        else:
            config.GIMI_DIRECTORY = answer
            cls.save_ini_file(config_parser, ini_file)
