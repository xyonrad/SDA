

import re

def safe_id_create(item_id: str):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", item_id)

