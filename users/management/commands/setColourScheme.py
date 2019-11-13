from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'set the colourscheme for all users'
    args = "<colour1> <colour2>"

    def add_arguments(self, parser):
        parser.add_argument('colours', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        if not len(kwargs["colours"]) == 2:
            print("needs two colour arguments in hex")

        for u in CustomUser.objects.all():
            u.header_colour = f"#{kwargs['colours'][0]}"
            u.page_colour = f"#{kwargs['colours'][1]}"
            u.save()
