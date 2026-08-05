from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Paciente, Cita, Entidad
from ..decorators import rol_requerido

@login_required
@rol_requerido(['Secretaria', 'Doctora'])
def pacientes_view(request):
    from django.db.models import Q
    pacientes = Paciente.objects.all().select_related('entidad')
    entidades = Entidad.objects.all()
    
    q = request.GET.get('q')
    if q:
        pacientes = pacientes.filter(
            Q(nombre_completo__icontains=q) |
            Q(nro_documento__icontains=q) |
            Q(correo_electronico__icontains=q)
        )
        
    return render(request, 'agendamiento/pacientes.html', {
        'pacientes': pacientes,
        'entidades': entidades,
        'q': q
    })

@login_required
@rol_requerido(['Secretaria'])
def editar_paciente_view(request, paciente_id):
    if request.method == 'POST':
        paciente = get_object_or_404(Paciente, id=paciente_id)
        
        paciente.nombre_completo = request.POST.get('nombre_completo')
        paciente.telefono = request.POST.get('telefono')
        paciente.correo_electronico = request.POST.get('correo_electronico')
        
        entidad_id = request.POST.get('entidad')
        if entidad_id:
            paciente.entidad_id = entidad_id
            
        paciente.save()
        messages.success(request, 'Datos del paciente actualizados con éxito.')
        
    return redirect('pacientes')

@login_required
@rol_requerido(['Secretaria', 'Doctora'])
def historial_paciente_view(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora_inicio')
    
    return render(request, 'agendamiento/historial_paciente.html', {
        'paciente': paciente,
        'citas': citas
    })
