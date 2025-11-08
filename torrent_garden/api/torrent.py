from datetime import datetime
from typing import Optional, List

import reflex as rx
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from torrent_garden import TORRENT_GARDEN_CLIENT_AUTHENTICATION_ENABLE, logger
from torrent_garden.db.count import (
    update_file_counts,
    update_total_files_size,
    COUNT_NAME_TORRENT_FILES_ARCHIVES,
    ARCHIVE_EXTENSIONS,
    COUNT_NAME_TORRENT_FILES_CODE_FILES,
    CODE_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
    COUNT_NAME_TORRENT_FILES_DOCUMENTS,
    EXECUTABLE_EXTENSIONS,
    COUNT_NAME_TORRENT_FILES_EXECUTABLES,
    COUNT_NAME_TORRENT_FILES_IMAGES,
    IMAGE_EXTENSIONS,
    AUDIO_EXTENSIONS,
    COUNT_NAME_TORRENT_FILES_AUDIO_FILES,
    COUNT_NAME_TORRENT_FILES_VIDEOS,
    VIDEO_EXTENSIONS,
    update_files_size,
    COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE,
    COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE,
    COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE,
    COUNT_NAME_TORRENT_FILES_IMAGES_SIZE,
    COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE,
    COUNT_NAME_TORRENT_FILES,
    COUNT_NAME_TORRENT_FILES_UNKNOWN,
    COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE,
    ALL_KNOWN_EXTENSIONS,
    update_total_torrent_count,
)
from torrent_garden.db.model import Crawler, Torrent, TorrentFile

api = FastAPI()


class AddTorrentFile(BaseModel):
    path: str = Field()
    size: int = Field()


class AddTorrent(BaseModel):
    info_hash: str = Field()
    name: str = Field()
    size: int = Field()
    files: List[AddTorrentFile] = Field()


class AddTorrentResponse(BaseModel):
    error: bool = Field()
    message: str = Field()


class AddTorrentRequest(BaseModel):
    torrent: AddTorrent = Field()
    name: Optional[str] = Field(default=None)
    token: Optional[str] = Field(default=None)


def get_torrent_file_type_count(files: List[AddTorrentFile], endings: List[str]) -> int:
    ret = 0
    for file in files:
        for ending in endings:
            if file.path.lower().endswith(ending):
                ret += 1
                break
    return ret


def get_torrent_file_type_size(files: List[AddTorrentFile], endings: List[str]) -> int:
    ret = 0
    for file in files:
        for ending in endings:
            if file.path.lower().endswith(ending):
                ret += file.size
                break
    return ret


def update_counts(session: Session, torrent: AddTorrent, new_files: List[TorrentFile]):
    """Update aggregate counters for newly added torrent and its new files.

    Notes:
    - We only count category additions for files that are truly new in the DB (new_files),
      to avoid double-counting when the same file appears in multiple torrents.
    - Unknown/Other file types (not matching any known extension) are tracked as well.
    """
    update_total_torrent_count(session, 1)

    # Total file count/size increments are based on new files only
    update_file_counts(session, COUNT_NAME_TORRENT_FILES, len(new_files))
    new_files_total_size = sum(f.size for f in new_files)
    update_total_files_size(session, new_files_total_size)

    # Define categories for compact iteration
    categories = [
        (COUNT_NAME_TORRENT_FILES_ARCHIVES, COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE, ARCHIVE_EXTENSIONS),
        (COUNT_NAME_TORRENT_FILES_CODE_FILES, COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE, CODE_EXTENSIONS),
        (COUNT_NAME_TORRENT_FILES_DOCUMENTS, COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE, DOCUMENT_EXTENSIONS),
        (COUNT_NAME_TORRENT_FILES_EXECUTABLES, COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE, EXECUTABLE_EXTENSIONS),
        (COUNT_NAME_TORRENT_FILES_IMAGES, COUNT_NAME_TORRENT_FILES_IMAGES_SIZE, IMAGE_EXTENSIONS),
        (COUNT_NAME_TORRENT_FILES_AUDIO_FILES, COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE, AUDIO_EXTENSIONS),
        (COUNT_NAME_TORRENT_FILES_VIDEOS, COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE, VIDEO_EXTENSIONS),
    ]

    for count_name, size_name, endings in categories:
        count_add = get_torrent_file_type_count(new_files, endings)  # type: ignore[arg-type]
        size_add = get_torrent_file_type_size(new_files, endings)    # type: ignore[arg-type]
        update_file_counts(session, count_name, count_add)
        update_files_size(session, size_name, size_add)

    # Unknown/Other files: those that do not match any known extension set
    def is_known(path: str) -> bool:
        p = path.lower()
        return any(p.endswith(ext) for ext in ALL_KNOWN_EXTENSIONS)

    unknown_count = sum(1 for f in new_files if not is_known(f.path))
    unknown_size = sum(f.size for f in new_files if not is_known(f.path))
    update_file_counts(session, COUNT_NAME_TORRENT_FILES_UNKNOWN, unknown_count)
    update_files_size(session, COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE, unknown_size)


