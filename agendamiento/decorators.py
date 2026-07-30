from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def rol_requerido(roles_permitidos):
    """
    Decorador para vistas que verifica si el usuario autenticado tiene uno de los roles permitidos.
    `roles_permitidos` debe ser una lista de strings con los nombres exactos de los roles.
    Ejemplo: @rol_requerido(['Secretaria', 'Doctora'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
                
            if request.user.rol and request.user.rol.nombre_rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
                
            # Si no tiene permiso
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator
