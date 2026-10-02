"""config read from environment/.env"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback").strip()

# With credentials everything works; without them, the service still starts read-only and serves the already
# imported history. It would make no sense to requrie an app registered on spotify, just to **look at** an
# archive that's already on disk.
SPOTIFY_ENABLED = bool(CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)

# path database from the disk
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/lifetime.db"))

if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = ROOT / DATABASE_PATH
    
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "15"))
PLAY_THRESHOLD = float(os.getenv("PLAY_THRESHOLD", "0.75"))
PLAYLIST_NAME_TEMPLATE = os.getenv("PLAYLIST_NAME_TEMPLATE", "Lifetime {year}")
PLAYLIST_PUBLIC = os.getenv("PLAYLIST_PUBLIC", "false").lower() in ("1", "true", "yes")

# cover generated and uploaded to spotify for every yearly playlist
PLAYLIST_COVER = os.getenv("PLAYLIST_COVERS", "true").lower() in ("1", "true", "yes")

# Secret that protects login, flush and cover refresh. If you don't set it, one is generated and saved in the db,
# and the full login URL ends up in the log at the startup: the service is never left open by oversight
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# origins allowed for the frontend (angular spa in dev and prod)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200").split(",")
    if origin.strip()
]

# below this threshold the listen doesn't even make it into the history (noise, instant skips)
MIN_PLAY_MS = int(os.getenv("MIN_PLAY_MS", "5000"))

# minimal scopes: read what's playing, write to your own playlists and upload their cover (ugc-image-upload, without
# which the upload returns 403)
SCOPES = " ".join(
    [
        "user-read-currently-playing",
        "user-read-playback-state",
        "playlist-read-private",
        "playlist-modify-private",
        "playlist-modify-public",
        "ugc-image-upload"
    ]
)

# spotify's hard limit per playlist, hence the split into parts
PLAYLIST_MAX_TRACKS = 10_000

API_BASE = "https://api.spotify.com/v1"
ACCOUNTS_BASE = "https://accounts.spotify.com"

def validate(require_credentials: bool = True) -> None:
    """fails right away if credentials are missing, instead of at the first api round
    
    `require_credentials=False` is for the offline import and the server's read-only mode, which don't call spotify:
    requiring a client id to read a local json file, or to browse the history already in the db, would make
    absolutely no sense
    """
    missing = [
        name
        for name, value in (
            ("SPOTIFY_CLIENT_ID", CLIENT_ID)
            ("SPOTIFY_CLIENT_SECRET", CLIENT_SECRET)
            ("SPOTIFY_REDIRECT_URI", REDIRECT_URI)
        )
        if not value
    ]
    if missing and require_credentials:
        raise RuntimeError(f"missing required env vars: {', '.join(missing)}")
    if "{year}" not in PLAYLIST_NAME_TEMPLATE:
        raise RuntimeError("PLAYLIST_NAME_TEMPLATE must contain '{year}'")
    if not 0 < PLAY_THRESHOLD <= 1:
        raise RuntimeError("PLAY_THRESHOLD must be between 0 and 1")
    if POLL_INTERVAL < 1:
        raise RuntimeError("POLL_INTERVAL must be at least 1 second")
