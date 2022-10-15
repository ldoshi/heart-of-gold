"""Run the ship."""

from typing import List

import collections
import getch
import spotipy
import time

#from pa_system.radio import local_radio
import plugin_api

_RESET_CODE = "qwedcxza"

# Spotify access.
_SPOTIPY_CLIENT_ID='ENTER HERE'
_SPOTIPY_CLIENT_SECRET='ENTER HERE'
_SPOTIPY_REDIRECT_URI='http://localhost'
_SPOTIFY_SCOPE = ["user-modify-playback-state", "user-read-playback-state", "user-read-currently-playing", "playlist-read-private", "playlist-read-collaborative", "app-remote-control", "streaming", "user-library-read"]

# Spotify player.
_DEVICE_ID = "ENTER HERE"

def beep() -> None:
    for _ in range(5):
        print('\a')
        time.sleep(.4)

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
                    beep()
                    continue
                
                for plugin in self._plugins:
                    plugin.command(command)
                    
            except Exception as e:
                print(e)

def create_radio_plugin() -> plugin_api.Plugin:
    pass
    
                
def main():
    # Create components.
    # Register with Bridge.

    bridge = Bridge(reset_code=_RESET_CODE)
#    bridge.register(create_radio_plugin())
    bridge.run()
    

if __name__ == "__main__":
    while True:
        main()
