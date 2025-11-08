from typing import List, Optional

import reflex as rx
from sqlalchemy.orm import selectinload
from sqlmodel import select

from torrent_garden.db.model import TorrentFile, Torrent
from torrent_garden.ui.component.list.torrent import torrent_list
from torrent_garden.ui.component.table.torrent import torrent_table
from torrent_garden.ui.page.base import page_base
from torrent_garden.ui.helper import array_count


class PageFileTorrentsState(rx.State):
    is_loading: bool = True
    file: Optional[TorrentFile] = None
    torrents: List[Torrent] = []

    @rx.event
    def on_load(self):
        self.is_loading = True
        with rx.session() as session:
            file_stmt = (
                select(TorrentFile)
                .where(TorrentFile.id == self.fid)
                .options(selectinload(TorrentFile.torrent))
            )
            file_obj = session.exec(file_stmt).one_or_none()
            if file_obj:
                # Load torrents with their files for display richness
                torrent_ids = [t.id for t in file_obj.torrent]
                if torrent_ids:
                    torrents_stmt = (
                        select(Torrent)
                        .where(Torrent.id.in_(torrent_ids))
                        .options(selectinload(Torrent.files))
                    )
                    self.torrents = list(session.exec(torrents_stmt).all())
                else:
                    self.torrents = []
                self.file = file_obj
            else:
                self.file = None
                self.torrents = []
        self.is_loading = False

    @rx.var
    def is_found(self) -> bool:
        return self.file is not None


def file_torrents_loading() -> rx.Component:
    return rx.hstack(rx.spinner(), width="100%", align="center", justify="center")


def file_torrents_found() -> rx.Component:
    return rx.vstack(
        rx.heading(f"Torrents containing: {PageFileTorrentsState.file.path}", size="4"),
        rx.text(f"Matches: {array_count(PageFileTorrentsState.torrents)}", size="2", color_scheme="gray"),
        rx.hstack(
            rx.mobile_only(torrent_list(PageFileTorrentsState.torrents), width="100%"),
            rx.tablet_and_desktop(torrent_table(PageFileTorrentsState.torrents), width="100%"),
            width="100%",
        ),
        width="100%",
        spacing="3",
    )


def file_torrents_not_found() -> rx.Component:
    return rx.hstack(rx.heading("File not found"), width="100%", justify="center")


def page_file_torrents() -> rx.Component:
    return page_base(
        rx.vstack(
            rx.cond(
                PageFileTorrentsState.is_loading,
                file_torrents_loading(),
                rx.cond(PageFileTorrentsState.is_found, file_torrents_found(), file_torrents_not_found()),
            ),
            width="100%",
        )
    )


@rx.page("/file/[fid]/torrents", on_load=PageFileTorrentsState.on_load)
def file_torrents() -> rx.Component:
    return page_file_torrents()
