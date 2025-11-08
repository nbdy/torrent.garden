from typing import List

import reflex as rx

from torrent_garden.db.model import TorrentFile
from torrent_garden.ui.helper import pretty_size


def file_list_item(f: TorrentFile) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(
                f.path,
                weight="bold",
                white_space="normal",
                style={"wordBreak": "break-word"},
            ),
            rx.hstack(
                rx.badge(f"Size: {pretty_size(f.size)}", color_scheme="gray"),
                width="100%",
                justify="start",
            ),
            width="100%",
            align="start",
            gap="$2",
        ),
        width="100%",
    )


def file_list(files: List[TorrentFile]) -> rx.Component:
    return rx.vstack(
        rx.foreach(files, file_list_item),
        width="100%",
        align="stretch",
        gap="$3",
    )
