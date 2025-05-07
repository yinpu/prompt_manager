# prompt_manager/__init__.py
"""
Prompt Manager – LLM prompt/version 管理库
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("prompt_manager")
except PackageNotFoundError:   # 本地开发
    __version__ = "0.2.0"

from .manager import PromptManager      # 外部唯一入口

__all__ = ["PromptManager", "__version__"]
