from core.models import UserRole

def user_has_role(user, role_names):
    """
    Check if the user has any of the specified roles.
    role_names can be a single string or a list of strings.
    Superusers always return True.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    
    if isinstance(role_names, str):
        role_names = [role_names]
    
    return UserRole.objects.filter(user=user, role__name__in=role_names).exists()
