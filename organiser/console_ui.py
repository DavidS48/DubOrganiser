import urwid
import logging
from typing import Any, List, Sequence, Callable, Union

from .music_library import Library, Artist, Album, Track

logging.basicConfig(filename="log.txt", level=logging.DEBUG)

Selectable = Union[Artist, Album, Track]



class PlayerMonitor:
    def __init__(self) -> None:
        self.current_playlist = [] # type: List[Track]

    def update_status(self, message: str, playlist: List[Track]) -> None:
        self.current_playlist = playlist
        urwid.emit_signal(self, "player_status", message)

urwid.register_signal(PlayerMonitor, "player_status")


class Selector:
    def __init__(
            self,
            library: Library,
            select_function: Callable[[Selectable], None]
        ) -> None:
        self.library = library
        self.current_results = [] # type: Sequence[Selectable]
        self.position = 0
        self.select = select_function

    def increment_pos(self) -> None:
        self.position = min(self.position + 1, len(self.current_results) - 1)

    def decrement_pos(self) -> None:
        self.position = max(self.position - 1, 0)

    def update_results(self, search: str) -> None:
        self.position = 0
        self.current_results = self.library.get_all_by_prefix(search)

    def make_selection(self) -> None:
        if self.current_results:
            self.select(self.current_results[self.position])


class SelectorContainer(urwid.Pile):
    def __init__(
            self,
            library: Library,
            select_function: Callable[[Selectable], None]
        ) -> None:
        self.selector = Selector(library, select_function)
        self.search = urwid.Edit(u"Artist, Album or Track Title:\n", "")
        self.results = urwid.Pile([urwid.Text(u"")])
        super(SelectorContainer, self).__init__([self.search, urwid.Divider(), self.results])
        urwid.connect_signal(self.search, "change", self.search_changed)

    def search_changed(self, edit: str, new_text: str) -> None:
        self.selector.update_results(new_text)
        self.redraw()


    def redraw(self) -> None:
        new_contents = []
        for ii, item in enumerate(self.selector.current_results):
            if ii == self.selector.position:
                new_contents.append((urwid.Text(("selected", str(item))), ("weight", 1)))
            else:
                new_contents.append((urwid.Text(str(item)), ("weight", 1)))
        self.results.contents = new_contents


    def keypress(self, size: int, key: str) -> Any:
        logging.info(f"Selector keypress {key}")
        if key == "enter":
            self.selector.make_selection()
        elif key == "down":
            self.selector.increment_pos()
            self.redraw()
        elif key == "up":
            self.selector.decrement_pos()
            self.redraw()
        else:
            return super(SelectorContainer, self).keypress(size, key)

class PlaylistWidget(urwid.Pile):
    def __init__(self, monitor: PlayerMonitor) -> None:
        self.monitor = monitor
        tunes = [urwid.Text(str(item)) for item in self.monitor.current_playlist]
        super(PlaylistWidget, self).__init__([self.coming_up_box()] + tunes)
        urwid.connect_signal(self.monitor, "player_status", self.update_playlist)
        logging.info("Set up playlist widget.")

    def update_playlist(self, message: str) -> None:
        logging.info("updating playlist")
        tunes = [urwid.Text(str(item)) for item in self.monitor.current_playlist]
        items = [(tune, ("weight", 1)) for tune in tunes]
        self.contents = [(self.coming_up_box(), ("weight", 1))] + items

    def coming_up_box(self) -> urwid.Text:
        return urwid.Text("Coming up:")



class SelectorApp:

    palette = [("selected", "black", "light gray")]

    def __init__(
            self,
            library: Library,
            select_function: Callable[[Selectable], None],
            player_monitor: PlayerMonitor) -> None:
        self.player_monitor = player_monitor
        self.player_status = urwid.Text("Waiting for a new selection.")
        self.playlist_widget = PlaylistWidget(player_monitor)

        self.selector_widget = SelectorContainer(library, select_function)
        self.app_area = urwid.Pile([self.player_status, urwid.Divider(), self.selector_widget])
        top = urwid.Filler(self.app_area, valign="top")
        self.current_app = "playlist"

        self.loop = urwid.MainLoop(
                top,
                self.palette,
                unhandled_input = self.unhandled_input
        )
        urwid.connect_signal(self.player_monitor, "player_status", self.player_update)

    def unhandled_input(self, key: str) -> None:
        if key == "tab":
            self.switch_tab()

    def switch_tab(self) -> None:
        logging.info(self.app_area.contents[2][0].focus)
        if self.current_app == "selector":
            logging.info("moving to playlist")
            self.app_area.contents[2] = self.playlist_widget, ("weight", 1)
            self.current_app = "playlist"
        else:
            logging.info("moving to selector")
            self.app_area.contents[2] = self.selector_widget, ("weight", 1)
            self.current_app = "selector"
        logging.info(self.app_area.contents[2][0].focus)
        self.app_area.focus_item = 2
        logging.info(self.app_area.contents[2][0].focus)

    def player_update(self, new_text: str) -> None:
        self.player_status.set_text(new_text)
        self.loop.draw_screen()

    def run(self) -> None:
        self.loop.run()

