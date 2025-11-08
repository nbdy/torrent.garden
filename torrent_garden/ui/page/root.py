import reflex as rx

from torrent_garden.ui.state.root import PageRootState


@rx.page("/", on_load=PageRootState.on_load)
def root() -> rx.Component:
    return rx.fragment()
