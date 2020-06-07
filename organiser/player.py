from threading import Thread
import sys
import subprocess
import time
from typing import List, Callable

from .music_library import Track, Filename

NotifyFunc = Callable[[str, List[Track]], None]

def make_player(monitor, mp3_player):
    if mp3_player == "mpg321":
        player_command = ["mpg321"]
    else:
        player_command = ["omxplayer", "-o", "alsa"]
    return Player(monitor.update_status, player_command)

class Player(Thread):
    def __init__(
            self,
            notify_changes: NotifyFunc,
            player_command: List[str]
    ) -> None:
        super(Player, self).__init__()
        self.queue = [] # type: List[Track]
        self.play_status = "Waiting for something to play."
        self.notify_changes = notify_changes
        self.player_command = player_command

    def command(self, filename: Filename) -> List[str]:
        return self.player_command +  [filename]

    def playlist(self, track: Track) -> None:
        self.queue.append(track)
        self.notify_changes(self.play_status, self.queue)

    def update_status(self, message: str) -> None:
        self.play_status = message
        self.notify_changes(message, self.queue)

    def run(self) -> None:
        print("running")
        while True:
            try:
                next_track = self.queue.pop(0)
                filename = next_track.filename
                self.update_status(f"Now playing: {next_track.artist} - {next_track.title}")
                subprocess.run(self.command(filename), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except IndexError:
                self.update_status("Waiting for something to play.")
                time.sleep(0.1)



