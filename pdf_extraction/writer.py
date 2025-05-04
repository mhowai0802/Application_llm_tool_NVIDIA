import json
from pathlib import Path

def write_json(path: str|Path, data) -> None:
    """
    Dump `data` as pretty JSON to `path`.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)