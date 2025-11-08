import reflex as rx

from torrent_garden.ui.component.button.debounced import debounced_button
from torrent_garden.ui.component.table.torrent import torrent_table
from torrent_garden.ui.component.list.torrent import torrent_list
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.state.browse import BrowseState, MODE_OPTIONS, COUNT_OPTIONS


def page_browse_table_form() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=BrowseState.query,
            placeholder="Search",
            on_change=BrowseState.set_query,
            width="100%"
        ),
        rx.select(
            MODE_OPTIONS,
            value=BrowseState.mode,
            on_change=BrowseState.set_mode
        ),
        rx.select(
            COUNT_OPTIONS,
            value=BrowseState.count,
            on_change=BrowseState.set_count
        ),
        debounced_button(rx.icon("refresh-cw"), on_click=BrowseState.refresh),
        width="100%"
    )


def page_browse_table_loading() -> rx.Component:
    return rx.hstack(
        rx.spinner(),
        width="100%",
        align="center"
    )


def pagination_number_button(number: int) -> rx.Component:
    return rx.button(
        rx.text(number),
        variant=rx.cond(number == BrowseState.page, "solid", "soft"),
        on_click=lambda: BrowseState.set_page(number),
    )


def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button("Prev", on_click=BrowseState.prev_page, disabled=BrowseState.page <= 1),
        rx.foreach(BrowseState.page_numbers, pagination_number_button),
        rx.button("Next", on_click=BrowseState.next_page, disabled=BrowseState.page >= BrowseState.total_pages),
        width="100%",
        justify="center",
        spacing="2",
    )


def page_browse() -> rx.Component:
    return page_base(
        rx.vstack(
            page_browse_table_form(),
            rx.cond(
                BrowseState.is_loading,
                page_browse_table_loading(),
                rx.vstack(
                    pagination_controls(),
                    rx.hstack(
                        rx.mobile_only(torrent_list(BrowseState.filtered_torrents), width="100%"),
                        rx.tablet_and_desktop(torrent_table(BrowseState.filtered_torrents, sort_by=BrowseState.sort_by, sort_desc=BrowseState.sort_desc, on_sort=BrowseState.set_sort), width="100%"),
                        width="100%",
                    ),
                    pagination_controls(),
                    width="100%",
                    spacing="3",
                ),
            ),

            width="100%",
            align="center",

            on_mount=BrowseState.on_mount,
            on_unmount=BrowseState.on_unmount,
        ),
    )


@rx.page("/browse", title="Browse")
def browse() -> rx.Component:
    return page_browse()
