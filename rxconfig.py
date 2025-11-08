from os import getenv

import reflex as rx
from dotenv import load_dotenv
from reflex.constants import StateManagerMode

load_dotenv()

VALKEY_HOST = getenv("VALKEY_HOST", "valkey")
VALKEY_PORT = getenv("VALKEY_PORT", "6379")

DATABASE_HOST = getenv("DATABASE_HOST", "pgbouncer")
DATABASE_PORT = getenv("DATABASE_PORT", 5432)
DATABASE_USER = getenv("DATABASE_USER", "postgres")
DATABASE_PASS = getenv("DATABASE_PASS", "postgres")
DATABASE_NAME = getenv("DATABASE_NAME", "garden")


def get_redis_uri() -> str:
    return f"redis://{VALKEY_HOST}:{VALKEY_PORT}"


def get_database_uri() -> str:
    return f"postgresql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


config = rx.Config(
    app_name="torrent_garden",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
    ],
    disable_plugins=[
        "reflex.plugins.sitemap.SitemapPlugin"
    ],
    show_built_with_reflex=False,
    telemetry_enabled=False,
    state_manager_mode=StateManagerMode.REDIS,
    redis_url=get_redis_uri(),
    db_url=get_database_uri(),
)
