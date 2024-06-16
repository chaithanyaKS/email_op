from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.processor.condition import Condition, ConditionType
from core.processor.rule import Rule, RuleType


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
