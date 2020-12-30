import sys
import os

from flask import Flask, render_template, url_for, redirect

from organiser.music_library import Library
from organiser.console_ui import SelectorApp, PlayerMonitor
from organiser.player import make_player


class FlaskMonitor:
    def __init__(self):
        self.current_status = "Not started"
        self.playlist = []
        self.playing = False

    def update_status(self, play_status, queue, playing = False):
        self.current_status = play_status
        self.playlist = queue
        self.playing = playing


app = Flask(__name__)
monitor = FlaskMonitor()
player_mode=os.getenv("MUSIC_PLAYER")
library_dir = os.getenv("MUSIC_DIR")
print("Loading library")
library = Library.from_dir(library_dir)
player = make_player(monitor, player_mode)
player.start()
print("Done")


@app.route("/artists")
def artists(message=None):
    artists = sorted(library.artists.get_by_prefix(""), key = lambda x: x.name)
    return render_template("artists.html", artists=artists, message=message)

@app.route("/artists/<artist_name>/albums")
def albums(artist_name):
    artist = library.artists.get(artist_name)
    print(artist_name)
    print(artist.name)
    print(artist.albums)
    return render_template("albums.html", artist_name = artist_name, albums = artist.albums.values())

@app.route("/artists/<artist_name>/albums/<album_name>/play")
def play_album(artist_name, album_name):
    print(f"Getting album {album_name} {artist_name}")
    album = library.albums.get(album_name, artist_name)
    for track in album.ordered_tracks():
        print("Got track")
        player.playlist(track)
        print(f"Playing {track.title}")
    return redirect(url_for("playlist", message="New tracks added to playlist!"))

@app.route("/skip_track")
def skip_track():
    print("Skipping track.")
    player.skip_track()
    return redirect(url_for("playlist", message="Playlist cleared."))

@app.route("/clear_playlist")
def clear_playlist():
    player.clear_queue()
    return redirect(url_for("playlist", message="Playlist cleared."))

@app.route("/playlist")
def playlist():
    print(monitor.current_status)
    print(monitor.playlist)
    return render_template("playlist.html", status=monitor.current_status, playlist=monitor.playlist, playing = monitor.playing)

