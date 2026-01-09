from __future__ import annotations

"""
Resilient HTTP download helpers for large raster assets.
"""

import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

def make_session() -> requests.Session:
    """
    Create a requests.Session with retry logic and pooled connections.
    """
    s = requests.Session()

    retry = Retry(
        total=8,
        connect=5,
        read=5,
        status=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(
        pool_connections=32,
        pool_maxsize=32,
        max_retries=retry,
    )
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    return s

def download(url: str, dst_path: str | Path, token: str, timeout=(10, 600)) -> Path:
    """
    Download a URL to disk with streaming, retries, and progress reporting.

    Args:
        url      – source URL.
        dst_path – destination file path.
        token    – bearer token used in Authorization header.
        timeout  – connect/read timeouts (seconds).
    """
    dst = Path(dst_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Encoding": "identity",  
        "Connection": "keep-alive",
    }

    tmp = dst.with_suffix(dst.suffix + ".part")

    session = make_session()
    with session.get(url, stream=True, headers=headers, timeout=timeout, allow_redirects=True) as r:
        r.raise_for_status()

        total = int(r.headers.get("content-length") or 0)

        chunk_size = 8 * 1024 * 1024          
        file_buffer = 8 * 1024 * 1024         

        with open(tmp, "wb", buffering=file_buffer) as f, tqdm(
            total=total if total > 0 else None,
            unit="B", unit_scale=True,
            desc=dst.name,
            miniters=1,
            mininterval=0.2,                
            maxinterval=1.0
        ) as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                pbar.update(len(chunk))

    os.replace(tmp, dst)
    return dst
