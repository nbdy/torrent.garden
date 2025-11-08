from typing import Callable

import reflex as rx

from sqlmodel import Session, select

from torrent_garden.db.count import (
    get_torrent_count,
    get_torrent_file_count,
    get_total_torrent_size,
    get_archive_file_count,
    get_code_file_count,
    get_document_file_count,
    get_executable_file_count,
    get_image_file_count,
    get_audio_file_count,
    get_video_file_count,
    COUNT_NAME_TORRENTS,
    COUNT_NAME_TORRENT_FILES,
    COUNT_NAME_TORRENT_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_ARCHIVES,
    COUNT_NAME_TORRENT_FILES_CODE_FILES,
    COUNT_NAME_TORRENT_FILES_DOCUMENTS,
    COUNT_NAME_TORRENT_FILES_EXECUTABLES,
    COUNT_NAME_TORRENT_FILES_IMAGES,
    COUNT_NAME_TORRENT_FILES_AUDIO_FILES,
    COUNT_NAME_TORRENT_FILES_VIDEOS,
    get_size,
    COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE,
    COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE,
    COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE,
    COUNT_NAME_TORRENT_FILES_IMAGES_SIZE,
    COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE,
    COUNT_NAME_TORRENT_FILES_UNKNOWN,
    COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE,
)
from torrent_garden.db.model import Counts


def _backfill_counts(session: Session, name: str, fnc: Callable[[Session], int]):
    print(f"Backfilling: {name}")
    statement = select(Counts).where(Counts.name == name)
    count = session.exec(statement).one_or_none()
    if count is None:
        count = Counts(name=name, value=fnc(session))
    else:
        count.value = fnc(session)
    session.add(count)
    session.commit()


def backfill_counts():
    with rx.session() as session:
        _backfill_counts(session, COUNT_NAME_TORRENTS, get_torrent_count)

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES, get_torrent_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_SIZE, get_total_torrent_size)

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_ARCHIVES, get_archive_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE))

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_CODE_FILES, get_code_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE))

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_DOCUMENTS, get_document_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE))

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_EXECUTABLES, get_executable_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE))

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_IMAGES, get_image_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_IMAGES_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_IMAGES_SIZE))

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_AUDIO_FILES, get_audio_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE))

        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_VIDEOS, get_video_file_count)
        _backfill_counts(session, COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE, lambda s: get_size(s, COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE))

        # Unknown/Other: totals minus known categories
        _backfill_counts(
            session,
            COUNT_NAME_TORRENT_FILES_UNKNOWN,
            lambda s: max(
                0,
                get_torrent_file_count(s)
                - (
                    get_archive_file_count(s)
                    + get_code_file_count(s)
                    + get_document_file_count(s)
                    + get_executable_file_count(s)
                    + get_image_file_count(s)
                    + get_audio_file_count(s)
                    + get_video_file_count(s)
                ),
            ),
        )
        _backfill_counts(
            session,
            COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE,
            lambda s: max(
                0,
                get_size(s, COUNT_NAME_TORRENT_FILES_SIZE)
                - (
                    get_size(s, COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE)
                    + get_size(s, COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE)
                    + get_size(s, COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE)
                    + get_size(s, COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE)
                    + get_size(s, COUNT_NAME_TORRENT_FILES_IMAGES_SIZE)
                    + get_size(s, COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE)
                    + get_size(s, COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE)
                ),
            ),
        )
