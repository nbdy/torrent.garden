from typing import List, Dict

import reflex as rx

from torrent_garden.db.count import (
    get_count,
    COUNT_NAME_TORRENTS,
    COUNT_NAME_TORRENT_FILES,
    COUNT_NAME_TORRENT_FILES_VIDEOS,
    COUNT_NAME_TORRENT_FILES_AUDIO_FILES,
    COUNT_NAME_TORRENT_FILES_IMAGES,
    COUNT_NAME_TORRENT_FILES_DOCUMENTS,
    COUNT_NAME_TORRENT_FILES_ARCHIVES,
    COUNT_NAME_TORRENT_FILES_EXECUTABLES,
    COUNT_NAME_TORRENT_FILES_CODE_FILES,
    COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE,
    get_size,
    COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_IMAGES_SIZE,
    COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE,
    COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE,
    COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE,
    COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE,
    COUNT_NAME_TORRENT_FILES_UNKNOWN,
    COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE,
    get_total_torrent_size,
)
from torrent_garden.db.graph import get_torrent_creation_timeline, get_torrent_creation_timeline_minutely, \
    get_torrent_creation_timeline_hourly


class MetricsState(rx.State):
    is_loading: bool = True

    total_torrent_count: int = 0
    total_torrent_file_count: int = 0

    total_torrent_size: int = 0

    total_video_count: int = 0
    total_audio_count: int = 0
    total_image_count: int = 0
    total_document_count: int = 0
    total_archive_count: int = 0
    total_executable_count: int = 0
    total_code_count: int = 0
    total_unknown_count: int = 0

    total_video_size: int = 0
    total_audio_size: int = 0
    total_image_size: int = 0
    total_document_size: int = 0
    total_archive_size: int = 0
    total_executable_size: int = 0
    total_code_size: int = 0
    total_unknown_size: int = 0

    file_type_count_chart_data: List[Dict[str, int]] = []
    file_type_size_chart_data: List[Dict[str, int]] = []

    torrent_timeline_data: List[Dict[str, any]] = []
    torrent_timeline_hourly_data: List[Dict[str, any]] = []
    torrent_timeline_minutely_data: List[Dict[str, any]] = []

    @rx.event(background=True)
    async def on_mount(self):
        async with self:
            self.is_loading = True

        with rx.session() as session:
            total_torrent_count = get_count(session, COUNT_NAME_TORRENTS)

            total_torrent_file_count = get_count(session, COUNT_NAME_TORRENT_FILES)
            total_torrent_file_size = get_total_torrent_size(session)

            total_video_count = get_count(session, COUNT_NAME_TORRENT_FILES_VIDEOS)
            total_video_size = get_size(session, COUNT_NAME_TORRENT_FILES_VIDEOS_SIZE)

            total_audio_count = get_count(session, COUNT_NAME_TORRENT_FILES_AUDIO_FILES)
            total_audio_size = get_size(session, COUNT_NAME_TORRENT_FILES_AUDIO_FILES_SIZE)

            total_image_count = get_count(session, COUNT_NAME_TORRENT_FILES_IMAGES)
            total_image_size = get_size(session, COUNT_NAME_TORRENT_FILES_IMAGES_SIZE)

            total_document_count = get_count(session, COUNT_NAME_TORRENT_FILES_DOCUMENTS)
            total_document_size = get_size(session, COUNT_NAME_TORRENT_FILES_DOCUMENTS_SIZE)

            total_archive_count = get_count(session, COUNT_NAME_TORRENT_FILES_ARCHIVES)
            total_archive_size = get_size(session, COUNT_NAME_TORRENT_FILES_ARCHIVES_SIZE)

            total_executable_count = get_count(session, COUNT_NAME_TORRENT_FILES_EXECUTABLES)
            total_executable_size = get_size(session, COUNT_NAME_TORRENT_FILES_EXECUTABLES_SIZE)

            total_code_count = get_count(session, COUNT_NAME_TORRENT_FILES_CODE_FILES)
            total_code_size = get_size(session, COUNT_NAME_TORRENT_FILES_CODE_FILES_SIZE)

            total_unknown_count = get_count(session, COUNT_NAME_TORRENT_FILES_UNKNOWN)
            total_unknown_size = get_size(session, COUNT_NAME_TORRENT_FILES_UNKNOWN_SIZE)

            torrent_timeline_data = get_torrent_creation_timeline(session)
            torrent_timeline_hourly_data = get_torrent_creation_timeline_hourly(session, 24)
            torrent_timeline_minutely_data = get_torrent_creation_timeline_minutely(session, 60)

            async with self:
                self.total_torrent_count = total_torrent_count

                self.total_torrent_file_count = total_torrent_file_count
                self.total_torrent_size = total_torrent_file_size

                self.total_video_count = total_video_count
                self.total_video_size = total_video_size

                self.total_audio_count = total_audio_count
                self.total_audio_size = total_audio_size

                self.total_image_count = total_image_count
                self.total_image_size = total_image_size

                self.total_document_count = total_document_count
                self.total_document_size = total_document_size

                self.total_archive_count = total_archive_count
                self.total_archive_size = total_archive_size

                self.total_executable_count = total_executable_count
                self.total_executable_size = total_executable_size

                self.total_code_count = total_code_count
                self.total_code_size = total_code_size
                self.total_unknown_count = total_unknown_count
                self.total_unknown_size = total_unknown_size

                self.file_type_count_chart_data = [
                    {"name": "Videos", "value": self.total_video_count, "fill": "#8884d8", "label": f"Videos: {self._format_count(self.total_video_count)}"},
                    {"name": "Music", "value": self.total_audio_count, "fill": "#82ca9d", "label": f"Music: {self._format_count(self.total_audio_count)}"},
                    {"name": "Images", "value": self.total_image_count, "fill": "#ffc658", "label": f"Images: {self._format_count(self.total_image_count)}"},
                    {"name": "Documents", "value": self.total_document_count, "fill": "#ff7300", "label": f"Documents: {self._format_count(self.total_document_count)}"},
                    {"name": "Archives", "value": self.total_archive_count, "fill": "#00c49f", "label": f"Archives: {self._format_count(self.total_archive_count)}"},
                    {"name": "Executables", "value": self.total_executable_count, "fill": "#ff8042", "label": f"Executables: {self._format_count(self.total_executable_count)}"},
                    {"name": "Code files", "value": self.total_code_count, "fill": "#0088fe", "label": f"Code files: {self._format_count(self.total_code_count)}"},
                    {"name": "Unknown", "value": self.total_unknown_count, "fill": "#999999", "label": f"Unknown: {self._format_count(self.total_unknown_count)}"},
                ]
                self.file_type_size_chart_data = [
                    {"name": "Videos", "value": self.total_video_size, "fill": "#8884d8", "label": f"Videos: {self._format_size(self.total_video_size)}"},
                    {"name": "Music", "value": self.total_audio_size, "fill": "#82ca9d", "label": f"Music: {self._format_size(self.total_audio_size)}"},
                    {"name": "Images", "value": self.total_image_size, "fill": "#ffc658", "label": f"Images: {self._format_size(self.total_image_size)}"},
                    {"name": "Documents", "value": self.total_document_size, "fill": "#ff7300", "label": f"Documents: {self._format_size(self.total_document_size)}"},
                    {"name": "Archives", "value": self.total_archive_size, "fill": "#00c49f", "label": f"Archives: {self._format_size(self.total_archive_size)}"},
                    {"name": "Executables", "value": self.total_executable_size, "fill": "#ff8042", "label": f"Executables: {self._format_size(self.total_executable_size)}"},
                    {"name": "Code files", "value": self.total_code_size, "fill": "#0088fe", "label": f"Code files: {self._format_size(self.total_code_size)}"},
                    {"name": "Unknown", "value": self.total_unknown_size, "fill": "#999999", "label": f"Unknown: {self._format_size(self.total_unknown_size)}"},
                ]

                self.torrent_timeline_data = torrent_timeline_data
                self.torrent_timeline_hourly_data = torrent_timeline_hourly_data
                self.torrent_timeline_minutely_data = torrent_timeline_minutely_data
        async with self:
            self.is_loading = False

    @staticmethod
    def _format_size(size: int) -> str:
        """Format bytes to human readable size."""
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        i = 0
        size_float = float(size)
        while size_float >= 1024 and i < len(units) - 1:
            size_float /= 1024
            i += 1
        return f"{size_float:.2f} {units[i]}"

    @staticmethod
    def _format_count(count: int) -> str:
        units = ['', 'K', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
        i = 0
        count_float = float(count)
        while count_float >= 1000 and i < len(units) - 1:
            count_float /= 1000
            i += 1
        # Do not append unit for the base unit (empty string) other than trimming spaces
        return f"{count_float:.2f} {units[i]}".strip()

    @rx.event
    def on_unmount(self):
        ...
