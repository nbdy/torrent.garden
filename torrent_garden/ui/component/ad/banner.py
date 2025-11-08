import reflex as rx
from reflex import Component

from torrent_garden.db.model import Ad


class BannerAd(rx.ComponentState):
    @classmethod
    def get_component(cls, *children, **props) -> Component:
        ad: Ad = props.pop("ad")
        return rx.hstack(
            rx.html(ad.html),
            width="100%",
            align="center",
            **props
        )


banner_ad = BannerAd.create
