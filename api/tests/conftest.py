import pytest


def rules_json():
    return [
        {
            "rule": {
                "type": "all",
                "conditions": [
                    {
                        "field": "from",
                        "predicate": "contains",
                        "value": "linkedin",
                        "type": "string",
                    },
                    {
                        "field": "subject",
                        "predicate": "contains",
                        "value": "developer",
                        "type": "string",
                    },
                    {
                        "field": "received",
                        "predicate": "less_than",
                        "value": "0",
                        "filter": "days",
                        "type": "datetime",
                    },
                ],
            },
            "actions": [
                {"type": "move_message", "value": "inbox"},
                {"type": "mark_as_read"},
            ],
        },
        {
            "rule": {
                "type": "all",
                "conditions": [
                    {
                        "field": "from",
                        "predicate": "contains",
                        "value": "linkedin",
                        "type": "string",
                    },
                    {
                        "field": "subject",
                        "predicate": "contains",
                        "value": "developer",
                        "type": "string",
                    },
                    {
                        "field": "received",
                        "predicate": "less_than",
                        "value": "2",
                        "filter": "days",
                        "type": "datetime",
                    },
                ],
            },
            "actions": [
                {"type": "move_message", "value": "inbox"},
                {"type": "mark_as_read"},
            ],
        },
    ]
