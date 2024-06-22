import psutil
from typing import Optional
import win32gui
import time
import logging


class GameMonitor:
    user_active: bool = True

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

        # wait_for_game() already ran, so it SHOULD find the game process
        self._process = self.find_game_process()
        assert self._process is not None, "Could not find the game process!"

        self._process_create_time = self._process.create_time()

    def is_user_active(self) -> bool:
        return self.user_active

    def get_process_create_time(self) -> float:
        return self._process_create_time

    def get_game_process(self) -> Optional[psutil.Process]:
        return self._process

    @classmethod
    def find_game_process(cls) -> Optional[psutil.Process]:
        for process in psutil.process_iter():
            if "GenshinImpact.exe" in process.name():
                return process

        return None

    @classmethod
    def wait_for_game(cls) -> None:
        if not hasattr(cls, "logger"):
            cls._logger = logging.getLogger(__name__)

        cls._logger.info("Waiting for game process")
        while not cls.find_game_process():
            cls._logger.info("Game process not found, waiting for 3s...")
            time.sleep(3)

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
