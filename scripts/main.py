import sys
from typing import Sequence, Union

from organiser.music_library import Library, Track, Album, Artist
from organiser.console_ui import SelectorApp, PlayerMonitor
from organiser.player import make_player

if __name__ == "__main__":
    monitor = PlayerMonitor()
    library = Library.from_dir(sys.argv[1])
    if len(sys.argv) > 2:
        player_mode = sys.argv[2]
    else:
        player_mode = "mpg321"
    player = make_player(monitor, player_mode)
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


    selector = SelectorApp(library, play, monitor)
    selector.run()
