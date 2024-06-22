from typing import Any
import tempfile
import os
import sys
import traceback


def exception_handler(exc_type: Any, exc_value: Any, tb: Any) -> None:
    with open(f"{tempfile.gettempdir()}\\GenshinRichPresence\\traceback.txt", "w") as file:
        for line in traceback.format_exception(exc_type, exc_value, tb):
            file.writelines(line)

    traceback.print_exception(exc_type, exc_value, tb)
    os.system("pause")
    sys.exit(-1)
