import logging
import os
import subprocess
import sys
import time
from typing import Optional

import psutil

import config

# Windows-only
if sys.platform != "linux" and sys.platform != "darwin":
    import win32gui


class GameMonitor:
    user_active: bool = False

    def __init__(self) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)

    def set_game_process(self) -> None:
        # wait_for_game() already ran, so it SHOULD find the game process now
        process: Optional[psutil.Process] = self.find_game_process(config.GAME_PROCESS_NAME)
        assert process is not None, "Could not find the game process"

        self._process: psutil.Process = process
        self._logger.info(f"Game process with PID {self._process.pid} found")

        self._process_create_time: float = self._process.create_time()

    def is_user_active(self) -> bool:
        return self.user_active

    def get_process_create_time(self) -> float:
        return self._process_create_time

    def is_process_running(self) -> bool:
        return self._process.is_running()

    def get_game_process(self) -> psutil.Process:
        return self._process

    @staticmethod
    def find_game_process(name: str) -> Optional[psutil.Process]:
        for process in psutil.process_iter():
            if name in process.name():
                return process

        return None

    @classmethod
    def wait_for_game(cls, game_name: str) -> bool:
        if not hasattr(cls, "_logger"):
            cls._logger = logging.getLogger(__name__)

        tries: int = 0
        cls._logger.info("Waiting for game process")

        while not cls.find_game_process(game_name):
            if tries >= 20 or config._program_stop_flag:
                cls._logger.debug("Game process was not found. exiting")
                return False

            cls._logger.warning("Game process not found, waiting for 3s...")
            tries += 1
            time.sleep(3)

        return True

    def check_changed_focus(self) -> bool:
        changed: bool = self.user_active

        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Genshin Impact":  # type: ignore[name-defined, unused-ignore] # Temp. workaround
            self.user_active = True
        else:
            self.user_active = False

        changed = changed != self.user_active

        if changed:
            self._logger.debug(f"Updated user_active status to {self.user_active}")

        return changed

    def run_game_and_gimi(self) -> None:
        if not self.find_game_process(config.GAME_PROCESS_NAME):
            # Work-aroundy: remove the log, start GIMI and the game, waits until GIMI creates another log file
            # Otherwise, it would read an old log, GIMI would write over it and it would bug
            log_file: str = os.path.join(config.GIMI_DIRECTORY, config.GIMI_LOG_NAME)

            if os.path.exists(log_file):
                os.remove(log_file)

            self._logger.info("Starting GIMI")
            subprocess.Popen(
                os.path.join(config.GIMI_DIRECTORY, "3DMigoto Loader.exe"),
                start_new_session=True,
                shell=True,
                cwd=config.GIMI_DIRECTORY,
                stdout=subprocess.DEVNULL,
            )

            self._logger.info("Starting game")
            subprocess.Popen(
                config.GAME_EXE_PATH,
                start_new_session=True,
                shell=True,
                cwd=os.path.dirname(config.GAME_EXE_PATH),
                stdout=subprocess.DEVNULL,
            )
