from typing import Optional

import reflex as rx
from reflex import Component

from torrent_garden.db.model import Torrent
from torrent_garden.ui.state.torrent.action import TorrentViewState


class OpenTorrentButton(rx.ComponentState):
    @classmethod
    def get_component(cls, *children, **props) -> Component:
        torrent: Torrent = props.pop("torrent")
        icon: str = props.pop("icon", "external-link")
        text: Optional[str] = props.pop("text", None)

        return rx.link(
            rx.cond(
                text,
                rx.button(rx.icon("external-link"), rx.text(text)),
                rx.icon_button(icon),
            ),
            on_click=[
                lambda: TorrentViewState.open(torrent.id),
                rx.redirect(f"magnet:?xt=urn:btih:{torrent.info_hash}&amp;dn={torrent.name}")
            ],
            color_scheme="blue",
            **props
        )


open_torrent_button = OpenTorrentButton.create
