from functools import wraps
from django.http import HttpResponseForbidden

def user_in_group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Vous n'êtes pas autorisé à accéder ce page")
        return _wrapped_view
    return decorator
