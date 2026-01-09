import os
from typing import Any
from sda import auth
from sda.db import init_engine
from sda.io import *
from loguru import logger
from datetime import datetime, timezone, timedelta
from shapely.geometry import Polygon, mapping, box

LOG_FILE = auth.DefaultDirectories.DATA / "logs" / "sda.log"

def configure_log(level: str = "INFO") -> None:
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        
    logger.remove()
    logger.add(
        LOG_FILE,
        mode='w',
        encoding="utf-8",
        level=level,
        backtrace=True,
        diagnose=False
    )

def main():
    cfg = auth.get_config()
    configure_log(cfg.log_level)
    init_engine(cfg)
    os.makedirs(CDSE_DATA_OUT_DIR, exist_ok=True)
    
    # Stub checks
    AOI_BBOX: Polygon           = box(60.0, 49.0, 180.0, 78.0)
    AOI_GEOJSON: dict[str, Any] = mapping(AOI_BBOX)

    day = datetime(2026, 1, 9, tzinfo=timezone.utc)

    collection = S2_COLLECTION_L2A
    s2_item = search_latest(collection, AOI_GEOJSON, day, fallback_days=14)
    
    s2_product_url = s2_item["Product"].href
    safe_id = safe_id_create(s2_item.id)
    zip_path = CDSE_DATA_OUT_DIR / f"S{collection[-5].upper()}{collection[-3:].upper()}__{safe_id}.zip"

    token = get_token() 

if __name__ == "__main__":
    main()
