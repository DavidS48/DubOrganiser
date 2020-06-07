
from typing import Dict, Sequence, List, Tuple, Union
import os
import eyed3

class ArtistName(str):
    pass

class TrackName(str):
    pass

class AlbumName(str):
    pass

class Filename(str):
    pass

class Track:
    def __init__(self, filename: Filename, title: TrackName, artist: ArtistName) -> None:
        self.filename = filename
        self.title = title
        self.artist = artist
        
    def __str__(self) -> str:
        return f"{self.artist} - {self.title} (track)"

class Album:
    def __init__(self, title: AlbumName, artist: ArtistName) -> None:
        self.title = title
        self.artist = artist
        self.tracks = {} # type: Dict[int, Track]

    def add_track(self, track: Track, pos: int) -> None:
        self.tracks[pos] = track

    def ordered_tracks(self) -> Sequence[Track]:
        return [self.tracks[i] for i in sorted(self.tracks.keys())]

    def __str__(self) -> str:
        return f"{self.artist} - {self.title} (album)"

class Artist:
    def __init__(self, name: ArtistName) -> None:
        self.name = name
        self.albums = {} # type: Dict[AlbumName, Album]
        self.tracks = {} # type: Dict[Filename, Track]

    def add_album(
            self,
            title: AlbumName,
            album: Album) -> None:
        self.albums[title] = album

    def add_track(self, track: Track, filename: Filename) -> None:
            self.tracks[filename] = track

    def __str__(self) -> str:
        return self.name

class ArtistList:
    def __init__(self, artists: Dict[ArtistName, Artist]) -> None:
        self.artists = artists

    def get_by_prefix(self, prefix: str) -> Sequence[Artist]:
        return [artist for name, artist in self.artists.items() if name.lower().startswith(prefix.lower())]

    def get(self, name: ArtistName) -> Artist:
        try:
            return self.artists[name]
        except KeyError:
            artist = Artist(name)
            self.artists[name] = artist
            return artist

class AlbumList:
    def __init__(self, albums: Dict[Tuple[AlbumName, ArtistName], Album]) -> None:
        self.albums = albums

    def get_by_prefix(self, prefix: str) -> Sequence[Album]:
        return [album for (name, artist), album in self.albums.items() if name.lower().startswith(prefix.lower())]

    def get(self, name: AlbumName, artist: ArtistName) -> Album:
        try:
            return self.albums[(name, artist)]
        except KeyError:
            album = Album(name, artist)
            self.albums[(name, artist)] = album
            return album

class TrackList:
    def __init__(self, tracks: Dict[Filename, Track]) -> None:
        self.tracks = tracks

    def get_by_prefix(self, prefix: str) -> Sequence[Track]:
        return [track for title, track in self.tracks.items() if track.title.lower().startswith(prefix.lower())]

    def add(self, track: Track, filename: Filename) -> None:
        self.tracks[filename] = track

class Library:
    def __init__(self) -> None:
        self.artists = ArtistList({})
        self.albums = AlbumList({})
        self.tracks = TrackList({})

    def get_by_prefix(self, prefix: str) -> Tuple[Sequence[Artist], Sequence[Album], Sequence[Track]]:
        return (
                self.artists.get_by_prefix(prefix),
                self.albums.get_by_prefix(prefix),
                self.tracks.get_by_prefix(prefix)
                )

    def get_all_by_prefix(
            self,
            prefix: str
    ) -> Sequence[Union[Artist, Album, Track]]:
        return (
                self.artists.get_by_prefix(prefix) + 
                self.albums.get_by_prefix(prefix) +
                self.tracks.get_by_prefix(prefix)
        )

    @classmethod
    def from_dir(cls, root_dir: str) -> "Library":
        library = cls()
        for dir_name, sub_dir_list, file_list in os.walk(root_dir):
            for file_name in file_list:
                if os.path.splitext(file_name)[1] == ".mp3":
                    file_path = os.path.join(dir_name, file_name)
                    audio_file = eyed3.load(file_path)
                    tag = audio_file.tag
                    library.add_file(
                            Filename(file_path),
                            TrackName(tag.title),
                            ArtistName(tag.artist),
                            AlbumName(tag.album),
                            ArtistName(tag.album_artist),
                            tag.track_num[0])
        return library


    def add_file(
            self, 
            filename: Filename,
            track_name: TrackName,
            artist_name: ArtistName,
            album_name: AlbumName,
            album_artist_name: ArtistName,
            album_pos: int) -> None:
        print(artist_name, track_name, album_pos)
        track = Track(filename, track_name, artist_name)
        artist = self.artists.get(artist_name)
        album_artist = self.artists.get(album_artist_name)
        album = self.albums.get(album_name, album_artist_name)
        album_artist.add_album(album_name, album)
        album.add_track(track, album_pos)
        artist.add_track(track, filename)
        self.tracks.add(track, filename)

