import json

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import Email
from core.processor.email_processor import GmailProcessor
from core.processor.process_executor.gmail_executor import GmailProcessExecutor
from core.processor.search_engine.db_search_engine import DBSearchEngine


@api_view(["GET"])
def ping(request: Request) -> Response:
    return Response({"detail": "Service is up and running"})


@api_view(["POST"])
def process_email(request: Request) -> Response:
    file = request.FILES.get("file", None)
    if file is None:
        return Response({"detail": "missing file"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validator = FileExtensionValidator(allowed_extensions=["json"])
        validator(file)
        rules = json.load(file)
        if isinstance(rules, dict):
            rules = [rules]

        process = GmailProcessor()
        search_engine = DBSearchEngine(Email)
        process_executor = GmailProcessExecutor()
        for rule in rules:
            process.add(rule)

        process.execute(search_engine=search_engine, executor=process_executor)
        return Response({"detail": "completed"})
    except ValidationError:
        return Response({"detail": "invalid file type"})
