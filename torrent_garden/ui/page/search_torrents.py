import reflex as rx

from torrent_garden.ui.component.button.debounced import debounced_button
from torrent_garden.ui.component.table.torrent import torrent_table
from torrent_garden.ui.component.list.torrent import torrent_list
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.state.browse import COUNT_OPTIONS
from torrent_garden.ui.state.search_torrents import TorrentSearchState


def pagination_number_button(number: int) -> rx.Component:
    return rx.button(
        rx.text(number),
        variant=rx.cond(number == TorrentSearchState.page, "solid", "soft"),
        on_click=lambda: TorrentSearchState.set_page(number),
    )


def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button("Prev", on_click=TorrentSearchState.prev_page, disabled=TorrentSearchState.page <= 1),
        rx.foreach(TorrentSearchState.page_numbers, pagination_number_button),
        rx.button("Next", on_click=TorrentSearchState.next_page, disabled=TorrentSearchState.page >= TorrentSearchState.total_pages),
        width="100%",
        justify="center",
        spacing="2",
    )


def search_torrents_form() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=TorrentSearchState.query,
            placeholder="Torrent name contains...",
            on_change=TorrentSearchState.set_query,
            width="100%",
        ),
        rx.select(
            COUNT_OPTIONS,
            value=TorrentSearchState.count,
            on_change=TorrentSearchState.set_count,
        ),
        debounced_button(rx.icon("search"), on_click=TorrentSearchState.search),
        width="100%",
    )


def search_torrents_loading() -> rx.Component:
    return rx.hstack(
        rx.spinner(),
        width="100%",
        align="center",
        justify="center",
    )


def search_torrents_results() -> rx.Component:
    return rx.vstack(
        rx.cond(
            TorrentSearchState.torrents.length() > 0,
            rx.vstack(
                pagination_controls(),
                rx.hstack(
                    rx.mobile_only(torrent_list(TorrentSearchState.sorted_torrents), width="100%"),
                    rx.tablet_and_desktop(torrent_table(TorrentSearchState.sorted_torrents, sort_by=TorrentSearchState.sort_by, sort_desc=TorrentSearchState.sort_desc, on_sort=TorrentSearchState.set_sort), width="100%"),
                    width="100%",
                ),
                pagination_controls(),
                width="100%",
                spacing="3",
            ),
            rx.text("No torrents found.", color_scheme="gray"),
        ),
        width="100%",
        spacing="2",
    )


def page_search_torrents() -> rx.Component:
    return page_base(
        rx.vstack(
            search_torrents_form(),
            rx.cond(TorrentSearchState.is_loading, search_torrents_loading(), search_torrents_results()),
            width="100%",
            align="center",
            spacing="4",
        )
    )


@rx.page("/search/torrents", title="Search Torrents")
def search_torrents() -> rx.Component:
    return page_search_torrents()
