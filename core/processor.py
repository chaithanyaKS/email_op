import enum
import os.path
from datetime import timedelta
from typing import Any, Literal, Optional, Protocol, Self

from django.db import models
from django.db.models import Q
from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CONDITION_FIELDS = ["from", "subject", "message", "received"]
STRING_PREDICATES = ["contains", "not_contains", "equals", "not_equals"]
DATETIME_PREDICATES = ["less_than", "greater_than"]
FILTERS = ["days"]
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class InvalidRuleType(Exception):
    pass


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
        raise InvalidRuleType(f"type '{type} is invalid'")


class ConditionType(str, enum.Enum):
    STRING = "string"
    DATETIME = "datetime"

    @classmethod
    def fetch(cls, type: str) -> Self:
        for _enum in cls:
            if _enum.value == type:
                return _enum
        raise InvalidRuleType(f"type '{type} is invalid'")


class ConditionError(Exception):
    pass


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


class ActionType(str, enum.Enum):
    MOVE_MESSAGE = "move_message"
    MARK_AS_READ = "mark_as_read"

    @classmethod
    def fetch(cls, type: str) -> Self:
        for _enum in cls:
            if _enum.value == type:
                return _enum
        raise InvalidRuleType(f"type '{type} is invalid'")


class Action:
    type: ActionType
    value: Optional[str]

    def __init__(self, action: dict) -> None:
        self.type = ActionType.fetch(action["type"])
        self.value = action.get("value")


class InvalidRuleTypeError(Exception):
    pass


class MissingRuleTypeError(Exception):
    pass


class MissingRuleConditionsError(Exception):
    pass


class Process:
    rule: Rule
    actions: list[Action] = []

    def add(self, process_dict: dict):
        rule = process_dict["rule"]
        actions = process_dict["actions"]
        self._set_rule(rule)
        self._set_actions(actions)
        return self

    def _set_rule(self, rule_dict: dict):
        rule_type = rule_dict.get("type", None)
        conditions = rule_dict.get("conditions", None)
        if rule_type is None:
            raise MissingRuleTypeError("'type' parameter is missing in rule")

        if conditions is None:
            raise MissingRuleConditionsError(
                "'conditions' parameter is missing in rule"
            )
        self.rule = Rule(rule_type, conditions)

    def _set_actions(self, actions: list):
        for action in actions:
            self.actions.append(Action(action))


class EmailProcessor(Protocol):
    pass


class SearchEngine(Protocol):
    def search(self, rule: Rule) -> list: ...


class DBSearchEngine:
    CONDITION_FIELDS_TO_DB_FIELDS = {
        "from": "from_email",
        "subject": "subject",
        "message": "message",
        "received": "received_at",
    }
    PREDICATE_DB_FILTER_MAPPINGS = {
        "contains": "icontains",
        "not_contains": "icontains",
        "equals": "iexact",
        "not_equals": "iexact",
        "less_than": "lt",
        "greater_than": "gt",
    }

    STRING_PREDICATES = ["contains", "not_contains", "equals", "not_equals"]
    DATETIME_PREDICATES = ["less_than", "greater_than"]

    def __init__(self, model: type[models.Model]):
        self._model = model

    def search(self, rule: Rule):
        negation_query = Q()
        query = Q()
        if rule.type == RuleType.ALL:
            for condition in rule.conditions:
                if condition.type == ConditionType.STRING:
                    q = self.build_string_query(condition)
                else:
                    q = self.build_datetime_query(condition)
                if "not" in condition.predicate:
                    negation_query &= q
                else:
                    query &= q
        else:
            for condition in rule.conditions:
                if condition.type == ConditionType.STRING:
                    q = self.build_string_query(condition)
                else:
                    q = self.build_datetime_query(condition)
                if "not" in condition.predicate:
                    negation_query &= q
                else:
                    query |= q
        return list(
            self._model.objects.filter(query)
            .exclude(negation_query)
            .values_list("msg_id", flat=True)
        )

    def build_string_query(self, condition: Condition) -> Q:
        query_str = {
            f"{self.CONDITION_FIELDS_TO_DB_FIELDS[condition.field]}__{self.PREDICATE_DB_FILTER_MAPPINGS[condition.predicate]}": condition.value
        }
        return Q(**query_str)

    def build_datetime_query(self, condition: Condition) -> Q:
        delta = {f"{condition.filter}": int(condition.value)}
        q = timezone.now() - timedelta(**delta)
        query_str = {
            f"{self.CONDITION_FIELDS_TO_DB_FIELDS[condition.field]}__{self.PREDICATE_DB_FILTER_MAPPINGS[condition.predicate]}": q
        }
        return Q(**query_str)


class ProcessExecutor(Protocol):
    def execute(self, actions: list[Action], msg_ids: list[str]): ...


class GmailProcessExecutor:
    def __init__(self) -> None:
        self._creds = None
        self._authenticate()

    def execute(self, actions: list[Action], msg_ids: list[str]):
        labels_to_add = []
        labels_to_remove = []
        for action in actions:
            if action.type == ActionType.MOVE_MESSAGE:
                labels_to_add.append(action.value.upper())
            elif action.type == ActionType.MARK_AS_READ:
                labels_to_remove.append("UNREAD")

        service = build("gmail", "v1", credentials=self._creds)
        bt = service.new_batch_http_request()
        for message_id in msg_ids:
            bt.add(
                service.users()
                .messages()
                .modify(
                    userId="me",
                    id=message_id,
                    body={
                        "addLabelIds": labels_to_add,
                        "removeLabelIds": labels_to_remove,
                    },
                )
            )
        bt.execute()

    def _authenticate(self):
        if os.path.exists("token.json"):
            self._creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self._creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self._creds.to_json())


class GmailProcessor:
    def __init__(self) -> None:
        self._processes = []

    def add(self, process_dict: dict):
        process = Process()
        process.add(process_dict)
        self._processes.append(process)
        return self

    def execute(self, search_engine: SearchEngine, executor: ProcessExecutor):
        for process in self._processes:
            msg_ids = search_engine.search(process.rule)
            executor.execute(process.actions, msg_ids)
