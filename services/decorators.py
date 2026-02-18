from functools import wraps
from django.core.exceptions import PermissionDenied
from core.models import RoleOperation

def require_soap_permission(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user = kwargs.get('user')
            if not user or (not user.is_authenticated and not user.is_superuser):
                 # Guardrail: Return error dict for auth failure
                return {
                    "success": False,
                    "error": "Authentication required",
                    "user_message": "You must be logged in to perform this operation."
                }

            # Superusers bypass checks
            if user.is_superuser:
                return func(self, *args, **kwargs)

            # Check if user has a role with this operation
            has_permission = RoleOperation.objects.filter(
                role__users__user=user,
                operation_name=operation_name,
                is_active=True
            ).exists()

            if not has_permission:
                return {
                    "success": False,
                    "error": "Permission Denied",
                    "user_message": f"User '{user.username}' does not have permission for '{operation_name}'."
                }

            return func(self, *args, **kwargs)
        return wrapper
    return decorator
