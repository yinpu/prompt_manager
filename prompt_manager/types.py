# prompt_manager/types.py
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List
import re


@dataclass(slots=True)
class ModelOutput:
    model_name: str
    output: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"model_name": self.model_name, "output": self.output, "meta": self.meta}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelOutput":
        return cls(
            model_name=data["model_name"],
            output=data["output"],
            meta=data.get("meta", {}),
        )


@dataclass(slots=True)
class PromptVersion:
    version: str                     # "v0001" 等
    content: str
    model_outputs: Dict[str, ModelOutput]
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # ---------- helpers ----------
    @classmethod
    def next_version(cls, existing: List["PromptVersion"]) -> str:
        if not existing:
            return "v0001"
        # 尝试找出所有数字版本号
        numeric_versions = []
        for p in existing:
            if re.match(r"^v\d+$", p.version):
                try:
                    numeric_versions.append(int(p.version.lstrip("v")))
                except ValueError:
                    continue
        
        if numeric_versions:
            last = max(numeric_versions)
            return f"v{last + 1:04d}"
        else:
            return "v0001"
    
    @classmethod
    def is_valid_version(cls, version: str) -> bool:
        """验证版本号格式是否有效"""
        # 允许 v开头数字 或 自定义格式（字母数字下划线-）
        return bool(re.match(r"^v\d+$|^[a-zA-Z0-9_-]+$", version))

    # ---------- (de)serialize ----------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "content": self.content,
            "model_outputs": {k: v.to_dict() for k, v in self.model_outputs.items()},
            "meta": self.meta,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptVersion":
        return cls(
            version=data["version"],
            content=data["content"],
            model_outputs={
                k: ModelOutput.from_dict(v) for k, v in data["model_outputs"].items()
            },
            meta=data.get("meta", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
