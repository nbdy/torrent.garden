from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, Relationship, SQLModel


class CrawlerTorrentLinkModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    crawler_id: int = Field(foreign_key="crawler.id")
    torrent_id: int = Field(foreign_key="torrent.id")


class FileTorrentLinkModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    torrent_id: int = Field(foreign_key="torrent.id")
    torrent_file_id: int = Field(foreign_key="torrentfile.id")


class Crawler(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    token: str = Field(max_length=1024)
    created_at: datetime = Field(default_factory=datetime.now)
    torrents: List["Torrent"] = Relationship(back_populates="crawlers", link_model=CrawlerTorrentLinkModel)
    failed_authentication_count: int = Field(default=0)


class TorrentFile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str = Field(unique=True)
    size: int = Field(sa_column=Column(BigInteger(), nullable=False))
    torrent: List["Torrent"] = Relationship(back_populates="files", link_model=FileTorrentLinkModel)


class Torrent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=1024)
    info_hash: str = Field()
    size: int = Field(sa_column=Column(BigInteger(), nullable=False))
    files: List["TorrentFile"] = Relationship(back_populates="torrent", link_model=FileTorrentLinkModel)
    views: int = Field(default=0)
    downloads: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(nullable=True)
    seen_count: int = Field(default=1)
    crawlers: List["Crawler"] = Relationship(back_populates="torrents", link_model=CrawlerTorrentLinkModel)


class Ad(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64)
    type: str = Field(max_length=64)
    html: str = Field()


class Counts(SQLModel, table=True):
    name: str = Field(primary_key=True)
    value: int = Field(sa_column=Column(BigInteger(), nullable=False))
