import reflex as rx

from torrent_garden.ui.component.button.debounced import debounced_button
from torrent_garden.ui.component.table.file_search import file_search_table
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.state.browse import COUNT_OPTIONS
from torrent_garden.ui.state.search_files import FileSearchState


def search_files_form() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=FileSearchState.name_query,
            placeholder="File name contains...",
            on_change=FileSearchState.set_name_query,
            width="100%",
        ),
        rx.input(
            value=FileSearchState.ext_query,
            placeholder="Ext (e.g. mp4)",
            on_change=FileSearchState.set_ext_query,
            width="200px",
        ),
        rx.select(
            COUNT_OPTIONS,
            value=FileSearchState.count,
            on_change=FileSearchState.set_count,
        ),
        debounced_button(rx.icon("search"), on_click=FileSearchState.search),
        width="100%",
    )


def search_files_loading() -> rx.Component:
    return rx.hstack(
        rx.spinner(),
        width="100%",
        align="center",
        justify="center",
    )


def search_files_results() -> rx.Component:
    return rx.vstack(
        rx.cond(
            FileSearchState.files.length() > 0,
            rx.vstack(
                pagination_controls(),
                file_search_table(FileSearchState.sorted_files, sort_by=FileSearchState.sort_by, sort_desc=FileSearchState.sort_desc, on_sort=FileSearchState.set_sort),
                pagination_controls(),
                width="100%",
                spacing="3",
            ),
            rx.text("No files found.", color_scheme="gray"),
        ),
        width="100%",
        spacing="2",
    )


def page_search_files() -> rx.Component:
    return page_base(
        rx.vstack(
            search_files_form(),
            rx.cond(FileSearchState.is_loading, search_files_loading(), search_files_results()),
            width="100%",
            align="center",
            spacing="4",
        )
    )


@rx.page("/search/files", title="Search Files")
def search_files() -> rx.Component:
    return page_search_files()



def pagination_number_button(number: int) -> rx.Component:
    return rx.button(
        rx.text(number),
        variant=rx.cond(number == FileSearchState.page, "solid", "soft"),
        on_click=lambda: FileSearchState.set_page(number),
    )


def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button("Prev", on_click=FileSearchState.prev_page, disabled=FileSearchState.page <= 1),
        rx.foreach(FileSearchState.page_numbers, pagination_number_button),
        rx.button("Next", on_click=FileSearchState.next_page, disabled=FileSearchState.page >= FileSearchState.total_pages),
        width="100%",
        justify="center",
        spacing="2",
    )
