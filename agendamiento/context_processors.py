from .models import ConfiguracionSistema

def configuracion_sistema(request):
    """
    Context processor para inyectar la configuración del sistema (colores, etc)
    en todas las plantillas.
    """
    try:
        config = ConfiguracionSistema.load()
    except Exception:
        # En caso de que la base de datos no esté lista
        config = None
        
    return {
        'configuracion': config
    }
