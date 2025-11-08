from typing import Optional

from sqlmodel import Session, select, func, or_

from torrent_garden.db.model import Torrent, TorrentFile, Counts


def get_torrent_count(session: Session) -> int:
    return int(session.exec(select(func.count(Torrent.id)).select_from(Torrent)).one())


def get_torrent_file_count(session: Session) -> int:
    return int(session.exec(select(func.count(TorrentFile.id)).select_from(TorrentFile)).one())


def get_total_torrent_size(session: Session) -> int:
    count: Optional[int] = session.exec(select(func.sum(Torrent.size)).select_from(Torrent)).one()
    if count is not None:
        return int(count)
    return 0


def get_file_count_by_extensions(session: Session, extensions: tuple[str, ...]) -> int:
    """Generic function to count files by their extensions."""
    if not extensions:
        return 0

    conditions = [TorrentFile.path.ilike(f'%{ext}') for ext in extensions]
    return int(session.exec(
        select(func.count(TorrentFile.id))
        .where(or_(*conditions))
        .select_from(TorrentFile)
    ).one())


VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg', '.ts',
                    '.vob', '.ogv', '.hevc', '.h264', '.divx', '.xvid', '.m2ts', '.mts', '.mxf', '.ogm', '.rm',
                    '.rmvb', '.asf')
AUDIO_EXTENSIONS = ('.mp3', '.flac', '.wav', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.ape', '.ac3', '.dts',
                    '.alac', '.mka', '.mp2', '.mpa', '.aif', '.caf', '.amr', '.midi', '.mid', '.oga')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tga', '.ico', '.psd', '.raw',
                    '.heic', '.heif', '.avif', '.jp2', '.j2k', '.cr2', '.nef', '.arw', '.orf', '.rw2', '.dng')
DOCUMENT_EXTENSIONS = ('.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.epub',
                       '.mobi', '.azw', '.azw3', '.md', '.csv', '.tsv', '.tex', '.odp', '.ods', '.odg', '.key',
                       '.numbers', '.pages')
ARCHIVE_EXTENSIONS = ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tar.gz', '.tar.bz2', '.tar.xz', '.iso',
                      '.dmg', '.zst', '.lz', '.lzma', '.lzh', '.cab', '.arj', '.r00', '.r01', '.part1.rar')
EXECUTABLE_EXTENSIONS = ('.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app', '.apk', '.ipa', '.bin', '.run',
                         '.appimage', '.bat', '.cmd', '.ps1', '.sh', '.bash', '.ksh', '.csh', '.vbs', '.jar', '.com')
CODE_EXTENSIONS = ('.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go', '.rs', '.ts', '.jsx',
                   '.tsx', '.vue', '.json', '.xml', '.yml', '.yaml', '.sh', '.bat', '.ps1', '.ini', '.conf', '.toml',
                   '.cfg', '.proto', '.sql', '.kt', '.kts', '.scala', '.hs', '.lua', '.dart', '.r', '.jl', '.m',
                   '.mm', '.h', '.hpp', '.hxx', '.cc', '.svelte', '.astro', '.ejs', '.handlebars', '.hbs',
                   '.mustache', '.pug', '.sass', '.scss', '.less', '.lock', '.editorconfig', '.prettierrc',
                   '.eslintrc', '.babelrc')

# Aggregated set of all known extensions for easy checks
ALL_KNOWN_EXTENSIONS = (
    VIDEO_EXTENSIONS
    + AUDIO_EXTENSIONS
    + IMAGE_EXTENSIONS
    + DOCUMENT_EXTENSIONS
    + ARCHIVE_EXTENSIONS
    + EXECUTABLE_EXTENSIONS
    + CODE_EXTENSIONS
)


def get_video_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, VIDEO_EXTENSIONS)


def get_audio_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, AUDIO_EXTENSIONS)


def get_image_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, IMAGE_EXTENSIONS)


def get_document_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, DOCUMENT_EXTENSIONS)


def get_archive_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, ARCHIVE_EXTENSIONS)


def get_executable_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, EXECUTABLE_EXTENSIONS)


def get_code_file_count(session: Session) -> int:
    return get_file_count_by_extensions(session, CODE_EXTENSIONS)


COUNT_NAME_TORRENTS = "torrents"
COUNT_NAME_TORRENT_FILES = "torrent_files"
COUNT_NAME_TORRENT_FILES_SIZE = "torrent_files_size"
COUNT_NAME_TORRENT_FILES_ARCHIVES = "torrent_files_archives"
COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE = "torrent_files_archives_size"
COUNT_NAME_TORRENT_FILES_CODE_FILES = "torrent_files_code_files"
COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE = "torrent_files_code_files_size"
COUNT_NAME_TORRENT_FILES_DOCUMENTS = "torrent_files_documents"
COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE = "torrent_files_documents_size"
COUNT_NAME_TORRENT_FILES_EXECUTABLES = "torrent_files_executables"
COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE = "torrent_files_executables_size"
COUNT_NAME_TORRENT_FILES_IMAGES = "torrent_files_images"
COUNT_NAME_TORRENT_FILES_IMAGES_SIZE = "torrent_files_images_size"
COUNT_NAME_TORRENT_FILES_AUDIO_FILES = "torrent_files_audio_files"
COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE = "torrent_files_audio_files_size"
COUNT_NAME_TORRENT_FILES_VIDEOS = "torrent_files_videos"
COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE = "torrent_files_videos_size"
# Newly tracked: unknown/other file types (not matching any known category)
COUNT_NAME_TORRENT_FILES_UNKNOWN = "torrent_files_unknown"
COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE = "torrent_files_unknown_size"


def get_count(session: Session, name: str) -> int:
    statement = select(Counts).where(Counts.name == name)
    count = session.exec(statement).one_or_none()
    if count is None:
        return 0
    return count.value


def update_total_torrent_count(session: Session, add: int):
    if add > 0:
        statement = select(Counts).where(Counts.name == COUNT_NAME_TORRENTS)
        count = session.exec(statement).first()
        count.value += add
        session.add(count)
        session.commit()


def update_total_files_size(session: Session, add: int):
    if add > 0:
        statement = select(Counts).where(Counts.name == COUNT_NAME_TORRENT_FILES_SIZE)
        count = session.exec(statement).first()
        count.value += add
        session.add(count)
        session.commit()


def update_file_counts(session: Session, name: str, add: int):
    if add > 0:
        statement = select(Counts).where(Counts.name == name)
        count = session.exec(statement).first()
        if count is None:
            count = Counts(name=name, value=add)
        else:
            count.value += add
        session.add(count)
        session.commit()


def get_size(session: Session, name: str) -> int:
    statement = select(Counts).where(Counts.name == name)
    count = session.exec(statement).one_or_none()
    if count is None:
        return 0
    return count.value


def update_files_size(session: Session, name: str, add: int):
    if add > 0:
        statement = select(Counts).where(Counts.name == name)
        count = session.exec(statement).first()
        if count is None:
            count = Counts(name=name, value=add)
        else:
            count.value += add
        session.add(count)
        session.commit()
