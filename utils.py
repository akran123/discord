import json, hashlib, os
from datetime import datetime, timezone
from pathlib import Path
import aiohttp, aiofiles, orjson, zstandard as zstd
from dotenv import load_dotenv

load_dotenv()

# .env 예시: BACKUP_BASE=C:/Users/you/Documents/discord-backups
BASE = Path(os.getenv("BACKUP_BASE")).expanduser().resolve()
ARCH = BASE / "archives"
ATT  = BASE / "attachments"
CKPT = BASE / "checkpoints.json"

# 디렉터리 보장
ARCH.mkdir(parents=True, exist_ok=True)
ATT.mkdir(parents=True, exist_ok=True)

if not CKPT.exists():
    CKPT.write_text("{}", encoding="utf-8")

def month_key(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"

def sha256_bytes(b: bytes) -> str:
    """
    바이트 데이터를 SHA-256 해시로 변환하여 64자리 16진수 문자열 반환.
    첨부파일 중복 제거와 폴더 경로 생성에 사용.
    """
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
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_ckpt(path: Path, d: dict):
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def iso_utc(dt) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat()
