from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

User = get_user_model()

USERS = [
    # ['username', 'password', is_superuser, is_staff, can_view, no_entry, list of permission groups]
    ['pgadmin', '2.718281', True, True, True, False, []],
    ['npetheriot', 'wK7CSZVQnv', True, True, True, False, []],
    ['jdouglas', 'FqkuNHt2Hn', False, False, False, True, ['Athletics', 'Service']],
    ['dlai', 'eNHx4cwpJZ', False, False, True, True, ['Service']],
    ['jtchan', 'PEd7Cbsp5e', False, False, True, True, ['Scholar', 'Service']],
    ['gjones', 'hg5MmWjhzL', True, True, True, False, []],
    ['syip', 'hg5MmWjhzL', False, False, True, True, ['Service']],
]

GROUPS = ['Athletics', 'Service', 'Scholar', 'Fine Arts']
MODELS = ['Student', ]
PERMISSIONS = ['change', ]  # For now only view permission by default for all, others include add, delete, change


class Command(BaseCommand):
    help = 'Creates 4 default groups for users and create pgadmin'

    def handle(self, *args, **options):
        for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            for model in MODELS:
                for permission in PERMISSIONS:
                    name = f'Can {permission} {model}'

                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        logging.warning(f"Permission not found with name '{name}'.")
                        continue

                    new_group.permissions.add(model_add_perm)

        for u in USERS:
            try:
                user = User.objects.create_user(u[0], password=u[1])
            except:
                logging.warning(f"Error creating user with name '{u[0]}'.")
                user = User.objects.get(username=u[0])

            user.is_superuser = u[2]
            user.is_staff = u[3]
            user.can_view = u[4]
            user.no_entry = u[5]
            user.save()

            for group in u[6]:
                Group.objects.get(name=group).user_set.add(user)
            print(f"Updated '{u[0]}' and with groups '{u[6]}'")

        print("Created default user and groups.")
