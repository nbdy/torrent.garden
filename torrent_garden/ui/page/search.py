import reflex as rx

from torrent_garden.ui.component.button.debounced import debounced_button
from torrent_garden.ui.component.table.torrent import torrent_table
from torrent_garden.ui.component.table.file import file_table
from torrent_garden.ui.component.list.torrent import torrent_list
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.state.browse import COUNT_OPTIONS
from torrent_garden.ui.state.search import SearchState


def search_form() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.input(
                value=SearchState.torrent_query,
                placeholder="Torrent name contains...",
                on_change=SearchState.set_torrent_query,
                width="100%",
            ),
            rx.select(
                COUNT_OPTIONS,
                value=SearchState.count,
                on_change=SearchState.set_count,
            ),
            debounced_button(rx.icon("search"), on_click=SearchState.search),
            width="100%",
        ),
        rx.hstack(
            rx.input(
                value=SearchState.file_name_query,
                placeholder="File name contains...",
                on_change=SearchState.set_file_name_query,
                width="100%",
            ),
            rx.input(
                value=SearchState.file_ext_query,
                placeholder="Ext (e.g. mp4)",
                on_change=SearchState.set_file_ext_query,
                width="200px",
            ),
            width="100%",
        ),
        width="100%",
        spacing="2",
    )


def search_loading() -> rx.Component:
    return rx.hstack(
        rx.spinner(),
        width="100%",
        align="center",
        justify="center",
    )


def search_results() -> rx.Component:
    return rx.vstack(
        # Torrent results
        rx.cond(
            SearchState.torrents.length() > 0,
            rx.vstack(
                rx.heading("Torrent results", size="3"),
                rx.hstack(
                    rx.mobile_only(torrent_list(SearchState.sorted_torrents), width="100%"),
                    rx.tablet_and_desktop(torrent_table(SearchState.sorted_torrents, sort_by=SearchState.torrent_sort_by, sort_desc=SearchState.torrent_sort_desc, on_sort=SearchState.set_torrent_sort), width="100%"),
                    width="100%",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        # File results
        rx.cond(
            SearchState.files.length() > 0,
            rx.vstack(
                rx.heading("File results", size="3"),
                file_table(SearchState.sorted_files, sort_by=SearchState.file_sort_by, sort_desc=SearchState.file_sort_desc, on_sort=SearchState.set_file_sort),
                width="100%",
                spacing="2",
            ),
        ),
        width="100%",
        spacing="4",
    )


def page_search() -> rx.Component:
    return page_base(
        rx.vstack(
            search_form(),
            rx.cond(SearchState.is_loading, search_loading(), search_results()),
            width="100%",
            align="center",
            spacing="4",
        )
    )


@rx.page("/search", title="Search")
def search() -> rx.Component:
    return page_search()
