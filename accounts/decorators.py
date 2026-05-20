from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(*allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login')

            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            tipo = (request.user.tipo_usuario or '').lower()

            if tipo not in [r.lower() for r in allowed_roles]:
                messages.error(request, 'Você não tem permissão.')
                return redirect('home')

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator