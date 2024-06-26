import signal
import atexit
import sys
from typing import Callable, Any, Optional
from types import FrameType


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
    sys.exit(0)
