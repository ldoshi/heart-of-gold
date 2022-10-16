import plugin_api
import wyze_sdk


class LightControls(plugin_api.Plugin):
    def __init__(self, wyze_client: wyze_sdk.Client, on_key: str, off_key: str):
        self._wyze_client = wyze_client
        self._on_key = on_key
        self._off_key = off_key
        self._bulbs = self._wyze_client.bulbs.list()

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

    def command(self, command: str) -> None:
        if command == self._on_key:
            self._turn_on()

        if command == self._off_key:
            self._turn_off()

    def reset(self) -> None:
        self._turn_off()
