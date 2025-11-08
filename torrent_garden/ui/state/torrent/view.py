from typing import Optional

import reflex as rx
from sqlalchemy.orm import selectinload
from sqlmodel import select

from torrent_garden.db.model import Torrent


class PageTorrentState(rx.State):
    is_loading: bool = True
    torrent: Optional[Torrent] = None

    @rx.event
    def on_load(self):
        self.is_loading = True
        with rx.session() as session:
            statement = (
                select(Torrent)
                .where(Torrent.id == self.tid)
                .options(selectinload(Torrent.files), selectinload(Torrent.crawlers))
            )
            torrent = session.exec(statement).one_or_none()
            if torrent:
                torrent.views += 1
                session.add(torrent)
                session.commit()
                session.refresh(torrent)
                session.expunge(torrent)
                self.torrent = torrent
            else:
                self.torrent = None
        self.is_loading = False

    @rx.var
    def is_found(self) -> bool:
        return self.torrent is not None
