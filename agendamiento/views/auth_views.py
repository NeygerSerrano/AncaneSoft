from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
import threading
import os
import datetime

from ..models import Usuario, CodigoRecuperacion, ConfiguracionSistema

class EmailThreadAuth(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send()
        except Exception as e:
            print(f"Error enviando correo de recuperación asíncrono: {e}")

def enviar_correo_recuperacion_async(codigo, destinatario):
    try:
        # Usar colores e información genérica de AncaneSoft para los correos del sistema (fuera de sesión)
        color_primario = '#1d8797'
        color_secundario = '#0f3856'
        nombre_clinica = 'AncaneSoft'

        html_content = render_to_string('agendamiento/emails/correo_recuperacion.html', {
            'codigo': codigo,
            'color_primario': color_primario,
            'color_secundario': color_secundario,
            'nombre_clinica': nombre_clinica,
        })
        text_content = f"Tu código de recuperación es: {codigo}"
        email = EmailMultiAlternatives(
            f"Código de Recuperación - {nombre_clinica}",
            text_content,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@mediqqta.com',
            [destinatario]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Logo Logic: Forzar logo de AncaneSoft
        logo_path = os.path.join(settings.BASE_DIR, 'agendamiento', 'static', 'agendamiento', 'img', 'AncaneSoftv2.png')
        filename = 'AncaneSoftv2.png'
            
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
            logo = MIMEImage(logo_data)
            logo.add_header('Content-ID', '<logo>')
            logo.add_header('Content-Disposition', 'inline', filename=filename)
            email.attach(logo)
            
        EmailThreadAuth(email).start()
    except Exception as e:
        print(f"Error preparando correo de recuperación: {e}")

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

def solicitar_recuperacion(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email_input)
            # Desactivar códigos anteriores
            CodigoRecuperacion.objects.filter(usuario=usuario, usado=False).update(usado=True)
            
            # Generar nuevo código de 6 dígitos
            codigo = get_random_string(length=6, allowed_chars='0123456789')
            CodigoRecuperacion.objects.create(usuario=usuario, codigo=codigo)
            
            # Enviar código por correo
            enviar_correo_recuperacion_async(codigo, usuario.email)
            
            request.session['reset_email'] = usuario.email
            messages.success(request, 'Te hemos enviado un código de 6 dígitos a tu correo electrónico.')
            return redirect('ingresar_codigo')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe una cuenta asociada a este correo electrónico.')
            
    return render(request, 'agendamiento/recuperar_password.html')

def ingresar_codigo(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('solicitar_recuperacion')
        
    if request.method == 'POST':
        codigo_input = request.POST.get('codigo')
        try:
            usuario = Usuario.objects.get(email=email)
            # Buscar código válido
            tiempo_limite = timezone.now() - datetime.timedelta(minutes=15)
            codigo_obj = CodigoRecuperacion.objects.filter(
                usuario=usuario, 
                codigo=codigo_input, 
                usado=False,
                creado_en__gte=tiempo_limite
            ).first()
            
            if codigo_obj:
                codigo_obj.usado = True
                codigo_obj.save()
                
                request.session['reset_authorized'] = True
                return redirect('restablecer_contrasena')
            else:
                messages.error(request, 'El código es inválido o ha expirado (15 min).')
        except Usuario.DoesNotExist:
            messages.error(request, 'Error interno. Intente nuevamente.')
            return redirect('solicitar_recuperacion')
            
    return render(request, 'agendamiento/ingresar_codigo.html', {'email': email})

def restablecer_contrasena(request):
    if not request.session.get('reset_authorized'):
        return redirect('solicitar_recuperacion')
        
    if request.method == 'POST':
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')
        
        if pass1 and pass2 and pass1 == pass2:
            email = request.session.get('reset_email')
            try:
                usuario = Usuario.objects.get(email=email)
                usuario.set_password(pass1)
                usuario.save()
                
                # Limpiar sesión
                del request.session['reset_email']
                del request.session['reset_authorized']
                
                messages.success(request, 'Tu contraseña ha sido restablecida con éxito. Ya puedes iniciar sesión.')
                return redirect('login')
            except Usuario.DoesNotExist:
                messages.error(request, 'Error de usuario.')
        else:
            messages.error(request, 'Las contraseñas no coinciden o están vacías.')
            
    return render(request, 'agendamiento/restablecer_password.html')

def logout_view(request):
    logout(request)
    return redirect('login')
