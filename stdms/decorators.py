from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def student_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access Denied: Students only")
    return wrapper

def teacher_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff and not request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access Denied: Teachers only")
    return wrapper


