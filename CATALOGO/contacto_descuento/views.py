from shlex import quote
from urllib.parse import quote_plus
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from catalogoGeneral.models import Producto, Marca, Color
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.urls import reverse


def catalogo_descuento(request):
    """Vista principal del catálogo"""
    # Obtener todos los productos activos con sus relaciones
    productos = Producto.objects.filter(activo=True, precio_descuento__isnull=False).select_related(
        'modelo__marca'
    ).prefetch_related(
        'colores', 
        'imagenes'  # ← ¡Importante prefetch las imágenes!
    )


    # Obtener marcas y colores para los filtros
    productomarca = Producto.objects.filter(precio_descuento__isnull=False, modelo__marca__activo=True)
    marcas = Marca.objects.filter(id__in=productomarca.values_list('modelo__marca_id', flat=True).distinct(), activo=True)
    listamarca = []
    for marca in marcas:

        if not marca.activo:
            print(f'{marca.modelo.marca.nombre} no está activo')
        else:
            listamarca.append(marca)
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
    
    print(f'marcas : {listamarca}')
    print(f'marcas : {type(marcas)}')
    for marca in listamarca:
        print(f'{marca.nombre} hola')

    for color in colores:
        print(f'{color.nombre} hola')
        
    context = {
        'productos': productos,
        'marcas': marcas,
        'colores': colores,
    }
    
    return render(request, 'descuento.html', context)


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
def filtrar_productosDescuento(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            marcas = data.get('marcas', [])
            precio = data.get('precio', '')
            
            
            print(f"Filtros recibidos - Marcas: {marcas}, Precio: {precio}")
            
            # Filtrar productos
            productos = Producto.objects.all()
            
            productos = productos.filter(precio_descuento__isnull=False ).distinct()

            if marcas:     
                productos = productos.filter(modelo__marca__id__in=marcas)             
                print(f"Productos después de filtrar por marcas: {productos.count()}")
                
            if precio:
                if precio == '0-50':
                    productos = productos.filter(precio_descuento__range=(0, 50), precio_descuento__isnull=False, )
                elif precio == '50-100':
                    productos = productos.filter(precio_descuento__range=(50, 100),   precio_descuento__isnull=False)
                elif precio == '100-200':
                    productos = productos.filter(precio_descuento__range=(100, 200) , precio_descuento__isnull=False)
                elif precio == '200+':
                    productos = productos.filter(precio_descuento__gt=200, precio_descuento__isnull=False)
                print(f"Productos después de filtrar por precio: {productos.count()}")
            
           
            
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
            
            print(f"Enviando {len(productos_data)} productos")
            return JsonResponse({'productos': productos_data})
            
        except Exception as e:
            print(f"Error en filtrar_productos: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_detalles_producto(request, producto_id):
    if request.method == 'GET':
        try:
            print(f'Obteniendo detalles del producto con ID: {type(producto_id)}')
            producto = Producto.objects.get(id=producto_id)
            print(f'Producto encontrado: {producto}')
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

            print(f'Producto data: {producto_data}')
            
            # Añadir colores
            for color in producto.colores.all():
                producto_data['colores'].append({
                    'id': color.id,
                    'nombre': color.nombre,
                    'codigo_hex': color.codigo_hex
                })

            print(f'Colores añadidos: {producto_data["colores"]}')
            print(f'data con colores: {producto_data}')
            
            # Añadir imágenes
            for imagen in producto.imagenes.all():
                producto_data['imagenes'].append({
                    'id': imagen.id,
                    'imagen_url': imagen.imagen.url,
                    'color_id': imagen.color.id,
                    'es_principal': imagen.es_principal
                })

            print(f'Imágenes añadidas: {producto_data["imagenes"]}')
            print(f'data con imagenes: {producto_data}')
            
            return JsonResponse(producto_data)
            
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def contacto(request):
    return render(request, 'contacto.html')

def mensaje_wasap(request):
    if request.method == 'POST':
        # Detectar si es iOS
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        es_ios = any(term in user_agent for term in ['iphone', 'ipad', 'ipod', 'ios'])
        
        print(f"User-Agent: {user_agent}")
        print(f"Es iOS: {es_ios}")
        
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name is None and phone is None and subject is None and message is None:
            producto = request.POST.get('productoSeleccionado')
            print(f'Producto seleccionado: {producto}')
            
            try:
                objetoProducto = Producto.objects.get(id=producto)
                print(f'Producto: {objetoProducto.modelo.nombre}')
                
                mensaje = f'Hola estoy interesado en este producto "{objetoProducto.modelo.nombre}", de la Marca: "{objetoProducto.modelo.marca.nombre}", con un precio de {objetoProducto.precio}$'
                # Color y talla elegidos (opcionales) y enlace de la página del producto
                color_elegido = request.POST.get('color')
                talla_elegida = request.POST.get('talla')
                if color_elegido:
                    mensaje += f'. Color: {color_elegido}'
                if talla_elegida:
                    mensaje += f'. Talla: {talla_elegida}'
                enlace_producto = request.build_absolute_uri(reverse('zapato_detalle', args=[objetoProducto.id]))
                mensaje += f'. Ver zapato: {enlace_producto}'
                mensaje_codificado = quote_plus(mensaje)
                
                # Generar URL según el dispositivo
                if es_ios:
                    # ✅ URL que SÍ funciona en iOS
                    url_wasap = f"https://wa.me/584126505112?text={mensaje_codificado}"
                    print(f'URL iOS: {url_wasap}')
                else:
                    # ✅ URL para Android y otros
                    url_wasap = f"https://api.whatsapp.com/send?phone=584126505112&text={mensaje_codificado}"
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'url_wasap': url_wasap,
                        'es_ios': es_ios,
                        'message': 'Mensaje enviado correctamente'
                    })
                    

            except Producto.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado'
                })
        
        # Crear mensaje normal
        mensaje_whatsapp = f"Hola, mi nombre es {name}. Asunto: {subject}. {message}"
        if phone:
            mensaje_whatsapp += f" Mi teléfono es {phone}."
        
        mensaje_codificado = quote_plus(mensaje_whatsapp)
        
        # Generar URL según el dispositivo
        if es_ios:
            # ✅ URL que SÍ funciona en iOS
            url_wasap = f"https://web.whatsapp.com/send?phone=584126505112&text={mensaje_codificado}&app_absent=0"
        else:
            # ✅ URL para Android y otros
            url_wasap = f"https://api.whatsapp.com/send?phone=584126505112&text={mensaje_codificado}"
        
        # Detectar si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'url_wasap': url_wasap,
                'es_ios': es_ios,
                'message': 'Mensaje enviado correctamente'
            })
        else:
            # Para peticiones normales (sin JavaScript)
            return render(request, 'contacto.html', {
                'enviado': True,
                'url_wasap': url_wasap,
                'mensaje': mensaje_whatsapp,
                'es_ios': es_ios
            })
    
    # Si es GET, mostrar el formulario normal
    return render(request, 'contacto.html', {'enviado': False})

def politica_privacidad(request):
    return render(request, 'politica_privacidad.html')

def terminos_condiciones(request):
    return render(request, 'terminos_condiciones.html') 

