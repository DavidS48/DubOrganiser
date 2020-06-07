from music_library import Library, Artist, Album, Track

from typing import Sequence, Union

class LibraryWrapper:
    def __init__(self, library: Library):
        self.library = library

    def search(self, prefix: str) -> Sequence[Union[Artist, Album, Track]]:
        artists, albums, tracks = self.library.get_by_prefix(prefix)
        return artists + albums + tracks


