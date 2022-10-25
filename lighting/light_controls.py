from typing import List, NamedTuple, Optional, Union

import enum
import plugin_api
import wyze_sdk


class ColorType(enum.Enum):
    COLOR = 1
    TEMPERATURE = 2


class LightingColor(NamedTuple):
    type: ColorType
    value: Union[int, str]


class LightControls(plugin_api.Plugin):
    def __init__(
        self,
        wyze_client: wyze_sdk.Client,
        nickname_prefix: str,
        on_key: str,
        off_key: str,
        color_next_key: Optional[str] = None,
        color_list: Optional[List[LightingColor]] = None,
    ):
        self._wyze_client = wyze_client
        self._on_key = on_key
        self._off_key = off_key

        self._color_next_key = color_next_key
        self._color_list = color_list
        self._color_list_index = 0

        self._bulbs = [
            bulb
            for bulb in self._wyze_client.bulbs.list()
            if bulb.nickname.startswith(nickname_prefix)
        ]

    def _turn_on(self) -> None:
        for bulb in self._bulbs:
            self._wyze_client.bulbs.turn_on(
                device_mac=bulb.mac, device_model=bulb.product.model
            )

    def _turn_off(self) -> None:
        for bulb in self._bulbs:
            self._wyze_client.bulbs.turn_off(
                device_mac=bulb.mac, device_model=bulb.product.model
            )

    def _next_color(self) -> None:
        self._color_list_index = (self._color_list_index + 1) % len(self._color_list)
        lighting_color = self._color_list[self._color_list_index]
        if lighting_color.type == ColorType.COLOR:
            for bulb in self._bulbs:
                self._wyze_client.bulbs.set_color(
                    device_mac=bulb.mac,
                    device_model=bulb.product.model,
                    color=lighting_color.value,
                )
            return

        if lighting_color.type == ColorType.TEMPERATURE:
            for bulb in self._bulbs:
                self._wyze_client.bulbs.set_color_temp(
                    device_mac=bulb.mac,
                    device_model=bulb.product.model,
                    color_temp=lighting_color.value,
                )
            return

    def command(self, command: str) -> None:
        if command == self._on_key:
            self._turn_on()

        if command == self._off_key:
            self._turn_off()

        if self._color_next_key is not None and command == self._color_next_key:
            self._next_color()

    def reset(self) -> None:
        self._turn_off()
