from django.contrib.auth.models import Group

def add_user_status(request):
    if request.user.is_authenticated:
        user_groups=request.user.groups.values_list('name',flat=True)
        is_admin='Admin' in user_groups
    else:
        is_admin=False
    return{'is_admin':is_admin}