import logging
from os import getenv
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# configure basic logging
LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()
_level = getattr(logging, LOG_LEVEL, logging.INFO)
logging.basicConfig(level=_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# environment variables
TORRENT_GARDEN_CLIENT_AUTHENTICATION_ENABLE: bool = getenv("TORRENT_GARDEN_ENABLE_CLIENT_AUTHENTICATION", "0") in ["1", "true", "True"]
TORRENT_GARDEN_CLIENT_AUTHENTICATION_FILE: Optional[str] = getenv("TORRENT_GARDEN_CLIENT_AUTHENTICATION_FILE", None)

TORRENT_GARDEN_ADS_ENABLE: bool = getenv("TORRENT_GARDEN_ADS_ENABLE", "0") in ["1", "true", "True"]
TORRENT_GARDEN_ADS_FILE: Optional[str] = getenv("TORRENT_GARDEN_ADS_FILE", None)

logger = logging.getLogger(__name__)
