import json
from pathlib import Path
from typing import Dict

import reflex as rx
from sqlmodel import Session, select

from torrent_garden import TORRENT_GARDEN_CLIENT_AUTHENTICATION_FILE, logger
from torrent_garden.db.model import Crawler


def create_client(session: Session, client: Dict[str, str]):
    statement = select(Crawler).where(Crawler.name == client["name"])
    db_crawler = session.exec(statement).one_or_none()
    if db_crawler is None:
        logger.info(f"Creating crawler: {client['name']}")
        db_crawler = Crawler(
            name=client["name"],
            token=client["token"],
            torrents=[],
        )
        session.add(db_crawler)
    else:
        logger.debug(f"Updating crawler: {client['name']}")
        db_crawler.token = client["token"]
    session.commit()


def create_clients():
    if TORRENT_GARDEN_CLIENT_AUTHENTICATION_FILE is not None:
        authentication_file_path = Path(TORRENT_GARDEN_CLIENT_AUTHENTICATION_FILE)
        if authentication_file_path.is_file():
            logger.info(f"Creating clients from file: {authentication_file_path}")
            clients = json.loads(authentication_file_path.read_text())
            with rx.session() as session:
                for client in clients:
                    create_client(session, client)
        else:
            logger.warning(f"File not found: {authentication_file_path}")