def create_torrent_files(session: Session, db_torrent: Torrent, torrent: AddTorrent) -> List[TorrentFile]:
    logger.info(f"Adding {len(torrent.files)} files to torrent: {torrent.name}")
    file_paths = [file.path for file in torrent.files]
    existing_files = session.exec(select(TorrentFile).where(TorrentFile.path.in_(file_paths))).all()
    existing_files_map = {file.path: file for file in existing_files}
    new_files = []
    for file in torrent.files:
        if file.path not in existing_files_map.keys():
            db_torrent_file = TorrentFile(
                path=file.path,
                size=file.size,
                torrent=[db_torrent]
            )
            session.add(db_torrent_file)
            new_files.append(db_torrent_file)
            existing_files_map[file.path] = db_torrent_file
        else:
            existing_file = existing_files_map[file.path]
            if db_torrent not in existing_file.torrent:
                existing_file.torrent.append(db_torrent)
                session.add(existing_file)
    session.commit()
    return new_files


def add_torrent(torrent: AddTorrent, crawler: Optional[Crawler] = None):
    # logger.info(torrent)
    with rx.session() as session:
        if crawler is not None:
            session.refresh(crawler)
        statement = select(Torrent).where(Torrent.info_hash == torrent.info_hash)
        db_torrent = session.exec(statement).one_or_none()
        if db_torrent is None:
            logger.info(f"Creating torrent: {torrent.name}")
            db_torrent = Torrent(
                name=torrent.name,
                info_hash=torrent.info_hash,
                size=torrent.size,
                crawlers=[],
                files=[],
            )
            session.add(db_torrent)
            session.commit()
            new_files = create_torrent_files(session, db_torrent, torrent)
            update_counts(session, torrent, new_files)
        else:
            logger.info(f"Updating torrent: {torrent.name}")
            db_torrent.seen_count += 1
            db_torrent.updated_at = datetime.now()
            session.add(db_torrent)

        if crawler is not None:
            if crawler not in db_torrent.crawlers:
                logger.info(f"Adding crawler: {crawler.name} to torrent: {torrent.name}")
                db_torrent.crawlers.append(crawler)

        session.commit()


@api.post("/api/torrent/add")
async def api_add_torrent(request: AddTorrentRequest) -> AddTorrentResponse:
    rsp = AddTorrentResponse(error=False, message="")

    if TORRENT_GARDEN_CLIENT_AUTHENTICATION_ENABLE:
        with rx.session() as session:
            crawler = session.exec(select(Crawler).where(Crawler.name == request.name)).one_or_none()
            if crawler is not None:
                if crawler.token == request.token:
                    add_torrent(request.torrent, crawler)
                else:
                    crawler.failed_authentication_count += 1
                    rsp.error = True
                    rsp.message = "Invalid credentials"
            else:
                rsp.error = True
                rsp.message = "Invalid credentials"
            session.commit()
    else:
        add_torrent(request.torrent)

    return rsp
