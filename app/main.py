import hashlib
import re
import secrets
from datetime import datetime, timezone
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .settings import ROOT_DIR, ALLOWED_BRANDS, CACHE_SECONDS, FEED_USER, FEED_PASS

app = FastAPI(title="Facebook CSV Feeds (Per Brand)")

# only simple safe names like "brand_a" or "nike-2025"
SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9_\-]*$")
PATTERN_SUFFIX = "_facebook_catalog.csv"
PATTERN_GLOB = f"*{PATTERN_SUFFIX}"

# --- Basic Auth ---
security = HTTPBasic()
def require_basic(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, FEED_USER)
    ok_pass = secrets.compare_digest(credentials.password, FEED_PASS)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

def csv_path_for_brand(brand: str) -> Path:
    brand = brand.strip().lower()
    if not SAFE_NAME.match(brand):
        raise HTTPException(status_code=400, detail="invalid brand name")

    # optionally enforce allow-list
    if ALLOWED_BRANDS and brand not in ALLOWED_BRANDS:
        raise HTTPException(status_code=404, detail="brand not allowed")

    # match the actual filename pattern
    filename = f"{brand}{PATTERN_SUFFIX}"
    path = ROOT_DIR / filename

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="CSV not found")
    return path

def file_meta(path: Path):
    s = path.stat()
    last_modified = datetime.fromtimestamp(s.st_mtime, tz=timezone.utc)
    size = s.st_size
    etag = hashlib.sha1(f"{int(s.st_mtime)}:{size}".encode()).hexdigest()
    return last_modified, etag, size

@app.get("/feeds")
def list_feeds(_: str = Depends(require_basic)) -> Dict[str, Any]:
    """
    Lists all *{PATTERN_SUFFIX} files in ROOT_DIR as feed endpoints.
    Extracts the brand from the filename by removing the known suffix.
    """
    csvs: List[Path] = sorted(ROOT_DIR.glob(PATTERN_GLOB))
    items = []
    for p in csvs:
        name = p.name
        if not name.endswith(PATTERN_SUFFIX):
            continue
        brand = name[: -len(PATTERN_SUFFIX)].lower()
        if not SAFE_NAME.match(brand):
            continue
        if ALLOWED_BRANDS and brand not in ALLOWED_BRANDS:
            continue
        items.append({
            "brand": brand,
            "filename": name,
            "url": f"/feed/{brand}.csv",
            "size_bytes": p.stat().st_size,
            "last_modified": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
        })
    return {"feeds": items}

@app.get("/feed/{brand}.csv")
def serve_brand_csv(brand: str, request: Request, _: str = Depends(require_basic)):
    path = csv_path_for_brand(brand)
    last_modified, etag, size = file_meta(path)

    # conditional GET
    inm = request.headers.get("if-none-match")
    if inm and inm.strip('"') == etag:
        return Response(status_code=304)

    ims = request.headers.get("if-modified-since")
    if ims:
        try:
            ims_dt = parsedate_to_datetime(ims)
            if ims_dt.tzinfo is None:
                ims_dt = ims_dt.replace(tzinfo=timezone.utc)
            if last_modified <= ims_dt:
                return Response(status_code=304)
        except Exception:
            pass

    headers = {
        "Content-Type": "text/csv; charset=utf-8",
        "Cache-Control": f"public, max-age={CACHE_SECONDS}, must-revalidate",
        "ETag": f"\"{etag}\"",
        "Last-Modified": formatdate(timeval=last_modified.timestamp(), usegmt=True),
        "Content-Length": str(size),
        "Content-Disposition": f'inline; filename="{path.name}"',
    }
    return FileResponse(path=path, media_type="text/csv; charset=utf-8", headers=headers, filename=path.name)
