# core/models.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import time
import uuid


@dataclass
class Asset:
    id: str
    category: str
    name: str
    prompt: str
    provider: str
    model: str
    created_at: float
    path: str  # relative path within project folder (project root)
    meta: Dict[str, Any]

    @staticmethod
    def new(
        category: str,
        name: str,
        prompt: str,
        provider: str,
        model: str,
        path: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "Asset":
        return Asset(
            id=str(uuid.uuid4()),
            category=category,
            name=name,
            prompt=prompt,
            provider=provider,
            model=model,
            created_at=time.time(),
            path=path,
            meta=meta or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Project:
    id: str
    title: str
    theme: str
    style_lock: str
    reels: int
    rows: int
    orientation: str
    created_at: float
    preview_config: Dict[str, Any]
    assets: List[Asset]

    @staticmethod
    def new(
        title: str,
        theme: str,
        style_lock: str,
        reels: int,
        rows: int,
        preview_config: Dict[str, Any],
        orientation: str,
    ) -> "Project":
        return Project(
            id=str(uuid.uuid4()),
            title=title,
            theme=theme,
            style_lock=style_lock,
            reels=reels,
            rows=rows,
            orientation=orientation,
            created_at=time.time(),
            preview_config=preview_config,
            assets=[],
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["assets"] = [a.to_dict() for a in self.assets]
        return d
