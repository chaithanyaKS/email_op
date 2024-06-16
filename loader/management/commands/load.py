from django.core.management.base import BaseCommand

from loader.loaders import GmailLoader


class Command(BaseCommand):
    help = "Load email data to database"

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("Starting loading process"))
        gmail_loader = GmailLoader()
        gmail_loader.load_data(10)
        self.stdout.write(self.style.SUCCESS("Loading process successfully completed"))
