import logging
import os
import shutil
from configparser import ConfigParser
from typing import Any, Optional, Union


class InteractionManager:
    def __init__(self, ini_file: str, log_file_name: str):
        self._logger = logging.getLogger(__name__)

        self.ini_file: str = ini_file
        self.log_file_name: str = log_file_name

        # Creates a case-sensitive ConfigParser
        self.config_parser: ConfigParser = ConfigParser()
        self.config_parser.optionxform = lambda option: option  # type: ignore # github.com/python/mypy/issues/5062

    def set_ini_option(self, section: str, option: str, value: Any) -> None:
        if not self.config_parser.has_section(section):
            self.config_parser.add_section(section)

        self.config_parser[section][option] = value

        with open(self.ini_file, "w") as file:
            self.config_parser.write(file)

    def get_ini_settings(
        self, section: str, option: Optional[str] = None, *, mode: str = "normal", type_: type = str
    ) -> Any:
        if mode not in ["strict", "normal"]:
            raise ValueError(f"Invalid mode: {mode}")

        if not os.path.exists(self.ini_file):
            if mode == "strict":
                raise FileNotFoundError(f'Could not find "{self.ini_file}" file')

            open(self.ini_file, "w").close()

        self.config_parser.read(self.ini_file)

        if not self.config_parser.has_section(section):
            if mode == "strict":
                raise ValueError(f"Section not found: {section}")

            return None

        if not option:
            return dict(self.config_parser[section])

        if not self.config_parser.has_option(section, option):
            if mode == "strict":
                raise ValueError(f"Option not found: [{section}]: {option}")

            return None

        if type_ == bool:
            return self.config_parser.getboolean(section, option)
        elif type_ == float:
            return self.config_parser.getfloat(section, option)
        elif type_ == int:
            return self.config_parser.getint(section, option)

        return self.config_parser[section][option]

    def get_environ_or_ini(
        self,
        section: str,
        name: Optional[str],
        default: Optional[Any] = None,
        *,
        check_file: bool = False,
        type_: type = str,
    ) -> Any:
        result: Any = os.getenv(
            name if name else section, self.get_ini_settings(section, name, type_=type_)
        )

        if result is not None:
            if check_file:
                result = self.check_directory(
                    result, check_file="3DMigoto Loader.exe", mode="strict"
                )
            return result

        if default is None:
            raise RuntimeError(
                "Missing required configuration. "
                f"Please set it on your config.ini: [{section}]{': ' + name if name else ''}"
            )

        return default

    @staticmethod
    def check_directory(
        directory: str, *, check_file: Optional[str] = None, mode: str = "normal"
    ) -> str:
        if not check_file:
            if os.path.exists(directory):
                return directory
        else:
            if os.path.exists(os.path.join(directory, check_file)):
                return directory
            elif mode == "strict":
                raise FileNotFoundError(f'The GIMI at "{directory}" was not found')

        content_type: str = "directory" if not check_file else "log"
        response: bool = bool(
            InteractionManager.wait_input_response(
                f'\nThe {content_type} at "{directory}" was not found\n'
                "Would you like to change it now?"
            )
        )
        if response:
            path: str = str(InteractionManager.wait_input_response("\nNew path:", question=False))
            return InteractionManager.check_directory(path, check_file=check_file)

        return directory

    @classmethod
    def find_folder(cls, folder: str, start: str) -> Optional[str]:
        if not hasattr(cls, "_logger"):
            cls._logger = logging.getLogger(__name__)

        cls._logger.info(f"Finding folder {folder} at {start}")
        for root, dirs, _ in os.walk(start):
            if folder in dirs:
                return os.path.join(root, folder)

        return None

    def set_up_rpc_data_folder(
        self, folder_name: str, datas_folder: str, mods_folder: str, copy_data: bool
    ) -> str:
        rpc_folder: Optional[str] = self.find_folder(folder_name, mods_folder)

        if rpc_folder:
            return rpc_folder

        if not copy_data:
            raise FileNotFoundError(
                f"The {folder_name} folder was not found on your GIMI's Mods folder. "
                "Please set COPY_REQUIRED_DATA to True on your config.ini if you're not sure what to do."
            )

        self._logger.info(f"Setting up {folder_name}")

        rpc_folder = os.path.join(mods_folder, folder_name)

        if not os.path.exists(rpc_folder):
            self._logger.info(f"Creating new {folder_name} folder at {rpc_folder}")
            os.mkdir(rpc_folder)

        shutil.copy(
            os.path.join(datas_folder, "characters", "PlayableCharacterData.ini"), rpc_folder
        )
        shutil.copy(os.path.join(datas_folder, "world", "WorldData.ini"), rpc_folder)

        return rpc_folder

    def get_check_save_ini(self, section: str, option: str, *, mode: str = "strict") -> str:
        self._logger.info("Finding and reading config.ini")
        argument: str = str(self.get_ini_settings(section, option, mode=mode))

        self._logger.info("Checking correct directory")
        directory: str = self.check_directory(argument, check_file=self.log_file_name, mode=mode)

        self._logger.info("Saving directory to config.ini")
        self.set_ini_option(section, option, directory)

        return directory

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
