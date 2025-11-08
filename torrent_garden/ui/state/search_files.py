from typing import List

import reflex as rx
from sqlalchemy.orm import selectinload
from sqlmodel import select, func

from torrent_garden.db.model import TorrentFile, Torrent
from torrent_garden.ui.state.browse import COUNT_OPTIONS


class FileSearchState(rx.State):
    is_loading: bool = False

    # Inputs
    name_query: str = ""
    ext_query: str = ""

    # Result limit
    count: str = COUNT_OPTIONS[2]  # default "50"
    _count: int = int(COUNT_OPTIONS[2])

    # Pagination
    page: int = 1
    total: int = 0

    # Results
    files: List[TorrentFile] = []

    # Sorting (client-side within current result page)
    sort_by: str = ""
    sort_desc: bool = True

    # ----- Computed -----
    def _total_pages(self) -> int:
        if self._count <= 0:
            return 1
        return max(1, (self.total + self._count - 1) // self._count)

    @rx.var
    def total_pages(self) -> int:
        return self._total_pages()

    @rx.var
    def page_numbers(self) -> list[int]:
        tp = self._total_pages()
        window = 3
        start = max(1, self.page - window)
        end = min(tp, self.page + window)
        return list(range(start, end + 1))

    @rx.var
    def sorted_files(self) -> List[TorrentFile]:
        col = (self.sort_by or "").strip()
        items = self.files
        if not col:
            return items
        def key_func(f: TorrentFile):
            if col == "path":
                return (f.path or "").lower()
            if col == "size":
                return int(f.size or 0)
            return 0
        return sorted(items, key=key_func, reverse=self.sort_desc)

    @rx.event
    def set_name_query(self, value: str):
        self.name_query = value
        self.page = 1

    @rx.event
    def set_ext_query(self, value: str):
        # normalize: strip leading dot
        self.ext_query = (value or "").lstrip(".")
        self.page = 1

    @rx.event
    def set_count(self, value: str):
        self.count = value
        self._count = int(value)
        self.page = 1

    @rx.event
    def set_page(self, page: int):
        if page < 1:
            page = 1
        tp = self._total_pages()
        if page > tp:
            page = tp
        self.page = page
        yield FileSearchState.search

    @rx.event
    def next_page(self):
        if self.page < self._total_pages():
            self.page += 1
            yield FileSearchState.search

    @rx.event
    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            yield FileSearchState.search

    def _search_files(self, session) -> List[TorrentFile]:
        name_q = (self.name_query or "").strip()
        ext_q = (self.ext_query or "").strip()
        if not name_q and not ext_q:
            self.total = 0
            return []
        base = select(TorrentFile)
        if name_q:
            base = base.where(TorrentFile.path.contains(name_q))
        if ext_q:
            base = base.where(TorrentFile.path.like(f"%.{ext_q}"))

        total_stmt = select(func.count(TorrentFile.id)).select_from(base.subquery())
        self.total = int(session.exec(total_stmt).one())

        stmt = (
            select(TorrentFile)
            .options(selectinload(TorrentFile.torrent))
        )
        if name_q:
            stmt = stmt.where(TorrentFile.path.contains(name_q))
        if ext_q:
            stmt = stmt.where(TorrentFile.path.like(f"%.{ext_q}"))
        stmt = (
            stmt.order_by(TorrentFile.path.asc())
            .limit(self._count)
            .offset((self.page - 1) * self._count)
        )
        return list(session.exec(stmt).all())

    @rx.event
    def set_sort(self, column: str):
        if column == "actions":
            return
        if column == self.sort_by:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_by = column
            self.sort_desc = True

    @rx.event
    def search(self):
        self.is_loading = True
        with rx.session() as session:
            self.files = self._search_files(session)
        self.is_loading = False

    @rx.event
    def on_unmount(self):
        self.is_loading = False
        self.name_query = ""
        self.ext_query = ""
        self.files = []
        self.page = 1
        self.total = 0

    @rx.event
    def open_related(self, fid: int):
        with rx.session() as session:
            stmt = (
                select(TorrentFile)
                .where(TorrentFile.id == fid)
                .options(selectinload(TorrentFile.torrent))
            )
            f = session.exec(stmt).one_or_none()
            if not f:
                return
            torrents = list(f.torrent or [])
            if len(torrents) == 1:
                tid = torrents[0].id
                # increment views similar to TorrentViewState.view
                t_stmt = select(Torrent).where(Torrent.id == tid)
                t = session.exec(t_stmt).one_or_none()
                if t:
                    t.views += 1
                    session.commit()
                yield rx.redirect(f"/t/{tid}")
            elif len(torrents) > 1:
                yield rx.redirect(f"/file/{fid}/torrents")
