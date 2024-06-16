from typing import Protocol

from core.processor.action import Action
from core.processor.exception import ConditionError, RuleTypeError
from core.processor.rule import Rule


class EmailProcessor(Protocol):
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
            raise RuleTypeError("'type' parameter is missing in rule")

        if conditions is None:
            raise ConditionError("'conditions' parameter is missing in rule")
        self.rule = Rule(rule_type, conditions)

    def _set_actions(self, actions: list):
        for action in actions:
            self.actions.append(Action(action))
