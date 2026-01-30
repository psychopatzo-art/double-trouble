# core/storage.py

from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any, List
from .models import Project, Asset


def project_dir(base: Path, project_id: str) -> Path:
    return base / "data" / "projects" / project_id


def ensure_project_dirs(base: Path, project_id: str, categories: List[str]) -> None:
    pdir = project_dir(base, project_id)
    (pdir / "assets").mkdir(parents=True, exist_ok=True)
    for c in categories:
        (pdir / "assets" / c).mkdir(parents=True, exist_ok=True)


def save_project(base: Path, project: Project) -> None:
    pdir = project_dir(base, project.id)
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "project.json").write_text(
        json.dumps(project.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_project(base: Path, project_id: str) -> Project:
    pdir = project_dir(base, project_id)
    raw = json.loads((pdir / "project.json").read_text(encoding="utf-8"))

    assets = [Asset(**a) for a in raw.get("assets", [])]

    # Backward compatibility: older projects may not have orientation
    orientation = raw.get("orientation") or raw.get("preview_config", {}).get("orientation") or "Landscape"

    proj = Project(
        id=raw["id"],
        title=raw.get("title", project_id),
        theme=raw.get("theme", ""),
        style_lock=raw.get("style_lock", ""),
        reels=int(raw.get("reels", 5)),
        rows=int(raw.get("rows", 3)),
        orientation=orientation,
        created_at=float(raw.get("created_at", 0)),
        preview_config=raw.get("preview_config", {}),
        assets=assets,
    )
    return proj


def list_projects(base: Path) -> List[Dict[str, Any]]:
    root = base / "data" / "projects"
    root.mkdir(parents=True, exist_ok=True)

    out: List[Dict[str, Any]] = []
    for p in root.iterdir():
        if not p.is_dir():
            continue
        pj = p / "project.json"
        if pj.exists():
            raw = json.loads(pj.read_text(encoding="utf-8"))
            out.append(
                {
                    "id": raw.get("id", p.name),
                    "title": raw.get("title", p.name),
                    "created_at": raw.get("created_at", 0),
                }
            )

    out.sort(key=lambda x: x["created_at"], reverse=True)
    return out


def add_asset(base: Path, project: Project, asset: Asset) -> None:
    project.assets.insert(0, asset)
    save_project(base, project)
