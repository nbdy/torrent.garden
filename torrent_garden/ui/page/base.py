import reflex as rx

from torrent_garden.ui.component.ad.banner import banner_ad
from torrent_garden.ui.component.navbar import navbar
from torrent_garden.ui.state.base import PageBaseState


def page_base(content: rx.Component) -> rx.Component:
    return rx.fragment(
        rx.vstack(
            navbar(),
            rx.vstack(
                rx.cond(PageBaseState.is_banner_ad_available, banner_ad(ad=PageBaseState.banner_ad)),
                content,
                width="100%",
                padding="2px"
            ),
            width="100%",
            padding="2px"
        ),
        on_mount=PageBaseState.on_mount,
        on_unmount=PageBaseState.on_unmount,
    )
