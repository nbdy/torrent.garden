from typing import List

import reflex as rx

from torrent_garden.db.model import Torrent
from torrent_garden.ui.component.button.open_torrent import open_torrent_button
from torrent_garden.ui.helper import pretty_size
from torrent_garden.ui.state.torrent.action import TorrentViewState


def torrent_table_header(sort_by=None, sort_desc=True, on_sort=None) -> rx.Component:
    def header_cell(label: str, col_id: str | None) -> rx.Component:
        if not col_id or on_sort is None:
            return rx.table.row_header_cell(label)
        return rx.table.row_header_cell(
            rx.hstack(
                rx.text(label),
                rx.cond(
                    sort_by == col_id,
                    rx.cond(
                        sort_desc,
                        rx.icon("arrow-down"),
                        rx.icon("arrow-up"),
                    ),
                    rx.icon("arrow-up-down", color_scheme="gray"),
                ),
                spacing="1",
                align="center",
            ),
            on_click=lambda: on_sort(col_id),
            cursor="pointer",
            user_select="none",
        )
    return rx.table.header(
        header_cell("Name", "name"),
        header_cell("Size", "size"),
        header_cell("Files", "files"),
        header_cell("Seen", "seen"),
        header_cell("Views", "views"),
        header_cell("Downloads", "downloads"),
        header_cell("First seen", "created_at"),
        header_cell("Last seen", "updated_at"),
        header_cell("Action", None),
    )


def torrent_table_body_row(torrent: Torrent) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.text(
                torrent.name,
                white_space="normal",  # allow wrapping to multiple lines
                # style can be used for additional CSS not directly exposed as props:
                style={"wordBreak": "break-word"},
            ),
            width="40%",
            overflow="hidden",
        ),
        rx.table.cell(rx.text(pretty_size(torrent.size))),
        rx.table.cell(rx.text(torrent.files.length())),
        rx.table.cell(rx.text(torrent.seen_count)),
        rx.table.cell(rx.text(torrent.views)),
        rx.table.cell(rx.text(torrent.downloads)),
        rx.table.cell(rx.moment(torrent.created_at, format="YYYY-MM-DD HH:mm:ss")),
        rx.table.cell(rx.cond(
            ~torrent.updated_at,
            rx.text("N/A"),
            rx.moment(torrent.updated_at, format="YYYY-MM-DD HH:mm:ss")
        )),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(rx.icon("eye"), on_click=lambda: TorrentViewState.view(torrent.id), color_scheme="blue"),
                open_torrent_button(torrent=torrent),
                width="100%",
                justify="end"
            )
        )
    )


def torrent_table_body(torrents: List[Torrent]) -> rx.Component:
    return rx.table.body(rx.foreach(torrents, torrent_table_body_row))


def torrent_table(torrents: List[Torrent], sort_by=None, sort_desc=True, on_sort=None) -> rx.Component:
    return rx.table.root(
        torrent_table_header(sort_by=sort_by, sort_desc=sort_desc, on_sort=on_sort),
        torrent_table_body(torrents),
        width="100%",
        table_layout="fixed",
    )
