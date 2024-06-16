import enum
from typing import Optional, Self

from core.processor.exception import ActionTypeError


class ActionType(str, enum.Enum):
    MOVE_MESSAGE = "move_message"
    MARK_AS_READ = "mark_as_read"

    @classmethod
    def fetch(cls, type: str) -> Self:
        for _enum in cls:
            if _enum.value == type:
                return _enum
        raise ActionTypeError(f"type '{type} is invalid'")


class Action:
    type: ActionType
    value: Optional[str]

    def __init__(self, action: dict) -> None:
        self.type = ActionType.fetch(action["type"])
        self.value = action.get("value")
