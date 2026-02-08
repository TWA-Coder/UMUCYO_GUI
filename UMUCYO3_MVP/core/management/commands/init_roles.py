from django.core.management.base import BaseCommand
from core.models import Role, RoleOperation

class Command(BaseCommand):
    help = 'Initialize default roles and permissions'

    def handle(self, *args, **options):
        # 1. Define Roles
        roles = ['Admin', 'Manager', 'Underwriter']
        role_objects = {}
        for role_name in roles:
            role, created = Role.objects.get_or_create(name=role_name)
            role_objects[role_name] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))
            else:
                self.stdout.write(f'Role already exists: {role_name}')

        # 2. Define Permissions (Operations per Role)
        operations = [
            'getTenderInformation',
            'sendAdvancePaymentInformation',
            'sendBidSecurityInformation',
            'getContractInformation',
            'sendCreditLineFacility',
            'sendPerformSecurityInformation',
        ]

        # Admin and Underwriter get all operations
        # Manager gets none (View Only)
        target_roles = [role_objects['Admin'], role_objects['Underwriter']]
        
        for role in target_roles:
            for op_name in operations:
                obj, created = RoleOperation.objects.get_or_create(role=role, operation_name=op_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Added permission {op_name} to {role.name}'))
                else:
                     self.stdout.write(f'Permission {op_name} already exists for {role.name}')
