from django.core.management.base import BaseCommand
from core.models import Role

class Command(BaseCommand):
    help = 'Seeds the database with default roles: admin, manager, user'

    def handle(self, *args, **options):
        roles = ['admin', 'manager', 'user']
        for role_name in roles:
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))
            else:
                self.stdout.write(f'Role already exists: {role_name}')
