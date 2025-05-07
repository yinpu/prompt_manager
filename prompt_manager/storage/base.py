# prompt_manager/storage/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict
from ..types import PromptVersion


class StorageBackend(ABC):
    def __init__(self, root_path: str | Path):
        self.root_path = Path(root_path).expanduser()

    # ---------- project ----------
    @abstractmethod
    def list_projects(self) -> List[str]:
        ...

    # ---------- prompt ----------
    @abstractmethod
    def list_prompts(self, project: str) -> List[str]:
        ...

    @abstractmethod
    def exists_prompt(self, project: str, prompt: str) -> bool:
        ...

    @abstractmethod
    def load_versions(self, project: str, prompt: str) -> List[PromptVersion]:
        ...

    @abstractmethod
    def save_version(
        self, project: str, prompt: str, version: PromptVersion, overwrite: bool = False
    ) -> None:
        ...

    @abstractmethod
    def delete_version(self, project: str, prompt: str, version_name: str) -> None:
        ...

    # ---------- misc ----------
    @abstractmethod
    def mkdir_prompt(self, project: str, prompt: str) -> None:
        ...
