# prompt_manager/manager.py
from __future__ import annotations
from pathlib import Path
from typing import List
from .storage.filesystem import FileSystemBackend
from .storage.base import StorageBackend
from .project import Project, Prompt
from .exceptions import ImportErrorBadFormat


class PromptManager:
    """
    Facade：统一入口。
    支持：
        - get_prompt("/proj/p1")   # 自动 strip '/'
        - import_prompt("xxx.json", "/newproj/foo")
    """

    def __init__(self, root_path: str | Path, backend: StorageBackend | None = None):
        self.backend = backend or FileSystemBackend(root_path)

    # ---------- project ----------
    def list_projects(self) -> List[str]:
        return self.backend.list_projects()

    def get_project(self, name: str) -> Project:
        # 自动创建目录
        self.backend._project_dir(name).mkdir(parents=True, exist_ok=True)
        return Project(name=name, backend=self.backend)

    # ---------- prompt ----------
    def get_prompt(self, path: str | List[str]) -> Prompt:
        """
        path:  "/project/prompt"  | "project/prompt" | ["project", "prompt"]
        若不存在将自动 mkdir。
        """
        if isinstance(path, str):
            path = path.lstrip("/")
            project_name, prompt_name = path.split("/", 1)
        else:
            project_name, prompt_name = path[0], path[1]

        project = self.get_project(project_name)
        return project.get_prompt(prompt_name)

    # ---------- import / export ----------
    def import_prompt(self, file: str | Path, dest_path: str | None = None) -> Prompt:
        """
        导入 .json 导出的 prompt。
        dest_path: "/proj/name" 若指定则覆盖项目及 prompt 名。
        """
        try:
            pr = Prompt._from_export(self.backend, file, dest_path)
            # 先确保目录存在
            self.backend.mkdir_prompt(pr.project, pr.name)
            pr.save(overwrite_existing=True)
            return pr
        except ImportErrorBadFormat:
            raise
