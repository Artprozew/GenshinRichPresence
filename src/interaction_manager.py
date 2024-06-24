import logging
import os
from configparser import ConfigParser
from typing import Any, Optional, Union


class InteractionManager:
    def __init__(self, ini_file: str, log_file_name: str):
        self._logger = logging.getLogger(__name__)

        self.ini_file: str = ini_file
        self.log_file_name = log_file_name
        self.config_parser: ConfigParser = ConfigParser()

    def set_ini_option(self, section: str, option: str, value: Any) -> None:
        if not self.config_parser.has_section(section):
            self.config_parser.add_section(section)

        self.config_parser[section][option] = value

        with open(self.ini_file, "w") as file:
            self.config_parser.write(file)

    def get_ini_option(
        self, section: str, option: str, *, message: Optional[str] = None, mode: str = "normal"
    ) -> str:
        if mode not in ["strict", "normal"]:
            raise ValueError(f"Invalid mode: {mode}")

        if not os.path.exists(self.ini_file):
            if mode == "strict":
                raise FileNotFoundError(f'Could not find "{self.ini_file}" file')

        self.config_parser.read(self.ini_file)

        if not self.config_parser.has_section(section) or not self.config_parser.has_option(
            section, option
        ):
            if mode == "strict" or not message:
                raise ValueError(f"Section or Option not found: [{section}] {option}")

            if message:
                print(f"\nCould not find the {option}.")
                response: str = str(
                    self.wait_input_response(f"Please insert the {message}", question=False)
                )
                self.set_ini_option(section, option, response)

        return self.config_parser[section][option]

    def get_check_save_ini(self, section: str, option: str, message: str) -> str:
        self._logger.info("Finding and reading config.ini")
        argument = self.get_ini_option(section, option, message=message, mode="normal")

        self._logger.info("Checking correct directory")
        directory: str = self.check_directory(argument, check_file=self.log_file_name)

        self._logger.info("Saving directory to config.ini")
        self.set_ini_option(section, option, directory)

        return directory

    @staticmethod
    def check_directory(dir: str, *, check_file: Optional[str] = None) -> str:
        if not check_file:
            if os.path.exists(dir):
                return dir
        else:
            if os.path.exists(os.path.join(dir, "d3d11_log.txt")):
                return dir

        content_type: str = "directory" if not check_file else "log"
        response: bool = bool(
            InteractionManager.wait_input_response(
                f'\nThe {content_type} at "{dir}" was not found\n'
                "Would you like to change it now?"
            )
        )
        if response:
            path: str = str(InteractionManager.wait_input_response("\nNew path:", question=False))
            return InteractionManager.check_directory(path, check_file=check_file)

        return dir

    @staticmethod
    def wait_input_response(message: str, *, question: bool = True) -> Union[str, bool]:
        while True:
            print(f"{message}{' (Y/N)' if question else ''}")
            response: str = input(" > ")

            if not response:
                continue

            if not question:
                return response

            response = response.lower()
            if response == "y" or response == "yes":
                return True
            elif response == "n" or response == "no":
                return False

    @classmethod
    def find_folder(cls, folder: str, start: str) -> Optional[str]:
        if not hasattr(cls, "_logger"):
            cls._logger = logging.getLogger(__name__)

        cls._logger.info(f"Finding folder {folder}")
        for root, dirs, _ in os.walk(start):
            if folder in dirs:
                return f"{root}\\{folder}"

        return None
