import reflex as rx

from torrent_garden.ui.helper import pretty_size, pretty_count, pie_tooltip_formatter_count, pie_tooltip_formatter_size
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.state.metrics import MetricsState


def page_metrics_file_type_count_pie_chart_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Count "),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=MetricsState.file_type_count_chart_data,
                    data_key="value",
                    name_key="label",
                    cx="60%",
                    cy="50%",
                    label_line=False,
                    label=False,
                    outer_radius=80,
                    fill="#8884d8",
                ),
                rx.recharts.tooltip(
                    formatter=pie_tooltip_formatter_count()
                ),
                rx.recharts.legend(
                    layout="vertical",
                    align="left",
                    vertical_align="middle",
                ),
                width="100%",
                height=300,
            ),
            width="100%",
        ),
        width="100%",
    )


def page_metrics_file_type_size_pie_chart_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Size"),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=MetricsState.file_type_size_chart_data,
                    data_key="value",
                    name_key="label",
                    cx="60%",
                    cy="50%",
                    label_line=False,
                    label=False,
                    outer_radius=80,
                    fill="#8884d8",
                ),
                rx.recharts.tooltip(
                    formatter=pie_tooltip_formatter_size()
                ),
                rx.recharts.legend(
                    layout="vertical",
                    align="left",
                    vertical_align="middle",
                ),
                width="100%",
                height=300,
            ),
            width="100%",
        ),
        width="100%",
    )


def page_metrics_count_card(title: str, value: str) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.heading(title),
            rx.heading(value),
            width="100%",
            justify="between"
        ),
        width="100%",
    )


def page_metrics_counts() -> rx.Component:
    return rx.hstack(
        page_metrics_count_card("Torrents", f"{pretty_count(MetricsState.total_torrent_count)}"),
        page_metrics_count_card("Files", f"{pretty_count(MetricsState.total_torrent_file_count)}"),
        page_metrics_count_card("Size", f"{pretty_size(MetricsState.total_torrent_size)}"),
        rx.icon_button(rx.icon("refresh_cw"), on_click=MetricsState.on_mount, variant="soft", size="3", loading=MetricsState.is_loading),
        width="100%",
        align="center",
        justify="between",
    )


def page_metrics_torrent_timeline_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Last 30 Days", size="4"),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="count",
                    stroke="#8884d8",
                    stroke_width=2,
                    type_="monotone",
                ),
                rx.recharts.x_axis(data_key="date"),
                rx.recharts.y_axis(),
                rx.recharts.tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=MetricsState.torrent_timeline_data,
                width="100%",
                height=300,
            ),
            spacing="3",
        ),
        width="100%",
    )


def page_metrics_torrent_timeline_hourly_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Last 24 Hours", size="4"),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="count",
                    stroke="#82ca9d",
                    stroke_width=2,
                    type_="monotone",
                ),
                rx.recharts.x_axis(data_key="time"),
                rx.recharts.y_axis(),
                rx.recharts.tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=MetricsState.torrent_timeline_hourly_data,
                width="100%",
                height=300,
            ),
            spacing="3",
        ),
        width="100%",
    )


def page_metrics_torrent_timeline_minutely_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Last 60 Minutes", size="4"),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="count",
                    stroke="#ffc658",
                    stroke_width=2,
                    type_="monotone",
                ),
                rx.recharts.x_axis(data_key="time"),
                rx.recharts.y_axis(),
                rx.recharts.tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=MetricsState.torrent_timeline_minutely_data,
                width="100%",
                height=300,
            ),
            spacing="3",
        ),
        width="100%",
    )


def page_metrics_graphs() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            page_metrics_file_type_count_pie_chart_card(),
            page_metrics_file_type_size_pie_chart_card(),
            spacing="2",
            width="100%",
        ),
        rx.hstack(
            page_metrics_torrent_timeline_minutely_card(),
            page_metrics_torrent_timeline_hourly_card(),
            page_metrics_torrent_timeline_card(),

            spacing="2",
            width="100%",
        ),
        spacing="2",
        width="100%"
    )


def page_metrics() -> rx.Component:
    return page_base(
        rx.vstack(
            page_metrics_counts(),
            page_metrics_graphs(),
            width="100%",
            on_mount=MetricsState.on_mount,
            on_unmount=MetricsState.on_unmount,
        )
    )


@rx.page("/metrics", title="Metrics")
def metrics() -> rx.Component:
    return page_metrics()
