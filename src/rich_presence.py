import config
import time
import pypresence
import logging
from game_monitor import GameMonitor
class DiscordRichPresence(pypresence.Presence):
    start = 0
    state = "Unknown"
    details = "Unknown"
    large_image = "Unknown"
    small_image = "Unknown"
    large_text = "Unknown"
    small_text = "Unknown"
    previous_region = "Unknown"
    current_region = "Unknown"
    current_character = "Unknown"
    updatable = False

    def __init__(self) -> None:
        super().__init__(config.APP_ID)
        self._logger = logging.getLogger(__name__)

        self.connect()
        self.game_monitor = GameMonitor()
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

        is_user_active = "In-Game" if self.game_monitor.is_user_active() else "Inactive"
        self.details = f"{is_user_active}. Exploring {self.current_region}"

        self.update(
            start=self.game_monitor.get_create_time(),  # type: ignore # Needs rework of class and better logic with None
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
