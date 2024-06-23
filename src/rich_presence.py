import config
import time
import pypresence
import logging
from game_monitor import GameMonitor
from utils import handle_exit
from typing import Final, Optional
from types import FrameType


class DiscordRichPresence(pypresence.Presence):
    start: int = 0
    state: str = "Unknown"
    details: str = "Unknown"
    large_image: str = "Unknown"
    small_image: str = "Unknown"
    large_text: str = "Unknown"
    small_text: str = "Unknown"
    previous_region: str = "Unknown"
    current_region: str = "Unknown"
    current_character: str = "Unknown"
    updatable: bool = False

    def __init__(self, game_monitor: GameMonitor) -> None:
        super().__init__(config.APP_ID)
        self._logger: logging.Logger = logging.getLogger(__name__)

        self.game_monitor: GameMonitor = game_monitor
        handle_exit.handle_exit_hook(self._teardown, 0, None)

    def _teardown(self, _signal_number: int, _stack_frame: Optional[FrameType]) -> None:
        self._logger.warning("Clearing Rich Presence")
        self.clear()

    def can_update_rpc(self) -> bool:
        if (time.time() - self.last_update) > config.RPC_UPDATE_RATE:
            return self.game_monitor.check_changed_focus() or self.updatable

        return False

    def set_last_update(self) -> None:
        self.last_update = time.time()

    def update_rpc(self) -> None:
        self.game_monitor.check_changed_focus()

        if not self.details or not self.current_region:
            self.details = "On Menus"

        # Workaround: Fixes the incorrect displayed region as Liyue when the player is on The Chasm
        # Issue #27: https://github.com/Artprozew/GenshinRichPresence/issues/27
        if self.current_region == "Liyue" and self.previous_region == "The Chasm":
            self._logger.debug("Setting region as the_chasm instead of liyue to workaround #27")
            self.current_region = "The Chasm"

        is_user_active: Final[str] = "In-Game" if self.game_monitor.is_user_active() else "Inactive"
        self.details = f"{is_user_active}. Exploring {self.current_region}"

        self.update(
            start=self.game_monitor.get_process_create_time(),
            state=f"Playing as {self.current_character}",
            details=self.details,
            large_image="genshin",
            small_image=self.small_image,
            large_text="Genshin Impact",
            small_text=self.current_character,
        )

        self.set_last_update()
        self.updatable = False
        self._logger.debug("RPC Updated")
