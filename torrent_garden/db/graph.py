from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlmodel import Session, func, and_, select

from torrent_garden.db.model import Torrent


def get_torrent_creation_timeline(session: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Get torrent creation count grouped by date for the last N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Query to get torrents grouped by creation date
    result = session.exec(
        select(
            func.date(Torrent.created_at).label('date'),
            func.count(Torrent.id).label('count')
        )
        .where(
            and_(
                Torrent.created_at >= start_date,
                Torrent.created_at <= end_date
            )
        )
        .group_by(func.date(Torrent.created_at))
        .order_by(func.date(Torrent.created_at))
    ).all()

    # Create a dictionary for quick lookup
    data_dict = {row.date: row.count for row in result}
    
    # Fill in missing dates with zero counts
    timeline_data = []
    current_date = start_date.date()
    while current_date <= end_date.date():
        timeline_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'count': data_dict.get(current_date, 0)
        })
        current_date += timedelta(days=1)

    return timeline_data


def get_torrent_creation_timeline_hourly(session: Session, hours: int = 24) -> List[Dict[str, Any]]:
    """Get torrent creation count grouped by hour for the last N hours."""
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours)

    # Query to get torrents grouped by hour using PostgreSQL date_trunc
    result = session.exec(
        select(
            func.date_trunc('hour', Torrent.created_at).label('hour'),
            func.count(Torrent.id).label('count')
        )
        .where(
            and_(
                Torrent.created_at >= start_date,
                Torrent.created_at <= end_date
            )
        )
        .group_by(func.date_trunc('hour', Torrent.created_at))
        .order_by(func.date_trunc('hour', Torrent.created_at))
    ).all()

    # Create a dictionary for quick lookup
    data_dict = {row.hour.replace(minute=0, second=0, microsecond=0): row.count for row in result}
    
    # Fill in missing hours with zero counts
    timeline_data = []
    current_hour = start_date.replace(minute=0, second=0, microsecond=0)
    while current_hour <= end_date:
        timeline_data.append({
            'time': current_hour.strftime('%H:00'),
            'count': data_dict.get(current_hour, 0),
            'fullTime': current_hour.strftime('%Y-%m-%d %H:00:00')
        })
        current_hour += timedelta(hours=1)

    return timeline_data


def get_torrent_creation_timeline_minutely(session: Session, minutes: int = 60) -> List[Dict[str, Any]]:
    """Get torrent creation count grouped by minute for the last N minutes."""
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=minutes)

    # Query to get torrents grouped by minute using PostgreSQL date_trunc
    result = session.exec(
        select(
            func.date_trunc('minute', Torrent.created_at).label('minute'),
            func.count(Torrent.id).label('count')
        )
        .where(
            and_(
                Torrent.created_at >= start_date,
                Torrent.created_at <= end_date
            )
        )
        .group_by(func.date_trunc('minute', Torrent.created_at))
        .order_by(func.date_trunc('minute', Torrent.created_at))
    ).all()

    # Create a dictionary for quick lookup
    data_dict = {row.minute.replace(second=0, microsecond=0): row.count for row in result}
    
    # Fill in missing minutes with zero counts
    timeline_data = []
    current_minute = start_date.replace(second=0, microsecond=0)
    while current_minute <= end_date:
        timeline_data.append({
            'time': current_minute.strftime('%H:%M'),
            'count': data_dict.get(current_minute, 0),
            'fullTime': current_minute.strftime('%Y-%m-%d %H:%M:00')
        })
        current_minute += timedelta(minutes=1)

    return timeline_data
