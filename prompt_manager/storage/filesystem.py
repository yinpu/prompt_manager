# prompt_manager/storage/filesystem.py
import json
from pathlib import Path
from typing import List
from ..exceptions import PromptNotFound, ProjectNotFound
from ..types import PromptVersion, ModelOutput
from .base import StorageBackend


class FileSystemBackend(StorageBackend):
    """
    目录结构：
        root/project/prompt/v0001/prompt.txt
                                     /outputs.json
                                     /meta.json
    """

    # ---------------- helpers ----------------
    def _project_dir(self, project: str) -> Path:
        return self.root_path / project

    def _prompt_dir(self, project: str, prompt: str) -> Path:
        return self._project_dir(project) / prompt

    # ---------------- project ----------------
    def list_projects(self) -> List[str]:
        if not self.root_path.exists():
            return []
        return [p.name for p in self.root_path.iterdir() if p.is_dir()]

    # ---------------- prompt -----------------
    def list_prompts(self, project: str) -> List[str]:
        proj = self._project_dir(project)
        if not proj.exists():
            raise ProjectNotFound(project)
        return [p.name for p in proj.iterdir() if p.is_dir()]

    def exists_prompt(self, project: str, prompt: str) -> bool:
        return self._prompt_dir(project, prompt).exists()

    def load_versions(self, project: str, prompt: str) -> List[PromptVersion]:
        pdir = self._prompt_dir(project, prompt)
        if not pdir.exists():
            raise PromptNotFound(f"{project}/{prompt}")

        versions: List[PromptVersion] = []
        for vdir in sorted(pdir.iterdir()):
            if not vdir.is_dir():
                continue
            (prompt_txt, outputs_json) = (vdir / "prompt.txt", vdir / "outputs.json")
            if not prompt_txt.exists() or not outputs_json.exists():
                continue

            content = prompt_txt.read_text(encoding="utf-8")
            raw_outputs = json.loads(outputs_json.read_text(encoding="utf-8"))
            model_outputs = {
                k: ModelOutput(
                    model_name=k,
                    output=v["output"],
                    meta=v.get("meta", {}),
                )
                for k, v in raw_outputs.items()
            }

            meta_path = vdir / "meta.json"
            meta = {}
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))

            versions.append(
                PromptVersion(
                    version=vdir.name,
                    content=content,
                    model_outputs=model_outputs,
                    meta=meta,
                )
            )
        return versions

    def save_version(
        self, project: str, prompt: str, version: PromptVersion, overwrite: bool = False
    ) -> None:
        vdir = self._prompt_dir(project, prompt) / version.version
        if vdir.exists():
            if not overwrite:
                raise FileExistsError(f"{vdir} already exists")
        else:
            vdir.mkdir(parents=True, exist_ok=False)

        (vdir / "prompt.txt").write_text(version.content, encoding="utf-8")

        outputs_json = {
            k: {"output": mo.output, "meta": mo.meta}
            for k, mo in version.model_outputs.items()
        }
        (vdir / "outputs.json").write_text(
            json.dumps(outputs_json, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        (vdir / "meta.json").write_text(
            json.dumps(version.meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def delete_version(self, project: str, prompt: str, version_name: str) -> None:
        vdir = self._prompt_dir(project, prompt) / version_name
        if vdir.exists():
            for f in vdir.iterdir():
                f.unlink()
            vdir.rmdir()

    # ---------------- misc -------------------
    def mkdir_prompt(self, project: str, prompt: str) -> None:
        self._prompt_dir(project, prompt).mkdir(parents=True, exist_ok=True)
