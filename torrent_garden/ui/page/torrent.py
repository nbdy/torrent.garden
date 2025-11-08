import reflex as rx

from torrent_garden.ui.component.button.open_torrent import open_torrent_button
from torrent_garden.ui.component.table.file import file_table
from torrent_garden.ui.component.list.file import file_list
from torrent_garden.ui.helper import pretty_size, array_count
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.state.torrent.view import PageTorrentState


def torrent_page_found() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading(PageTorrentState.torrent.name),
            width="100%",
            justify="center"
        ),
        rx.hstack(
            rx.heading(f"Size: {pretty_size(PageTorrentState.torrent.size)}", size="4"),
            rx.divider(orientation="vertical"),
            rx.heading(f"Files: {array_count(PageTorrentState.torrent.files)}", size="4"),
            width="100%",
            justify="center"
        ),
        rx.hstack(
            open_torrent_button(torrent=PageTorrentState.torrent, text="Download"),
            width="100%",
            justify="center"
        ),

        rx.hstack(
            rx.mobile_only(file_list(PageTorrentState.torrent.files), width="100%"),
            rx.tablet_and_desktop(file_table(PageTorrentState.torrent.files), width="100%"),
            width="100%",
        ),

        width="100%"
    )


def torrent_page_not_found() -> rx.Component:
    return rx.hstack(
        rx.heading("Not Found"),
        width="100%"
    )


def torrent_page_loading() -> rx.Component:
    return rx.hstack(
        rx.spinner(),
        width="100%",
        align="center"
    )


def torrent_page_loaded() -> rx.Component:
    return rx.cond(
        PageTorrentState.is_found,
        torrent_page_found(),
        torrent_page_not_found(),
    )


def torrent_page_content() -> rx.Component:
    return rx.cond(
        PageTorrentState.is_loading,
        torrent_page_loading(),
        torrent_page_loaded(),
    )


def torrent_page() -> rx.Component:
    return page_base(
        rx.vstack(
            rx.cond(
                PageTorrentState.is_found,
                torrent_page_found(),
                torrent_page_not_found(),
            ),

            width="100%"
        )
    )


@rx.page("/t/[tid]", on_load=PageTorrentState.on_load)
def torrent() -> rx.Component:
    return torrent_page()
