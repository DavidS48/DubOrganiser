import sys

from flask import Flask, render_template, url_for, redirect

from organiser.music_library import Library
from organiser.console_ui import SelectorApp, PlayerMonitor
from organiser.player import make_player


class FlaskMonitor:
    def update_status(self, play_status, queue):
        pass


app = Flask(__name__)
print("Loading library")
monitor = FlaskMonitor()
library = Library.from_dir("/home/david/Music/")
player_mode="mpg321"
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
    return render_template("albums.html", albums = artist.albums.values())

@app.route("/artists/<artist_name>/albums/<album_name>/play")
def play_album(artist_name, album_name):
    print(f"Getting album {album_name} {artist_name}")
    album = library.albums.get(album_name, artist_name)
    for track in album.ordered_tracks():
        print("Got track")
        player.playlist(track)
        print(f"Playing {track.title}")
    return redirect(url_for("artists", message="New tracks added to playlist!"))


