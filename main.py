import sys
from typing import Sequence, Union

from music_library import Library, Track, Album, Artist
from console_ui import SelectorApp, PlayerMonitor
from player import Player
from wrappers import LibraryWrapper

if __name__ == "__main__":
    monitor = PlayerMonitor()
    library = Library.from_dir(sys.argv[1])
    library_wrapper = LibraryWrapper(library)

    player = Player(monitor.update_status)
    player.start()

    def play(item: Union[Artist, Album, Track]) -> None:
        if isinstance(item, Track):
            player.playlist(item)
        elif isinstance(item, Album):
            for track in item.ordered_tracks():
                player.playlist(track)
        elif isinstance(item, Artist):
            for track in item.tracks.values():
                player.playlist(track)


    selector = SelectorApp(library_wrapper, play, monitor)
    selector.run()
