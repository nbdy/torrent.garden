from typing import Optional

import reflex as rx
from sqlmodel import select

from torrent_garden.db.model import Ad


class PageBaseState(rx.State):
    banner_ad: Optional[Ad] = None

    @rx.var
    def is_banner_ad_available(self) -> bool:
        return self.banner_ad is not None

    @rx.event
    def on_mount(self):
        with rx.session() as session:
            statement = select(Ad).where(Ad.type == "banner")
            self.banner_ad = session.exec(statement).one_or_none()

    @rx.event
    def on_unmount(self):
        ...
