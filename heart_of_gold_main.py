"""Run the ship."""

from typing import List

import collections
import getch
import spotipy
import time
import wyze_sdk

from lighting import light_controls
from pa_system.radio import local_radio

import plugin_api

_RESET_CODE = "qwedcxza"

################################################################################
## Commands
################################################################################

_RADIO_PLAY_KEYS = ["a", "s"]
_RADIO_CHANGE_STATION_PREVIOUS_KEYS = ["q", "w"]
_RADIO_CHANGE_STATION_NEXT_KEYS = ["z", "x"]

_LIGHT_CONTROLS_BED_ROOM_ON_KEY = "r"
_LIGHT_CONTROLS_BED_ROOM_OFF_KEY = "f"
_LIGHT_CONTROLS_LIVING_ROOM_ON_KEY = "e"
_LIGHT_CONTROLS_LIVING_ROOM_OFF_KEY = "d"
_LIGHT_CONTROLS_LIVING_ROOM_COLOR_NEXT_KEY = "c"
_LIGHT_CONTROLS_LIVING_ROOM_COLOR_LIST = [
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=3800),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="ff0000"),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="ffff00"),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="00ff00"),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="0000ff"),
]

################################################################################
## Radio Constants
################################################################################

_RADIO_STATIONS_DIRECTORY = (
    "/home/lyric/Documents/heart-of-gold/pa_system/radio/stations"
)

# Spotify access.
_RADIO_SPOTIPY_CLIENT_ID = "ENTER HERE"
_RADIO_SPOTIPY_CLIENT_SECRET = "ENTER HERE"
_RADIO_SPOTIPY_REDIRECT_URI = "http://localhost"
_RADIO_SPOTIFY_SCOPE = [
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing",
    "playlist-read-private",
    "playlist-read-collaborative",
    "app-remote-control",
    "streaming",
    "user-library-read",
]

# Spotify player.
_RADIO_SPOTIFY_DEVICE_ID = "ENTER HERE"

################################################################################
## Light Controls Constants
################################################################################

_LIGHT_CONTROLS_BED_ROOM_NICKNAME_PREFIX = "bed_room"
_LIGHT_CONTROLS_LIVING_ROOM_NICKNAME_PREFIX = "living_room"

_LIGHT_CONTROLS_EMAIL = "ENTER HERE"
_LIGHT_CONTROLS_PASSWORD = "ENTER HERE"


def _beep() -> None:
    for _ in range(5):
        print("\a")
        time.sleep(0.4)


def _create_radio_plugin() -> plugin_api.Plugin:
    spotify_client = spotipy.Spotify(
        auth_manager=spotipy.oauth2.SpotifyOAuth(
            client_id=_RADIO_SPOTIPY_CLIENT_ID,
            client_secret=_RADIO_SPOTIPY_CLIENT_SECRET,
            redirect_uri=_RADIO_SPOTIPY_REDIRECT_URI,
            scope=_RADIO_SPOTIFY_SCOPE,
        )
    )

    def get_stations() -> List[local_radio.Station]:
        stations = []
        stations.extend(
            local_radio.create_directory_stations(_RADIO_STATIONS_DIRECTORY)
        )
        stations.extend(
            local_radio.create_spotify_stations(
                spotify_client, _RADIO_SPOTIFY_DEVICE_ID
            )
        )
        return stations

    return local_radio.Radio(
        get_stations_fn=get_stations,
        play_keys=_RADIO_PLAY_KEYS,
        change_station_previous_keys=_RADIO_CHANGE_STATION_PREVIOUS_KEYS,
        change_station_next_keys=_RADIO_CHANGE_STATION_NEXT_KEYS,
    )


def _create_light_controls_plugins() -> List[plugin_api.Plugin]:
    wyze_client = wyze_sdk.Client(
        email=_LIGHT_CONTROLS_EMAIL, password=_LIGHT_CONTROLS_PASSWORD
    )
    return [
        light_controls.LightControls(
            wyze_client=wyze_client,
            nickname_prefix=_LIGHT_CONTROLS_BED_ROOM_NICKNAME_PREFIX,
            on_key=_LIGHT_CONTROLS_BED_ROOM_ON_KEY,
            off_key=_LIGHT_CONTROLS_BED_ROOM_OFF_KEY,
        ),
        light_controls.LightControls(
            wyze_client=wyze_client,
            nickname_prefix=_LIGHT_CONTROLS_LIVING_ROOM_NICKNAME_PREFIX,
            on_key=_LIGHT_CONTROLS_LIVING_ROOM_ON_KEY,
            off_key=_LIGHT_CONTROLS_LIVING_ROOM_OFF_KEY,
            color_next_key=_LIGHT_CONTROLS_LIVING_ROOM_COLOR_NEXT_KEY,
            color_list=_LIGHT_CONTROLS_LIVING_ROOM_COLOR_LIST,
        ),
    ]


class Bridge:
    def __init__(self, reset_code: str):
        self._plugins = []
        self._reset_code = collections.deque(reset_code)
        self._command_buffer = collections.deque([None] * len(self._reset_code))

    def register(self, plugin: plugin_api.Plugin) -> None:
        self._plugins.append(plugin)

    def _reset_requested(self, command: str) -> bool:
        self._command_buffer.popleft()
        self._command_buffer.append(command)
        return self._command_buffer == self._reset_code

    def run(self):
        while True:
            try:
                command = getch.getch().lower()

                if self._reset_requested(command):
                    for plugin in self._plugins:
                        plugin.reset()
                    _beep()
                    continue

                for plugin in self._plugins:
                    plugin.command(command)

            except Exception as e:
                print(e)


def main():
    bridge = Bridge(reset_code=_RESET_CODE)
    bridge.register(_create_radio_plugin())
    for light_control_plugin in _create_light_controls_plugins():
        bridge.register(light_control_plugin)
    bridge.run()


if __name__ == "__main__":
    while True:
        main()
