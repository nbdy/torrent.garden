import sys

import reflex as rx

from torrent_garden.api.torrent import api as torrent_api
from torrent_garden.utils.backfill_counts import backfill_counts
from torrent_garden.utils.create_ads import create_ads
from torrent_garden.utils.create_clients import create_clients

app = rx.App(
    theme=rx.theme(accent_color="green"),
    api_transformer=torrent_api,
)

from torrent_garden.db.model import Torrent     # noqa
from torrent_garden.db.model import TorrentFile # noqa
from torrent_garden.db.model import Crawler     # noqa
from torrent_garden.db.model import Ad          # noqa

import torrent_garden.ui.page.root              # noqa
import torrent_garden.ui.page.metrics           # noqa
import torrent_garden.ui.page.browse            # noqa
import torrent_garden.ui.page.search_torrents   # noqa
import torrent_garden.ui.page.search_files      # noqa
import torrent_garden.ui.page.torrent           # noqa
import torrent_garden.ui.page.about             # noqa

if not any(arg in sys.argv for arg in ["migrate", "makemigrations", "db", "init"]):
    create_clients()
    create_ads()
    backfill_counts()
