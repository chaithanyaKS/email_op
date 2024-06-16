import enum
from typing import Any, Literal, Optional, Self

from core.processor.exception import ConditionError, ConditionTypeError

CONDITION_FIELDS = ["from", "subject", "message", "received"]
STRING_PREDICATES = ["contains", "not_contains", "equals", "not_equals"]
DATETIME_PREDICATES = ["less_than", "greater_than"]
FILTERS = ["days"]


class ConditionType(str, enum.Enum):
    STRING = "string"
    DATETIME = "datetime"

    @classmethod
    def fetch(cls, type: str) -> Self:
        for _enum in cls:
            if _enum.value == type:
                return _enum
        raise ConditionTypeError(f"type '{type} is invalid'")


class Condition:
    field: str
    predicate: str
    value: Any
    type: ConditionType
    filter: Optional[Literal["days", "months"]]

    def __init__(self, condition_dict) -> None:
        self._validate_condition_dict(condition_dict)
        self.field = condition_dict["field"]
        self.predicate = condition_dict["predicate"]
        self.value = condition_dict["value"]
        self.type = condition_dict["type"]
        self.filter = condition_dict.get("filter")

    def _validate_condition_dict(self, condition_dict: dict):
        field = condition_dict["field"]
        predicate = condition_dict["predicate"]
        type = condition_dict["type"]
        filter = condition_dict.get("filter")

        if field not in CONDITION_FIELDS:
            raise ConditionError(f"Invalid condition field {field}")

        if type == ConditionType.STRING and predicate not in STRING_PREDICATES:
            raise ConditionError(f"Invalid predicate {predicate} for type {type}")

        if type == ConditionType.DATETIME and predicate not in DATETIME_PREDICATES:
            raise ConditionError(f"Invalid predicate {predicate} for type {type}")

        if filter:
            if type != ConditionType.DATETIME:
                raise ConditionError(f"filter is not supported for {type}")
            if filter not in FILTERS:
                raise ConditionError(f"invalid filter {filter}")
