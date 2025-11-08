import json
from pathlib import Path
from typing import Dict

import reflex as rx
from sqlmodel import Session, select

from torrent_garden import TORRENT_GARDEN_ADS_FILE, logger
from torrent_garden.db.model import Ad


def create_ad(session: Session, ad: Dict[str, str]):
    statement = select(Ad).where(Ad.html == ad["html"])
    db_ad = session.exec(statement).one_or_none()
    if db_ad is None:
        logger.info(f"Creating ad: {ad['name']}")
        db_ad = Ad(
            name=ad["name"],
            html=ad["html"]
        )
        session.add(db_ad)
    else:
        logger.debug(f"Updating ad: {ad['name']}")
        db_ad.html = ad["html"]
    session.commit()


def create_ads():
    if TORRENT_GARDEN_ADS_FILE is not None:
        ads_file_path = Path(TORRENT_GARDEN_ADS_FILE)
        if ads_file_path.is_file():
            logger.info(f"Creating ads from file: {ads_file_path}")
            ads = json.loads(ads_file_path.read_text())
            with rx.session() as session:
                for ad in ads:
                    create_ad(session, ad)
        else:
            logger.warning(f"File not found: {ads_file_path}")
