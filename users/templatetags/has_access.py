from django import template
from users.models import AccessControl

register = template.Library()


@register.filter(name='has_access')
def has_group(user, perm):
    try:
        perm = AccessControl.objects.get(identifier=perm)
    except Exception as e:
        print(f"Can't find permission: {perm}")
        return False

    return perm in user.accesscontrol.all()
