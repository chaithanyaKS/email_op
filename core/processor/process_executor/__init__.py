from typing import Protocol

from core.processor import Action


class ProcessExecutor(Protocol):
    def execute(self, actions: list[Action], msg_ids: list[str]): ...
