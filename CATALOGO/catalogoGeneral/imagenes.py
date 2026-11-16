"""Utilidades para las fotos de producto (varias por color).

- procesar_imagen: valida, corrige orientacion EXIF, limita a 1600 px y convierte a WebP.
- agregar_imagenes: suma fotos nuevas a un producto+color respetando el maximo de 6.
- normalizar_principal: la foto con menor orden de cada color es la principal.
- eliminar_imagen: borra el registro y el archivo del disco.
"""
import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import Max
from PIL import Image, ImageOps

from .models import Color, ImagenProducto

MAX_FOTOS_POR_COLOR = 6
MAX_LADO_PX = 1600
CALIDAD_WEBP = 82


def procesar_imagen(archivo):
    """Devuelve un ContentFile .webp listo para el ImageField, o None si no es una imagen valida."""
    try:
        archivo.seek(0)
        img = Image.open(archivo)
        img.load()
        img = ImageOps.exif_transpose(img)

        tiene_alfa = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
        img = img.convert('RGBA' if tiene_alfa else 'RGB')

        # thumbnail respeta la proporcion y nunca agranda las imagenes pequenas
        img.thumbnail((MAX_LADO_PX, MAX_LADO_PX), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format='WEBP', quality=CALIDAD_WEBP, method=4)
    except Exception:
        return None
    return ContentFile(buffer.getvalue(), name=f'{uuid.uuid4().hex[:16]}.webp')


def normalizar_principal(producto_id, color_id):
    """Deja es_principal=True solo en la foto de menor orden de ese producto+color."""
    imagenes = list(ImagenProducto.objects.filter(producto_id=producto_id, color_id=color_id))
    for i, imagen in enumerate(imagenes):
        debe = (i == 0)
        if imagen.es_principal != debe:
            imagen.es_principal = debe
            imagen.save(update_fields=['es_principal'])


def agregar_imagenes(producto, color_id, archivos):
    """Suma `archivos` a las fotos que ya tiene el producto para ese color.

    Devuelve (guardadas, avisos): cantidad guardada y lista de textos para mostrar al usuario.
    """
    avisos = []
    if not archivos:
        return 0, avisos

    existentes = ImagenProducto.objects.filter(producto=producto, color_id=color_id)
    cupo = MAX_FOTOS_POR_COLOR - existentes.count()
    ultimo = existentes.aggregate(m=Max('orden'))['m']
    siguiente = 0 if ultimo is None else ultimo + 1

    guardadas = 0
    omitidas_por_cupo = 0
    invalidas = []

    for archivo in archivos:
        if cupo <= 0:
            omitidas_por_cupo += 1
            continue
        contenido = procesar_imagen(archivo)
        if contenido is None:
            invalidas.append(getattr(archivo, 'name', 'archivo'))
            continue
        imagen = ImagenProducto(producto=producto, color_id=color_id, orden=siguiente)
        imagen.imagen.save(contenido.name, contenido, save=False)
        imagen.save()
        siguiente += 1
        cupo -= 1
        guardadas += 1

    normalizar_principal(producto.id, color_id)

    nombre_color = Color.objects.filter(pk=color_id).values_list('nombre', flat=True).first() or color_id
    if omitidas_por_cupo:
        avisos.append(
            f'Color {nombre_color}: el máximo es {MAX_FOTOS_POR_COLOR} fotos. '
            f'Se guardaron {guardadas} y se omitieron {omitidas_por_cupo}.'
        )
    if invalidas:
        avisos.append(f'Color {nombre_color}: no se pudieron leer como imagen: {", ".join(invalidas)}.')
    return guardadas, avisos


def eliminar_imagen(imagen):
    """Borra el archivo del disco y el registro; reasigna la principal del color."""
    producto_id, color_id = imagen.producto_id, imagen.color_id
    imagen.imagen.delete(save=False)
    imagen.delete()
    normalizar_principal(producto_id, color_id)
