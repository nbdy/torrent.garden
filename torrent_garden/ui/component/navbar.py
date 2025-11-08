import reflex as rx

from torrent_garden.ui.component.button.navbar import navbar_button


# Desktop / tablet navbar (original layout)
def desktop_navbar_start() -> rx.Component:
    return rx.hstack(
        rx.icon("tree-palm"),
        width="100%",
        align="center",
        justify="start",
    )


def desktop_navbar_center() -> rx.Component:
    return rx.hstack(
        navbar_button(icon="chart-area", text="Metrics", width="120px", href="/metrics"),
        navbar_button(icon="layout-dashboard", text="Browse", width="120px", href="/browse"),
        navbar_button(icon="magnet", text="Torrents", width="120px", href="/search/torrents"),
        navbar_button(icon="file-search", text="Files", width="120px", href="/search/files"),
        width="100%",
        align="center",
        justify="center",
    )


def desktop_navbar_end() -> rx.Component:
    return rx.hstack(
        navbar_button(icon="info", text="About", href="/about"),
        width="100%",
        align="center",
        justify="end",
    )


def desktop_navbar() -> rx.Component:
    return rx.card(
        rx.hstack(
            desktop_navbar_start(),
            desktop_navbar_center(),
            desktop_navbar_end(),
            width="100%",
            justify="center",
        ),
        width="100%",
    )


# Mobile navbar with burger menu on the right and icon on the left
def mobile_navbar() -> rx.Component:
    return rx.card(
        rx.hstack(
            # Left-side app icon
            rx.icon("tree-palm"),
            # Right-side burger menu
            rx.menu.root(
                rx.menu.trigger(
                    rx.icon_button(rx.icon("menu"), variant="ghost"),
                ),
                rx.menu.content(
                    rx.menu.item("Metrics", on_click=rx.redirect("/metrics")),
                    rx.menu.item("Browse", on_click=rx.redirect("/browse")),
                    rx.menu.item("Search Torrents", on_click=rx.redirect("/search/torrents")),
                    rx.menu.item("Search Files", on_click=rx.redirect("/search/files")),
                    rx.menu.item("About", on_click=rx.redirect("/about")),
                ),
            ),
            width="100%",
            align="center",
            justify="between",
        ),
        width="100%",
    )


def navbar() -> rx.Component:
    # Use responsive helpers to choose the appropriate navbar
    return rx.hstack(
        rx.mobile_only(mobile_navbar(), width="100%"),
        rx.tablet_and_desktop(desktop_navbar(), width="100%"),
        width="100%",
    )
