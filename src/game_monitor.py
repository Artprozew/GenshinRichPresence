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
        if not GameMonitor.process:
            GameMonitor.get_process()

    def get_create_time(self):
        return GameMonitor.process.create_time()

    def is_user_active(self) -> bool:
        return GameMonitor.user_active

    @classmethod
    def get_process(cls) -> Optional[psutil.Process]:
        for proc in psutil.process_iter():
            if "GenshinImpact.exe" in proc.name():
                    GameMonitor.process = proc
                    return proc
            
        return None

    @classmethod
    def wait_for_game(cls):
        logger.info("Searching for game process")
        while not GameMonitor.process:
            GameMonitor.get_process()
            logger.info("Game process not found, waiting for 3s...")
            time.sleep(3)

    def check_changed_focus(self) -> bool:
        changed: bool = GameMonitor.user_active

        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Genshin Impact":  # type: ignore[name-defined, unused-ignore] # Temp. workaround
            GameMonitor.user_active = True
        else:
            GameMonitor.user_active = False

        changed = changed != GameMonitor.user_active
        if changed:
            logger.debug(f"Updated user_active status to {GameMonitor.user_active}")
        return changed
