from django import template
from django.template.defaultfilters import filesizeformat
import os

register = template.Library()

@register.filter
def get_imagen_por_color(imagenes, color_id):
    """Retorna la imagen asociada a un color específico"""
    try:
        color_id = int(color_id)
        for imagen in imagenes:
            # Verificar si la imagen tiene relación con color
            if hasattr(imagen, 'color') and imagen.color and imagen.color.id == color_id:
                return imagen
    except (ValueError, TypeError):
        pass
    return None

@register.filter
def basename(value):
    """Retorna el nombre del archivo de una ruta"""
    if value:
        return os.path.basename(str(value))
    return ''

@register.filter
def get_imagen_principal_por_color(producto, color_id):
    """Obtiene la imagen principal para un color específico"""
    try:
        color_id = int(color_id)
        for imagen in producto.imagenes.all():
            if hasattr(imagen, 'color') and imagen.color and imagen.color.id == color_id and imagen.es_principal:
                return imagen
    except (ValueError, TypeError):
        pass
    return None

@register.filter
def get_imagenes_por_color(imagenes, color_id):
    """Retorna la lista de TODAS las imágenes de un color (en orden)"""
    try:
        color_id = int(color_id)
    except (ValueError, TypeError):
        return []
    return [img for img in imagenes if img.color_id == color_id]
