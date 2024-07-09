import atexit
import logging
import signal
from types import FrameType
from typing import Any, Callable, Optional

import config


def handle_exit_hook(
    function: Callable[[int, Optional[FrameType]], Any],
    signal_number: int,
    stack_frame: Optional[FrameType],
) -> None:
    # Win32
    atexit.register(function, signal_number, stack_frame)

    # Posix
    signal.signal(signal.SIGINT, function)
    signal.signal(signal.SIGTERM, function)


def safe_exit() -> None:
    logging.getLogger(__name__).warning("Stopping program")
    config._program_stop_flag = True
    config._tray_icon.stop()
    # Graceful exits only seems to work if we just stop the tray icon and the log loop
    # i.e. sys.exit(0) would error
