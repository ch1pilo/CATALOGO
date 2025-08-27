from .models import Marca, Color

def catalogos_context(request):
    return {
        'todas_marcas': Marca.objects.filter(activo=True),
        'todos_colores': Color.objects.filter(activo=True),
    }