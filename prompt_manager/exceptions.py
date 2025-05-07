# prompt_manager/exceptions.py
class PromptManagerError(Exception):
    """基础异常"""


class ProjectNotFound(PromptManagerError):
    pass


class PromptNotFound(PromptManagerError):
    pass


class VersionExists(PromptManagerError):
    pass


class VersionNotFound(PromptManagerError):
    pass


class ImportErrorBadFormat(PromptManagerError):
    pass
