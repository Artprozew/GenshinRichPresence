import logging
import re
import time
from types import FrameType
from typing import Any, Final, Union

import pypresence

import config
from config import configRPC_characters, configRPC_configs, configRPC_regions
from game_monitor import GameMonitor
from utils import handle_exit


class DiscordRichPresence(pypresence.Presence):
    start: int = 0

    state: str = "Unknown"
    details: str = "Unknown"

    large_image: str = "genshin"
    small_image: str = "genshin"
    large_text: str = "Genshin Impact"
    small_text: str = "Unknown"

    previous_region: str = "Unknown"
    current_region: str = "Unknown"
    current_character: str = "Unknown"
    current_weapon: str = "Unknown"

    game_name: Final[str] = "Genshin Impact"
    game_image: Final[str] = "genshin"

    last_update: float = time.time() - 10000
    updatable: bool = True

    def __init__(self, game_monitor: GameMonitor) -> None:
        super().__init__(config.APP_ID)
        self._logger: logging.Logger = logging.getLogger(__name__)
        handle_exit.handle_exit_hook(self._teardown, 0, None)

        self.game_monitor: GameMonitor = game_monitor
        self.connected = False

        self.rpc_configs: dict[str, list[Any]] = {
            "large_image": [configRPC_configs["large_image"], []],
            "large_text": [configRPC_configs["large_text"], []],
            "small_image": [configRPC_configs["small_image"], []],
            "small_text": [configRPC_configs["small_text"], []],
            "state": [configRPC_configs["state"], []],
            "details": [configRPC_configs["details"], []],
        }
        self.pre_parse_configs()

    def _teardown(self, _signal_number: int, _stack_frame: Union[FrameType, None]) -> None:
        if self.connected:
            self._logger.warning("Clearing Rich Presence")

            try:
                self.clear()
            except pypresence.exceptions.PipeClosed:
                pass

            self.connected = False

    def connect(self) -> None:
        self._logger.info("Connecting Rich Presence")
        self.update_event_loop(pypresence.utils.get_event_loop())
        self.loop.run_until_complete(self.handshake())
        self.connected = True

    def can_update_rpc(self) -> bool:
        if (time.time() - self.last_update) > config.RPC_UPDATE_RATE:
            return self.game_monitor.check_changed_focus() or self.updatable

        return False

    def set_last_update(self) -> None:
        self.last_update = time.time()

    def is_user_active(self) -> str:
        return "in-game" if self.game_monitor.is_user_active() else "inactive"

    def pre_parse_configs(self) -> None:
        variables: dict[str, str] = {
            "character": "current_character",
            "character_image": "character_image",
            "region": "current_region",
            "region_image": "region_image",
            "game_name": "game_name",
            "game_image": "game_image",
            "user_activity": "self.is_user_active",
        }
        compiled_regex: re.Pattern[str] = re.compile(r"%\((.*?)\)")

        for name in configRPC_configs.keys():
            matches: list[str] = re.findall(compiled_regex, configRPC_configs[name])

            for match in matches:
                if match not in variables.keys():
                    raise ValueError(f"{name}: {match} is not a valid variable")

                self.rpc_configs[name][0] = self.rpc_configs[name][0].replace(f"%({match})", "{}")
                self.rpc_configs[name][1].append(variables[match])

    def get_parsed_configs(self, name: str) -> Union[str, Any]:
        all_attrib: list[str] = []

        for attribute in self.rpc_configs[name][1]:
            if attribute == "character_image":
                if self.current_character in configRPC_characters:
                    all_attrib.append(configRPC_characters[self.current_character])
                else:
                    all_attrib.append("_".join(self.current_character.split()).lower())
            elif attribute == "region_image":
                if self.current_region in configRPC_regions:
                    all_attrib.append(configRPC_regions[self.current_region])
                else:
                    all_attrib.append("None")
            elif attribute == "self.is_user_active":
                all_attrib.append(self.is_user_active())
            else:
                all_attrib.append(getattr(self, attribute))

        return self.rpc_configs[name][0].format(*all_attrib)

    def update_rpc(self) -> None:
        self.game_monitor.check_changed_focus()

        # Workaround: Fixes the incorrect displayed region as Liyue when the player is on The Chasm
        # Issue #27: https://github.com/Artprozew/GenshinRichPresence/issues/27
        if self.current_region == "Liyue" and self.previous_region == "The Chasm":
            self._logger.debug("Setting region as the_chasm instead of liyue to workaround #27")
            self.current_region = "The Chasm"

        try:
            self.update(
                start=self.game_monitor.get_process_create_time(),
                state=self.get_parsed_configs("state"),
                details=self.get_parsed_configs("details"),
                large_image=self.get_parsed_configs("large_image"),
                small_image=self.get_parsed_configs("small_image"),
                large_text=self.get_parsed_configs("large_text"),
                small_text=self.get_parsed_configs("small_text"),
            )
        except pypresence.exceptions.PipeClosed:
            self.connect()

        self.set_last_update()
        self.updatable = False
        self._logger.debug("RPC Updated")
