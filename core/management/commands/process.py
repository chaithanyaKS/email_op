import json

from django.core.management.base import BaseCommand

from core.models import Email
from core.processor.email_processor import GmailProcessor
from core.processor.process_executor.gmail_executor import GmailProcessExecutor
from core.processor.search_engine.db_search_engine import DBSearchEngine


class Command(BaseCommand):
    help = "Rule based operations on email"

    def add_arguments(self, parser):
        parser.add_argument(
            "file", type=str, help="Path To Organization Configuration File"
        )

    def handle(self, *args, **options):
        try:
            rule_file = options["file"]
            with open(rule_file) as fp:
                rules = json.load(fp)
            process = GmailProcessor()
            search_engine = DBSearchEngine(Email)
            process_executor = GmailProcessExecutor()
            for rule in rules:
                process.add(rule)

            process.execute(search_engine=search_engine, executor=process_executor)
            self.stdout.write(self.style.SUCCESS("All the operation ran successfully"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {rule_file} does not exist"))
