# Torrent Garden

**A DHT Network Research and Educational Tool**

An automated torrent metadata indexer for studying peer-to-peer networks, DHT protocols, and distributed systems.

## ⚠️ Legal Disclaimer

**This software is provided for educational and research purposes only.**

- Designed for studying P2P network protocols and distributed hash table (DHT) systems
- Users are solely responsible for complying with local laws and regulations
- Should only be used to index legal content (Linux ISOs, Creative Commons works, public domain content, etc.)
- The developers do not endorse or encourage any illegal activity
- Content indexed from the DHT network is user-generated and beyond our control

**By using this software, you acknowledge that you understand and accept these terms.**

## Features

- Automated DHT network metadata collection
- Full-text search across torrent and file names
- File categorization by type (videos, audio, documents, archives, code, etc.)
- Real-time statistics dashboard
- RESTful API for crawler integration
- Modern, responsive web interface built with [Reflex](https://reflex.dev/)

## Architecture

**Torrent Garden Server** (this repository)
- Web interface for browsing and searching indexed torrents
- REST API endpoint for receiving data from crawlers
- PostgreSQL database for torrent metadata storage
- Valkey (Redis-compatible) for state management

**DHT Crawler** (companion project: [dhtc-client](https://github.com/nbdy/dhtc-client))
- Connects to BitTorrent DHT network
- Discovers and collects publicly available torrent metadata
- Sends collected data to Torrent Garden server

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Docker and Docker Compose

## Installation

```bash
# Clone and navigate
git clone <repository-url>
cd torrent_garden

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create .env file
cat > .env << EOF
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASS=postgres
DATABASE_NAME=garden
VALKEY_HOST=localhost
VALKEY_PORT=6379
TORRENT_GARDEN_ENABLE_CLIENT_AUTHENTICATION=0
LOG_LEVEL=INFO
EOF

# Start services
docker-compose -f docker-compose-local.yml up -d

# Initialize database
uv run reflex db init
uv run reflex db makemigrations
uv run reflex db migrate

# Run application
uv run reflex run
```

**Access**: http://localhost:3000 (Frontend) | http://localhost:8000 (API)

## API

**Endpoint**: `POST /api/torrent/add`

**Request**:
```json
{
  "name": "crawler-name",
  "token": "crawler-token",
  "torrent": {
    "info_hash": "abc123def456...",
    "name": "Ubuntu 24.04 LTS",
    "size": 4820000000,
    "files": [
      {
        "path": "ubuntu-24.04-desktop-amd64.iso",
        "size": 4820000000
      }
    ]
  }
}
```

**Authentication**: Set `TORRENT_GARDEN_ENABLE_CLIENT_AUTHENTICATION=1` and configure `clients.json` for authenticated mode.

## Database Management

```bash
# Migrations
uv run reflex db makemigrations
uv run reflex db migrate

# Direct access
psql -h localhost -U postgres -d garden

# Backup
docker-compose -f docker-compose-local.yml exec db pg_dump -U postgres garden > backup.sql
```

## License

See LICENSE file.

---

🔬 **Research and educational tool** | ⚖️ **Comply with local laws** | 🚫 **Not for copyright infringement**
