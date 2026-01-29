from __future__ import annotations
from pathlib import Path
import io
import zipfile

def zip_project(project_path: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in project_path.rglob("*"):
            if p.is_file():
                z.write(p, arcname=p.relative_to(project_path))
    return buf.getvalue()
