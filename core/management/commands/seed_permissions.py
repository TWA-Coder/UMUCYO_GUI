from django.core.management.base import BaseCommand
from core.models import Role, RoleOperation

class Command(BaseCommand):
    help = 'Seeds permissions for all roles to access all operations'

    def handle(self, *args, **options):
        roles = Role.objects.all()
        operations = [
            'getTenderInformation',
            'sendAdvancePaymentInformation',
            'sendBidSecurityInformation',
            'getContractInformation',
            'sendCreditLineFacility',
            'sendPerformSecurityInformation',
        ]

        count = 0
        for role in roles:
            for op in operations:
                obj, created = RoleOperation.objects.get_or_create(
                    role=role,
                    operation_name=op,
                    defaults={'is_active': True}
                )
                if created:
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} missing permission entries.'))
        self.stdout.write(self.style.SUCCESS(f'Verified permissions for {self.process_roles} roles.'))

    @property
    def process_roles(self):
         return Role.objects.count()
