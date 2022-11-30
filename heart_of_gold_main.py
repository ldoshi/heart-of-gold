"""Run the ship."""

from typing import Callable, List

import collections
import datetime
import functools
import spotipy
import pynput
import threading
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

_SECONDS_IN_A_DAY = 60 * 60 * 24


class DailyTaskManager:
    def __init__(self):
        self._tasks = []
        self._timer = None
        self._is_running = False

    def _run_tasks(self) -> None:
        for task in self._tasks:
            task()

        self._is_running = False
        self.start()

    def start(self) -> None:
        if not self._is_running:
            self._timer = threading.Timer(_SECONDS_IN_A_DAY, self._run_tasks)
            self._timer.start()
            self._is_running = True

    def add_task(self, task: Callable) -> None:
        self._tasks.append(task)


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


def _refresh_wyze_client_token(wyze_client: wyze_sdk.Client) -> None:
    response = wyze_client.refresh_token()
    wyze_client._token = response["data"]["access_token"]
    wyze_client._refresh_token = response["data"]["refresh_token"]


def _create_light_controls_plugins(
    daily_task_manager: DailyTaskManager,
) -> List[plugin_api.Plugin]:
    wyze_client = wyze_sdk.Client(
        email=_LIGHT_CONTROLS_EMAIL, password=_LIGHT_CONTROLS_PASSWORD
    )
    daily_task_manager.add_task(
        functools.partial(_refresh_wyze_client_token, wyze_client)
    )
    return [
        light_controls.LightControls(
            wyze_client=wyze_client,
            nickname_prefix=_LIGHT_CONTROLS_BED_ROOM_NICKNAME_PREFIX,
            on_key=_LIGHT_CONTROLS_BED_ROOM_ON_KEY,
            off_key=_LIGHT_CONTROLS_BED_ROOM_OFF_KEY,
            active_time_start=datetime.time(4, 0, 0),
            active_time_end=datetime.time(20, 30, 0),
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

    def command(self, key: str):
        try:
            command = key.char.lower()
            if self._reset_requested(command):
                for plugin in self._plugins:
                    plugin.reset()
                _beep()
                return

            for plugin in self._plugins:
                if plugin.is_active():
                    plugin.command(command)

        except Exception as e:
            print(e)


def main():
    bridge = Bridge(reset_code=_RESET_CODE)
    daily_task_manager = DailyTaskManager()
    bridge.register(_create_radio_plugin())
    for light_control_plugin in _create_light_controls_plugins(daily_task_manager):
        bridge.register(light_control_plugin)

    daily_task_manager.start()
    with pynput.keyboard.Listener(on_release=bridge.command) as listener:
        listener.join()


if __name__ == "__main__":
    while True:
        main()
