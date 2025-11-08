from typing import List

import reflex as rx

from torrent_garden.db.model import Torrent
from torrent_garden.ui.component.button.open_torrent import open_torrent_button
from torrent_garden.ui.helper import pretty_size
from torrent_garden.ui.state.torrent.action import TorrentViewState


def torrent_list_item(t: Torrent) -> rx.Component:
    return rx.card(
        rx.vstack(
            # Title / name
            rx.text(
                t.name,
                weight="bold",
                white_space="normal",
                style={"wordBreak": "break-word"},
            ),
            # Key facts
            rx.hstack(
                rx.badge(f"Size: {pretty_size(t.size)}", color_scheme="gray"),
                rx.badge(f"Files: {t.files.length()}", color_scheme="gray"),
                rx.spacer(),
                justify="between",
                width="100%",
            ),
            # Secondary metrics (compact)
            rx.hstack(
                rx.text(f"Seen: {t.seen_count}", size="1", color_scheme="gray"),
                rx.text(f"Views: {t.views}", size="1", color_scheme="gray"),
                rx.text(f"DL: {t.downloads}", size="1", color_scheme="gray"),
                width="100%",
                justify="start",
                wrap="wrap",
                gap="$2",
            ),
            # Actions
            rx.hstack(
                rx.icon_button(rx.icon("eye"), on_click=lambda: TorrentViewState.view(t.id), color_scheme="blue"),
                open_torrent_button(torrent=t),
                width="100%",
                justify="end",
                gap="$2",
            ),
            width="100%",
            align="start",
            gap="$2",
        ),
        width="100%",
    )


def torrent_list(torrents: List[Torrent]) -> rx.Component:
    return rx.vstack(
        rx.foreach(torrents, torrent_list_item),
        width="100%",
        align="stretch",
        gap="$3",
    )
