"""Run the ship."""

from typing import List

import collections
import getch
import spotipy
import time

from pa_system.radio import local_radio
import plugin_api

_RESET_CODE = "qwedcxza"

################################################################################
## Commands
################################################################################

_RADIO_PLAY_KEYS = ['a', 's', 'd']
_RADIO_CHANGE_STATION_PREVIOUS_KEYS = ['q', 'w', 'e']
_RADIO_CHANGE_STATION_NEXT_KEYS = ['z', 'x', 'c']

################################################################################
## Radio Constants 
################################################################################

_RADIO_STATIONS_DIRECTORY = "/home/lyric/Documents/heart-of-gold/pa_system/radio/stations"

# Spotify access.
_RADIO_SPOTIPY_CLIENT_ID='ENTER HERE'
_RADIO_SPOTIPY_CLIENT_SECRET='ENTER HERE'
_RADIO_SPOTIPY_REDIRECT_URI='http://localhost'
_RADIO_SPOTIFY_SCOPE = ["user-modify-playback-state", "user-read-playback-state", "user-read-currently-playing", "playlist-read-private", "playlist-read-collaborative", "app-remote-control", "streaming", "user-library-read"]

# Spotify player.
_RADIO_SPOTIFY_DEVICE_ID = "ENTER HERE"

def _beep() -> None:
    for _ in range(5):
        print('\a')
        time.sleep(.4)


def _create_radio_plugin() -> plugin_api.Plugin:
    # spotify_client = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(
    #     client_id=_RADIO_SPOTIPY_CLIENT_ID,
    #     client_secret=_RADIO_SPOTIPY_CLIENT_SECRET,
    #     redirect_uri=_RADIO_SPOTIPY_REDIRECT_URI,
    #     scope=_RADIO_SPOTIFY_SCOPE))

    def get_stations() -> List[local_radio.Station]:
        stations = []
        stations.extend(local_radio.create_directory_stations(_RADIO_STATIONS_DIRECTORY))
#        stations.extend(local_radio.create_spotify_stations(spotify_client, _RADIO_SPOTIFY_DEVICE_ID))
        return stations

    
    radio = local_radio.Radio(
        get_stations_fn=get_stations,
        play_keys=_RADIO_PLAY_KEYS,
        change_station_previous_keys=_RADIO_CHANGE_STATION_PREVIOUS_KEYS,
        change_station_next_keys=_RADIO_CHANGE_STATION_NEXT_KEYS)
    return radio


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
    bridge.run()
    

if __name__ == "__main__":
    while True:
        main()
