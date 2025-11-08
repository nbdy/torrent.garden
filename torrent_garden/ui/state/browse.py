from enum import StrEnum
from typing import List
from datetime import datetime

import reflex as rx
from sqlmodel import func, select
from sqlalchemy.orm import selectinload

from torrent_garden.db.model import Torrent

MODE_OPTIONS = ["Newest", "Most Downloaded", "Most Viewed", "Random"]
ORDER_OPTIONS = ["Descending", "Ascending"]
COUNT_OPTIONS = ["10", "20", "50", "100", "200", "500"]


class Mode(StrEnum):
    NEWEST = "Newest"
    MOST_DOWNLOADED = "Most Downloaded"
    MOST_VIEWED = "Most Viewed"
    RANDOM = "Random"


class Order(StrEnum):
    DESCENDING = "Descending"
    ASCENDING = "Ascending"


class BrowseState(rx.State):
    is_loading: bool = True

    mode: str = MODE_OPTIONS[0]
    _mode: Mode = Mode(MODE_OPTIONS[0])

    order: str = ORDER_OPTIONS[0]
    _order: str = Order(ORDER_OPTIONS[0])

    count: str = COUNT_OPTIONS[0]
    _count: int = int(COUNT_OPTIONS[0])

    query: str = ""

    page: int = 1
    total: int = 0

    torrents: List[Torrent] = []
    _torrents: List[Torrent] = []

    # Sorting (client-side within the current page)
    sort_by: str = ""  # one of: name, size, files, seen, views, downloads, created_at, updated_at; empty means no override
    sort_desc: bool = True

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
        pages = list(range(start, end + 1))
        return sorted(pages)

    def _load_torrents(self):
        self.is_loading = True
        with rx.session() as session:
            data_stmt = select(Torrent).options(selectinload(Torrent.files))
            total_stmt = select(func.count(Torrent.id)).select_from(Torrent)
            # Note: Browse page should not search the database by name; it only filters displayed items locally.
            match self._mode:
                case Mode.NEWEST:
                    data_stmt = data_stmt.order_by(Torrent.created_at.desc())
                case Mode.MOST_DOWNLOADED:
                    data_stmt = data_stmt.order_by(Torrent.downloads.desc())
                case Mode.MOST_VIEWED:
                    data_stmt = data_stmt.order_by(Torrent.views.desc())
                case Mode.RANDOM:
                    data_stmt = data_stmt.order_by(func.random())
            offset = (self.page - 1) * self._count
            data_stmt = data_stmt.limit(self._count).offset(offset)
            self.torrents = list(session.exec(data_stmt).all())
            self.total = int(session.exec(total_stmt).one())
        self.is_loading = False

    @rx.event
    def refresh(self):
        self._load_torrents()

    @rx.event
    def set_mode(self, mode: str):
        self.mode = mode
        self._mode = Mode(mode)
        self.page = 1
        yield BrowseState.refresh

    @rx.event
    def set_count(self, count: str):
        self.count = count
        self._count = int(count)
        self.page = 1
        yield BrowseState.refresh

    @rx.event
    def set_query(self, query: str):
        # Update the local filter query without triggering a database refresh.
        self.query = query

    @rx.event
    def set_page(self, page: int):
        if page < 1:
            page = 1
        tp = self._total_pages()
        if page > tp:
            page = tp
        self.page = page
        yield BrowseState.refresh

    @rx.event
    def next_page(self):
        if self.page < self._total_pages():
            self.page += 1
            yield BrowseState.refresh

    @rx.event
    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            yield BrowseState.refresh

    @rx.event
    def set_sort(self, column: str):
        # Toggle sort on same column; default to descending on new column. Ignore forbidden column identifiers.
        if column == "action":
            return
        if column == self.sort_by:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_by = column
            self.sort_desc = True

    @rx.event
    def on_mount(self):
        yield BrowseState.refresh

    @rx.event
    def on_unmount(self):
        self.is_loading = True
        self.query = ""
        self.torrents = []
        self.page = 1
        self.total = 0

    @rx.var
    def filtered_torrents(self) -> List[Torrent]:
        """Filter only the currently loaded page of torrents by the local query, then apply client-side sorting if set."""
        items = self.torrents
        if self.query:
            q = self.query.lower()
            items = [t for t in items if q in (t.name or "").lower()]

        # Apply sorting
        col = (self.sort_by or "").strip()
        if col:
            def key_func(t: Torrent):
                if col == "name":
                    return (t.name or "").lower()
                if col == "size":
                    return int(t.size or 0)
                if col == "files":
                    # t.files is eager-loaded list
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
                    # None should be treated as the oldest for ascending and newest for descending; using datetime.min handles that for ascending; reverse flag covers desc.
                    return t.updated_at or datetime.min
                return 0
            items = sorted(items, key=key_func, reverse=self.sort_desc)

        return items
