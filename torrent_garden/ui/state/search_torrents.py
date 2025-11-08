from typing import List
from datetime import datetime

import reflex as rx
from sqlalchemy.orm import selectinload
from sqlmodel import select, func

from torrent_garden.db.model import Torrent
from torrent_garden.ui.state.browse import COUNT_OPTIONS


class TorrentSearchState(rx.State):
    is_loading: bool = False

    # Inputs
    query: str = ""

    # Result limit
    count: str = COUNT_OPTIONS[2]  # default "50"
    _count: int = int(COUNT_OPTIONS[2])

    # Pagination
    page: int = 1
    total: int = 0

    # Results
    torrents: List[Torrent] = []

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
    def sorted_torrents(self) -> List[Torrent]:
        col = (self.sort_by or "").strip()
        items = self.torrents
        if not col:
            return items
        def key_func(t: Torrent):
            if col == "name":
                return (t.name or "").lower()
            if col == "size":
                return int(t.size or 0)
            if col == "files":
                return len(list(t.files or []))
            if col == "seen":
                return int(t.seen_count or 0)
            if col == "views":
                return int(t.views or 0)
            if col == "downloads":
                return int(t.downloads or 0)
            if col == "created_at":
                return t.created_at or datetime.min
            if col == "updated_at":
                return t.updated_at or datetime.min
            return 0
        return sorted(items, key=key_func, reverse=self.sort_desc)

    # ----- Events -----
    @rx.event
    def set_query(self, value: str):
        self.query = value
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
        yield TorrentSearchState.search

    @rx.event
    def next_page(self):
        if self.page < self._total_pages():
            self.page += 1
            yield TorrentSearchState.search

    @rx.event
    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            yield TorrentSearchState.search

    # ----- Data access -----
    def _search_torrents(self, session) -> List[Torrent]:
        q = (self.query or "").strip()
        if not q:
            self.total = 0
            return []
        base = (
            select(Torrent)
            .where(Torrent.name.contains(q))
        )
        # total count
        total_stmt = select(func.count(Torrent.id)).select_from(base.subquery())
        self.total = int(session.exec(total_stmt).one())

        # page data
        stmt = (
            select(Torrent)
            .options(selectinload(Torrent.files))
            .where(Torrent.name.contains(q))
            .order_by(Torrent.created_at.desc())
            .limit(self._count)
            .offset((self.page - 1) * self._count)
        )
        return list(session.exec(stmt).all())

    @rx.event
    def set_sort(self, column: str):
        if column == "action":
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
            self.torrents = self._search_torrents(session)
        self.is_loading = False

    @rx.event
    def on_unmount(self):
        self.is_loading = False
        self.query = ""
        self.torrents = []
        self.page = 1
        self.total = 0
