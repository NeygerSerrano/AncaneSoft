from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from ..models import Usuario

def login_view(request):
    if request.method == 'POST':
        nro_doc_input = request.POST.get('nro_documento')
        contrasena_input = request.POST.get('password')

        try:
            usuario_db = Usuario.objects.get(nro_documento=nro_doc_input)
            user = authenticate(request, username=usuario_db.username, password=contrasena_input)

            if user is not None:
                login(request, user)
                
                if user.rol and user.rol.nombre_rol == 'Secretaria':
                    return redirect('dashboard') 
                elif user.rol and user.rol.nombre_rol == 'Recepcionista':
                    return redirect('dashboard') 
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, 'La contraseña es incorrecta.')
                
        except Usuario.DoesNotExist:
            messages.error(request, 'El número de documento no está registrado.')

    return render(request, 'agendamiento/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
