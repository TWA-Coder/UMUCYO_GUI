from django import template
from core.utils import user_has_role

register = template.Library()

@register.filter
def has_role(user, role_names):
    if not user:
        return False
    # Handle comma-separated string from template
    if isinstance(role_names, str):
        role_list = [r.strip() for r in role_names.split(',')]
    else:
        role_list = role_names
        
    return user_has_role(user, role_list)
