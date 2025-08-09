import json, hashlib
from datetime import datetime, timezone
import aiohttp, aiofiles, orjson, zstandard as zstd
from pathlib import Path
from .paths import ATT

def month_key(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

async def download_and_store(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as r:
        r.raise_for_status()
        data = await r.read()
    h = sha256_bytes(data)
    sub = ATT / h[:2] / h[2:4]
    sub.mkdir(parents=True, exist_ok=True)
    fp = sub / h
    if not fp.exists():
        async with aiofiles.open(fp, "wb") as f:
            await f.write(data)
    return str(fp)

def zstd_writer(path: Path):
    cctx = zstd.ZstdCompressor(level=9)
    f = path.open("wb")
    return f, cctx.stream_writer(f)

def zstd_reader(path: Path):
    dctx = zstd.ZstdDecompressor()
    f = path.open("rb")
    return f, dctx.stream_reader(f)

def load_ckpt(path: Path) -> dict:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except: return {}

def save_ckpt(path: Path, d: dict):
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def iso_utc(dt) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat()
