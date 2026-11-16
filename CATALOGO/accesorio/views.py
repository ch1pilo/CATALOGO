from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from catalogoGeneral.models import Producto, Marca, Color
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from django.template.loader import render_to_string
import logging
logger = logging.getLogger(__name__)

def catalogo_accesorio(request):
    """Vista principal del catálogo"""
    # Obtener todos los productos activos con sus relaciones
    productos = Producto.objects.filter(activo=True, modelo__tipoProducto__nombre='Accesorio').select_related(
        'modelo__marca'
    ).prefetch_related(
        'colores', 
        'imagenes'  # ← ¡Importante prefetch las imágenes!
    )

    # Obtener marcas y colores para los filtros
    marcas = Marca.objects.filter(tipoProducto__nombre='Accesorio')
    listamarca = []
    for marca in marcas:
        logger.debug(f'marca : {marca.nombre} ')
        for producto in productos:
            logger.debug(f'producto : {producto.modelo.marca.nombre} = {marca.nombre}')
            if producto.modelo.marca.nombre == marca.nombre:
                if marca not in listamarca:
                    listamarca.append(marca)
                    logger.debug(f'marca agregada : {marca.nombre} ')

    colores = Color.objects.filter(activo=True)
    
    # Aplicar filtros si se enviaron en la solicitud
    marca_id = request.GET.get('marca')
    color_id = request.GET.get('color')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    if marca_id:
        productos = productos.filter(modelo__marca_id=marca_id)
    
    if color_id:
        productos = productos.filter(colores__id=color_id)
    
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
    
    logger.debug(f'marcas : {listamarca}')
    logger.debug(f'marcas : {type(marcas)}')
    for marca in listamarca:
        logger.debug(f'{marca.nombre} hola')

    for color in colores:
        logger.debug(f'{color.nombre} hola')
        
    context = {
        'productos': productos,
        'marcas': listamarca,
        'colores': colores,
    }
    
    return render(request, 'catalogo_accesorio.html', context)


def detalle_producto(request, producto_id):
    """Vista para mostrar el detalle de un producto específico"""
    producto = get_object_or_404(
        Producto.objects.select_related('modelo__marca')
                       .prefetch_related('colores', 'tallas', 'imagenes'),
        id=producto_id,
        activo=True
    )
    
    # Productos relacionados (misma marca o mismos colores)
    productos_relacionados = Producto.objects.filter(
        Q(modelo__marca=producto.modelo.marca) | Q(colores__in=producto.colores.all()),
        activo=True
    ).exclude(id=producto.id).distinct()[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    
    return render(request, 'detalle_producto.html', context)

@csrf_exempt  # ¡IMPORTANTE! Añade este decorador
def filtrar_productosRopa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            marcas = data.get('marcas', [])
            precio = data.get('precio', '')
            
            
            logger.debug(f"Filtros recibidos - Marcas: {marcas}, Precio: {precio}")
            
            # Filtrar productos
            productos = Producto.objects.all()
            
            productos = productos.filter(modelo__tipoProducto__nombre='Accesorio').distinct()

            if marcas:
                productos = productos.filter(modelo__marca__id__in=marcas, modelo__tipoProducto__nombre='Accesorio').distinct()
                logger.debug(f"Productos después de filtrar por marcas: {productos.count()}")
                
            if precio:
                if precio == '0-50':
                    
                    productos = productos.filter(
                        Q(precio__lt=50, activo=True, modelo__tipoProducto__nombre='Accesorio') |
                        Q(precio_descuento__lt=50, modelo__tipoProducto__nombre='Accesorio')
                    ).distinct()

                if precio == '50-100':
                    productos = productos.filter(
                        modelo__tipoProducto__nombre='Accesorio', 
                        activo=True
                    ).filter(
                        Q(precio_descuento__isnull=False, precio_descuento__gte=50, precio_descuento__lt=100) |
                        Q(precio_descuento__isnull=True, precio__gte=50, precio__lt=100)
                    ).distinct()
                             

                if precio == '100-200':
                    productos = productos.filter(
                        modelo__tipoProducto__nombre='Accesorio', 
                        activo=True
                    ).filter(
                        Q(precio_descuento__isnull=False, precio_descuento__gte=100, precio_descuento__lt=200) |
                        Q(precio_descuento__isnull=True, precio__gte=100, precio__lt=200)
                    ).distinct()

                if precio == '200+':
                    productos = productos.filter(
                        modelo__tipoProducto__nombre='Accesorio', 
                        activo=True
                    ).filter(
                        Q(precio_descuento__isnull=False, precio_descuento__gte=200,) |
                        Q(precio_descuento__isnull=True, precio__gte=200)
                    ).distinct()
                logger.debug(f"Productos después de filtrar por precio: {productos.count()}")
            
           
            
            # Serializar los productos
            productos_data = []
            for producto in productos:
                # Obtener la URL de la imagen
                imagen_url = ''
                if producto.imagenes.first():
                    imagen_url = producto.imagenes.first().imagen.url
                
                producto_dict = {
                    'id': producto.id,
                    'marca': producto.modelo.marca.nombre,
                    'nombre': producto.modelo.nombre,
                    'precio': float(producto.precio),
                    'precio_descuento': float(producto.precio_descuento) if producto.precio_descuento else None,
                    'colores': [{
                        'nombre': color.nombre,
                        'codigo_hex': color.codigo_hex
                    } for color in producto.colores.all()],
                    'stock': producto.stock,
                    'imagen_url': imagen_url
                }
                productos_data.append(producto_dict)
            
            logger.debug(f"Enviando {len(productos_data)} productos")
            return JsonResponse({'productos': productos_data})
            
        except Exception as e:
            logger.debug(f"Error en filtrar_productos: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_detalles_producto(request, producto_id):
    if request.method == 'GET':
        try:
            logger.debug(f'Obteniendo detalles del producto con ID: {type(producto_id)}')
            producto = Producto.objects.get(id=producto_id)
            logger.debug(f'Producto encontrado: {producto}')
            # Serializar datos del producto
            producto_data = {
                'id': producto.id,
                'marca': producto.modelo.marca.nombre,
                'nombre': producto.modelo.nombre,
                'descripcion': producto.modelo.descripcion,
                'precio': float(producto.precio),
                'precio_descuento': float(producto.precio_descuento) if producto.precio_descuento else None,
                'stock': producto.stock,
                'colores': [],
                'tallas': [talla.valor for talla in producto.tallas.all()],
                'imagenes': []
            }

            logger.debug(f'Producto data: {producto_data}')
            
            # Añadir colores
            for color in producto.colores.all():
                producto_data['colores'].append({
                    'id': color.id,
                    'nombre': color.nombre,
                    'codigo_hex': color.codigo_hex
                })

            logger.debug(f'Colores añadidos: {producto_data["colores"]}')
            logger.debug(f'data con colores: {producto_data}')
            
            # Añadir imágenes
            for imagen in producto.imagenes.all():
                producto_data['imagenes'].append({
                    'id': imagen.id,
                    'imagen_url': imagen.imagen.url,
                    'color_id': imagen.color.id,
                    'es_principal': imagen.es_principal
                })

            logger.debug(f'Imágenes añadidas: {producto_data["imagenes"]}')
            logger.debug(f'data con imagenes: {producto_data}')
            
            return JsonResponse(producto_data)
            
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

