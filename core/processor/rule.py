import enum
from typing import Self

from core.processor.condition import Condition
from core.processor.exception import RuleTypeError


class RuleType(str, enum.Enum):
    ALL = "all"
    ANY = "any"

    @classmethod
    def is_valid(cls, type: str) -> bool:
        return any(enum.value == type for enum in cls)

    @classmethod
    def fetch(cls, type: str) -> Self:
        for _enum in cls:
            if _enum.value == type:
                return _enum
        raise RuleTypeError(f"type '{type} is invalid'")


class Rule:
    type: RuleType
    conditions: list[Condition]

    def __init__(self, type: str, conditions: list) -> None:
        self.type = RuleType.fetch(type)
        self.conditions = []
        self._set_conditions(conditions)

    def _set_conditions(self, conditions: list):
        for condition in conditions:
            con = Condition(condition)
            self.conditions.append(con)
