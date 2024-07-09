import os
import time
import traceback
from typing import Any

import config
from utils.handle_exit import safe_exit


def exception_handler(exc_type: Any, exc_value: Any, tb: Any) -> None:
    with open(os.path.join(config.MAIN_DIRECTORY, "traceback.txt"), "w") as file:
        for line in traceback.format_exception(exc_type, exc_value, tb):
            file.writelines(line)

    traceback.print_exception(exc_type, exc_value, tb)
    time.sleep(5)
    safe_exit()
