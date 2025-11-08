from typing import List

import reflex as rx

from torrent_garden.db.model import TorrentFile
from torrent_garden.ui.helper import pretty_size
from torrent_garden.ui.state.search_files import FileSearchState


def file_search_table_header(sort_by=None, sort_desc=True, on_sort=None) -> rx.Component:
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
        header_cell("Path", "path"),
        header_cell("Size", "size"),
        header_cell("Actions", None),
    )


def file_search_action_cell(f: TorrentFile) -> rx.Component:
    return rx.hstack(
        rx.icon_button(
            rx.icon("chevrons-right"),
            on_click=lambda: FileSearchState.open_related(f.id),
            color_scheme="indigo",
            disabled=rx.cond(f.torrent.length() == 0, True, False),
        ),
        justify="end",
        width="100%",
    )


def file_search_table_body_row(f: TorrentFile) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.text(
                f.path,
                white_space="normal",
                style={"wordBreak": "break-word"},
            ),
            width="50%",
            overflow="hidden",
        ),
        rx.table.cell(rx.text(pretty_size(f.size))),
        rx.table.cell(file_search_action_cell(f)),
    )


def file_search_table_body(files: List[TorrentFile]) -> rx.Component:
    return rx.table.body(rx.foreach(files, file_search_table_body_row))


def file_search_table(files: List[TorrentFile], sort_by=None, sort_desc=True, on_sort=None) -> rx.Component:
    return rx.table.root(
        file_search_table_header(sort_by=sort_by, sort_desc=sort_desc, on_sort=on_sort),
        file_search_table_body(files),
        width="100%",
        table_layout="fixed",
    )
