import psutil
from typing import Optional
import win32gui
import time
import logging

logger = logging.getLogger(__name__)


class GameMonitor:
    user_active = True
    create_time = 0
    process = None

    def __init__(self) -> None:
        if not self.process:

    def get_create_time(self):
        return self.process.create_time()

    def is_user_active(self) -> bool:
        return self.user_active

    @classmethod
    def get_process(cls) -> Optional[psutil.Process]:
        for process in psutil.process_iter():
            if "GenshinImpact.exe" in process.name():
                    cls.process = process
                    return process
            
        return None

    @classmethod
    def wait_for_game(cls):
        cls.logger.info("Waiting for game process")
        while not cls.get_process():
            cls.logger.info("Game process not found, waiting for 3s...")
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
