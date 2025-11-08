from typing import List
from datetime import datetime

import reflex as rx
from sqlalchemy.orm import selectinload
from sqlmodel import select

from torrent_garden.db.model import Torrent, TorrentFile
from torrent_garden.ui.state.browse import COUNT_OPTIONS


class SearchState(rx.State):
    is_loading: bool = False

    # Queries
    torrent_query: str = ""
    file_name_query: str = ""
    file_ext_query: str = ""

    # Result limit
    count: str = COUNT_OPTIONS[2]  # default "50"
    _count: int = int(COUNT_OPTIONS[2])

    # Results
    torrents: List[Torrent] = []
    files: List[TorrentFile] = []

    # Sorting (client-side)
    torrent_sort_by: str = ""
    torrent_sort_desc: bool = True
    file_sort_by: str = ""
    file_sort_desc: bool = True

    # ----- Computed -----
    @rx.var
    def sorted_torrents(self) -> List[Torrent]:
        col = (self.torrent_sort_by or "").strip()
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
        return sorted(items, key=key_func, reverse=self.torrent_sort_desc)

    @rx.var
    def sorted_files(self) -> List[TorrentFile]:
        col = (self.file_sort_by or "").strip()
        items = self.files
        if not col:
            return items
        def key_func(f: TorrentFile):
            if col == "path":
                return (f.path or "").lower()
            if col == "size":
                return int(f.size or 0)
            return 0
        return sorted(items, key=key_func, reverse=self.file_sort_desc)

    @rx.event
    def set_torrent_query(self, value: str):
        self.torrent_query = value

    @rx.event
    def set_file_name_query(self, value: str):
        self.file_name_query = value

    @rx.event
    def set_file_ext_query(self, value: str):
        self.file_ext_query = value

    @rx.event
    def set_count(self, value: str):
        self.count = value
        self._count = int(value)

    def _search_torrents(self, session) -> List[Torrent]:
        q = (self.torrent_query or "").strip()
        if not q:
            return []
        stmt = (
            select(Torrent)
            .options(selectinload(Torrent.files))
            .where(Torrent.name.contains(q))
            .order_by(Torrent.created_at.desc())
            .limit(self._count)
        )
        return list(session.exec(stmt).all())

    def _search_files(self, session) -> List[TorrentFile]:
        name_q = (self.file_name_query or "").strip()
        ext_q = (self.file_ext_query or "").strip().lstrip(".")
        if not name_q and not ext_q:
            return []
        stmt = select(TorrentFile)
        if name_q:
            stmt = stmt.where(TorrentFile.path.contains(name_q))
        if ext_q:
            # Match file extension at the end of the path
            stmt = stmt.where(TorrentFile.path.like(f"%.{ext_q}"))
        stmt = stmt.limit(self._count)
        return list(session.exec(stmt).all())

    # Sorting events
    @rx.event
    def set_torrent_sort(self, column: str):
        if column == "action":
            return
        if column == self.torrent_sort_by:
            self.torrent_sort_desc = not self.torrent_sort_desc
        else:
            self.torrent_sort_by = column
            self.torrent_sort_desc = True

    @rx.event
    def set_file_sort(self, column: str):
        if column == "actions":
            return
        if column == self.file_sort_by:
            self.file_sort_desc = not self.file_sort_desc
        else:
            self.file_sort_by = column
            self.file_sort_desc = True

    @rx.event
    def search(self):
        self.is_loading = True
        with rx.session() as session:
            self.torrents = self._search_torrents(session)
            self.files = self._search_files(session)
        self.is_loading = False

    @rx.event
    def on_unmount(self):
        # Reset state when leaving the page
        self.is_loading = False
        self.torrent_query = ""
        self.file_name_query = ""
        self.file_ext_query = ""
        self.torrents = []
        self.files = []
