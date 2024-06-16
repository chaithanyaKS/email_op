from typing import Protocol

from core.processor.rule import Rule


class SearchEngine(Protocol):
    def search(self, rule: Rule) -> list: ...
