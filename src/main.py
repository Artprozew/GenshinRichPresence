import logging.config
from log_monitor import LogMonitor
from interaction_manager import InteractionManager
from utils.exception_manager import exception_handler
import sys
from game_monitor import GameMonitor
import config
import os
import logging


if os.path.exists("logging.conf"):
    logging.config.fileConfig("logging.conf")
else:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(module)s (%(levelname)s): %(message)s",
    )

logger = logging.getLogger(__name__)


class GenshinRichPresence:
    def start(self) -> None:
        sys.excepthook = exception_handler
        InteractionManager.check_gimi_dir()
        GameMonitor.wait_for_game()
        LogMonitor(os.path.join(config.GIMI_DIRECTORY, "d3d11_log.txt")).start()


if __name__ == "__main__":
    GenshinRichPresence().start()
