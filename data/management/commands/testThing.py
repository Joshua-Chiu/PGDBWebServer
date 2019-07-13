from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "test command does nothing"

    def add_arguments(self, parser):
        parser.add_argument('amount', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        self.stdout.write("hello world!")
        self.stdout.write(str(kwargs["amount"][0]))

