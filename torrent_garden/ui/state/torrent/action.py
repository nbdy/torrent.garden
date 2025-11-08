import reflex as rx
from sqlmodel import select

from torrent_garden.db.model import Torrent


class TorrentViewState(rx.State):
    @rx.event
    def open(self, tid: int):
        with rx.session() as session:
            statement = select(Torrent).where(Torrent.id == tid)
            db_torrent = session.exec(statement).one_or_none()
            db_torrent.downloads += 1
            session.commit()


    @rx.event
    def view(self, tid: int):
        with rx.session() as session:
            statement = select(Torrent).where(Torrent.id == tid)
            db_torrent = session.exec(statement).one_or_none()
            db_torrent.views += 1
            session.commit()
        yield rx.redirect(f"/t/{tid}")
