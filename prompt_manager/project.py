# prompt_manager/project.py
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Any
from pathlib import Path

from .types import PromptVersion, ModelOutput
from .exceptions import (
    VersionExists,
    VersionNotFound,
    ImportErrorBadFormat,
)
from .storage.base import StorageBackend


# ----------------------------------------------------------------------
# Prompt  ——  一个 prompt（多版本）的聚合对象
# ----------------------------------------------------------------------
@dataclass
class Prompt:
    project: str
    name: str
    backend: StorageBackend
    _versions: List[PromptVersion] = field(default_factory=list)
    _loaded: bool = False

    # ---------- lazy load ----------
    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._versions = self.backend.load_versions(self.project, self.name)
            self._loaded = True

    # ---------- 只读 ----------
    @property
    def versions(self) -> List[PromptVersion]:
        self._ensure_loaded()
        return self._versions

    @property
    def latest(self) -> PromptVersion | None:
        self._ensure_loaded()
        return self._versions[-1] if self._versions else None

    def get_version(self, version_name: str) -> PromptVersion:
        self._ensure_loaded()
        for v in self._versions:
            if v.version == version_name:
                return v
        raise VersionNotFound(version_name)

    # ---------- 写操作 ----------
    def add_version(
        self,
        content: str,
        model_outputs: Dict[str, str | Dict[str, Any]],
        meta: Dict[str, Any] | None = None,
        version: str | None = None,
    ) -> PromptVersion:
        self._ensure_loaded()
        
        # 使用自定义版本号或生成下一个版本号
        if version is not None:
            # 验证版本号格式
            if not PromptVersion.is_valid_version(version):
                raise ValueError(f"无效的版本号格式: {version}")
            
            # 检查版本号是否已存在
            for v in self._versions:
                if v.version == version:
                    raise VersionExists(f"版本 {version} 已存在")
            
            version_name = version
        else:
            version_name = PromptVersion.next_version(self._versions)

        parsed_outputs: Dict[str, ModelOutput] = {}
        for m, val in model_outputs.items():
            if isinstance(val, str):
                parsed_outputs[m] = ModelOutput(model_name=m, output=val)
            else:  # dict
                parsed_outputs[m] = ModelOutput(
                    model_name=m,
                    output=val["output"],
                    meta=val.get("meta", {}),
                )

        pv = PromptVersion(
            version=version_name,
            content=content,
            model_outputs=parsed_outputs,
            meta=meta or {},
        )
        self._versions.append(pv)
        return pv

    def modify_version(
        self,
        version_name: str,
        *,
        content: str | None = None,
        model_outputs: Dict[str, str | Dict[str, Any]] | None = None,
        meta_update: Dict[str, Any] | None = None,
        replace_meta: bool = False,
    ) -> PromptVersion:
        v = self.get_version(version_name)
        if content is not None:
            v.content = content
        if model_outputs is not None:
            for m, val in model_outputs.items():
                if isinstance(val, str):
                    v.model_outputs[m] = ModelOutput(model_name=m, output=val)
                else:
                    v.model_outputs[m] = ModelOutput(
                        model_name=m,
                        output=val["output"],
                        meta=val.get("meta", {}),
                    )
        if meta_update is not None:
            if replace_meta:
                v.meta = meta_update
            else:
                v.meta.update(meta_update)
        return v

    def delete_version(self, version_name: str) -> None:
        self._ensure_loaded()
        self._versions = [v for v in self._versions if v.version != version_name]
        self.backend.delete_version(self.project, self.name, version_name)

    def save(self, overwrite_existing: bool = False) -> None:
        """把内存中的版本写入持久层"""
        self._ensure_loaded()
        disk_versions = {
            v.version for v in self.backend.load_versions(self.project, self.name)
        }
        for v in self._versions:
            if v.version in disk_versions and not overwrite_existing:
                continue
            self.backend.save_version(
                self.project, self.name, v, overwrite=overwrite_existing
            )

    # ---------- 导入 / 导出 ----------
    def export(self, to_file: str | Path) -> Path:
        """导出成 JSON 文件（包含 project/prompt 名及全部版本）"""
        data = {
            "project": self.project,
            "prompt": self.name,
            "versions": [v.to_dict() for v in self.versions],
        }
        to_file = Path(to_file).expanduser()
        to_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        return to_file

    @classmethod
    def _from_export(
        cls,
        backend: StorageBackend,
        file: str | Path,
        dest_path: str | None = None,
    ) -> "Prompt":
        """内部：从导出文件构建 Prompt（未写磁盘）"""
        file = Path(file).expanduser()
        try:
            data = json.loads(file.read_text("utf-8"))
            versions = [PromptVersion.from_dict(d) for d in data["versions"]]
        except Exception as e:
            raise ImportErrorBadFormat(str(e)) from e

        project = data["project"]
        prompt_name = data["prompt"]
        if dest_path:
            dest_path = dest_path.lstrip("/")
            project, prompt_name = dest_path.split("/", 1)

        pr = cls(project=project, name=prompt_name, backend=backend)
        pr._versions = versions
        pr._loaded = True
        return pr

    def add_model_output(
        self,
        version_name: str,
        model_name: str,
        output: str | Dict[str, Any],
    ) -> PromptVersion:
        """向现有版本添加模型输出"""
        v = self.get_version(version_name)
        
        if isinstance(output, str):
            v.model_outputs[model_name] = ModelOutput(model_name=model_name, output=output)
        else:
            v.model_outputs[model_name] = ModelOutput(
                model_name=model_name,
                output=output["output"],
                meta=output.get("meta", {}),
            )
        
        return v

    def select_version(self, version_name: str) -> PromptVersion:
        """选择特定版本作为当前版本"""
        v = self.get_version(version_name)
        # 将选定版本移到列表末尾，使其成为"latest"
        self._versions = [ver for ver in self._versions if ver.version != version_name]
        self._versions.append(v)
        return v


# ----------------------------------------------------------------------
# Project  ——  项目级对象（持有多个 prompt）
# ----------------------------------------------------------------------
@dataclass
class Project:
    name: str
    backend: StorageBackend

    # prompt 列表
    def list_prompts(self) -> List[str]:
        return self.backend.list_prompts(self.name)

    # 获取 / 创建 prompt
    def get_prompt(self, prompt_name: str) -> Prompt:
        if not self.backend.exists_prompt(self.name, prompt_name):
            self.backend.mkdir_prompt(self.name, prompt_name)
        return Prompt(project=self.name, name=prompt_name, backend=self.backend)



