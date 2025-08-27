from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Producto, Modelo, Color, Talla, Marca, ImagenProducto


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('gestion_productos')
    return render(request, 'catalog/confirmar_eliminacion.html', {'producto': producto})


def gestion_marcas(request):
    marcas = Marca.objects.all()
    for marca in marcas:
        print(f'{marca.nombre} hola')
    return render(request, 'marcas.html', {'marcas': marcas})

def guardar_marca(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_marca')
        print(f'{nombre} hola')
        activo = request.POST.get('activo', 'off') == 'on'
        descripcion = request.POST.get('descripcion')
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre de la marca es obligatorio.'})
        
        enviar = Marca(
            nombre=nombre,
            activo=activo,
            descripcion=descripcion
        ) 

        enviar.save()
        marca = Marca.objects.get(nombre=nombre)
        
        return JsonResponse({'success': True, 'marca_id': marca.id})
    
    return render(request, 'marca.html')

def gestion_modelos(request):
    marca = Marca.objects.all()
    modelos = Modelo.objects.select_related('marca').all()
    return render(request, 'modelos.html', {'modelos': modelos,
                                            'marcas': marca})

def guardar_modelo(request):
    if request.method == 'POST':
        marca_id = request.POST.get('marca')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        activo = request.POST.get('activo', 'off') == 'on'
        
        marca = get_object_or_404(Marca, id=marca_id)
        modelo, created = Modelo.objects.update_or_create(
            marca=marca,
            nombre=nombre,
            defaults={'descripcion': descripcion, 'activo': activo}
        )
        
        return JsonResponse({'success': True, 'modelo_id': modelo.id})
    
    marcas = Marca.objects.all()
    return render(request, 'crear_modelo.html', {'marcas': marcas})


def gestion_colores(request):
    colores = Color.objects.all()
    return render(request, 'colores.html', {'colores': colores})   

def guardar_color(request):
    if request.method == 'POST':
        nombre = request.POST.get('color-nombre')

        print(f'{nombre} hola')
        activo = request.POST.get('activo', 'off') == 'on'
        codigo_hex = request.POST.get('colores_hex', '#FFFFFF')        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del color es obligatorio.'})
        
        enviar = Color(
            nombre=nombre,
            codigo_hex=codigo_hex,
            activo=activo,
        )

        enviar.save()
        color = Color.objects.get(nombre=nombre)
        
        return JsonResponse({'success': True, 'color_id': color.id})
    
    return render(request, 'colores.html') 

def gestion_tallas(request):
    tallas = Talla.objects.all()
    return render(request, 'tallas.html', {'tallas': tallas})   

def guardar_talla(request):
    if request.method == 'POST':
        valor = request.POST.get('talla-valor')
        tipo = request.POST.get('tipo-talla', 'NUM')
        orden = request.POST.get('orden', 0)
        
        if not valor:
            return JsonResponse({'success': False, 'error': 'El valor de la talla es obligatorio.'})
        
        enviar = Talla(
            valor=valor,
            tipo=tipo,
            orden=orden
        )

        enviar.save()
        talla = Talla.objects.get(valor=valor)
        
        return JsonResponse({'success': True, 'talla_id': talla.id})
    
    return render(request, 'tallas.html')

def cargar_tallas(request):
    tallas = Talla.objects.all().values('id', 'valor', 'tipo')
    tallas_list = list(tallas)
    return JsonResponse(tallas_list, safe=False)


def gestion_productos(request):
    productos = Producto.objects.select_related('modelo__marca', 'color', 'talla').all()
    marca = Marca.objects.all()
    modelos = Modelo.objects.all()
    colores = Color.objects.all()
    return render(request, 'productos.html', {'productos': productos
                                              , 'marcas': marca
                                              , 'modelos': modelos
                                              , 'colores': colores})  

def obtener_productos(request): 
    productos = Producto.objects.select_related('modelo', 'modelo__marca').prefetch_related('colores', 'tallas').all()
    productos_list = []
    
    for producto in productos:
        producto_dict = {
            'id': producto.id,
            'marca': producto.modelo.marca.nombre if producto.modelo and producto.modelo.marca else 'N/A',
            'modelo': producto.modelo.nombre if producto.modelo else 'N/A',
            'color': producto.obtener_colores_str(),  # String con colores
            'talla': producto.obtener_tallas_str(),   # String con tallas
            'precio': str(producto.precio),
            'stock': producto.stock,
            'activo': producto.activo
        }
        productos_list.append(producto_dict)
    
    return JsonResponse(productos_list, safe=False)

def guardar_producto(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            modelo_id = request.POST.get('modelo')
            colores_ids = request.POST.get('colores', '').split(',')  # Nuevo: colores como lista
            tallas_ids = request.POST.get('tallas', '').split(',')
            precio = request.POST.get('precio')
            precio_descuento = request.POST.get('descuento', None)
            stock = request.POST.get('stock', 0)
            
            print(f'colores_ids: {colores_ids}')
            # Validaciones
            if not modelo_id or not colores_ids or not tallas_ids or not precio:
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'})
            
            colores_ids = [color_id.strip() for color_id in colores_ids if color_id.strip()]
            tallas_ids = [talla_id.strip() for talla_id in tallas_ids if talla_id.strip()]
            
            if not colores_ids:
                return JsonResponse({'success': False, 'error': 'Debe seleccionar al menos un color.'})
            if not tallas_ids:
                return JsonResponse({'success': False, 'error': 'Debe seleccionar al menos una talla.'})
            
            # Crear el producto
            producto = Producto.objects.create(
                modelo_id=modelo_id,
                precio=precio,
                precio_descuento=precio_descuento if precio_descuento else None,
                stock=stock
            )
            
            # Agregar colores y tallas
            for color_id in colores_ids:
                producto.colores.add(color_id)
            for talla_id in tallas_ids:
                producto.tallas.add(talla_id)
            
            return JsonResponse({
                'success': True, 
                'message': 'Producto creado correctamente',
                'producto_id': producto.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error: {str(e)}'})


def editar_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    tallaObjetoP = producto.tallas.all()  # Obtener las tallas del producto
    # Obtener todas las tallas para mostrar en el formulario
    tallas = Talla.objects.all().order_by('tipo', 'orden', 'valor')
    
    # Obtener las IDs de las tallas ya asociadas al producto
    tallas_seleccionadas_ids = [talla.id for talla in tallaObjetoP]
    
    # Obtener modelos de la misma marca para el select
    modelos = producto.modelo
    
    
    
    # Obtener todos los colores
    colores = Color.objects.all().order_by('nombre')

    colores_producto = producto.colores.all()  # Asumiendo que la relación se llama 'colores'
    colores_seleccionados_ids = [color.id for color in colores_producto]

    for color in colores:
        print(f'{color.nombre} hola')
    
    if request.method == 'POST':
        # Procesar el formulario de actualización
        modelo_id = request.POST.get('modelo_id')
        color_id = request.POST.get('colores_ids', '').split(',')
        tallas_ids = request.POST.get('tallas_ids', '').split(',')
        precio = request.POST.get('precio')
        precio_descuento = request.POST.get('precio_descuento')
        stock = request.POST.get('stock')
        activo = request.POST.get('activo') == 'true'

        antesComa = precio.split(',')
        if len(antesComa) > 1:
            precio = float(antesComa[0])

        antesComaDescuento = precio_descuento.split(',')
        if len(antesComaDescuento) > 1:
            precio_descuento = float(antesComaDescuento[0])

        print(f'vamos bien hasta aqui {modelo_id} {color_id} {tallas_ids} {type(precio)} {type(precio_descuento)} {type(int(stock))} {activo}')

        try:
            # Actualizar el producto
            producto.precio = precio
            producto.precio_descuento = precio_descuento if precio_descuento else None
            producto.stock = int(stock) if stock else 0
            producto.activo = activo
            
            print(f'vamos bien hasta aqui 2 {producto.precio} {producto.precio_descuento} {producto.stock} {producto.activo}')
            # Guardar cambios
            producto.save()
            print('Producto actualizado correctamente')
            # Actualizar las tallas (relación ManyToMany)
            producto.tallas.clear()

            for talla_id in tallas_ids:
                print(f'talla id: {talla_id}')
                if talla_id:  # Evitar IDs vacíos
                    producto.tallas.add(talla_id)

            print('Tallas actualizadas correctamente')

            # Actualizar los colores (relación ManyToMany)
            producto.colores.clear()

            print(f'no hace el recorrifo {(color_id)}')
            for color in color_id:
                print(f'color id: {color}')
                if color:  # Evitar IDs vacíos
                    producto.colores.add(color)

            print('Colores actualizados correctamente')

            for color_id in color_id:
                file_key = f'imagen_color_{color_id}'
                
                if file_key in request.FILES:
                    imagen_file = request.FILES[file_key]
                    
                    # Buscar o crear imagen para este color-producto
                    try:
                        imagen_producto, created = ImagenProducto.objects.get_or_create(
                            producto=producto,
                            color_id=color_id,
                            defaults={'imagen': imagen_file}
                        )
                        
                        if not created:
                            # Actualizar imagen existente
                            imagen_producto.imagen = imagen_file
                            imagen_producto.save()
                        
                        print(f'✅ Imagen {"creada" if created else "actualizada"} para color {color_id}')

                        
                    except Exception as e:
                        print(f'❌ Error al procesar imagen para color {color_id}: {e}')

            return redirect('gestion_productos')
            
        except Exception as e:
            # En caso de error, mostrar el formulario con mensaje de error
            return render(request, 'editar_producto.html', {
                'producto': producto,
                'tallas': tallas,
                'tallas_seleccionadas_ids': tallas_seleccionadas_ids,
                'modelos': modelos,
                'colores': colores,
                'colores_seleccionados_ids': colores_seleccionados_ids,  # Esto es lo importante
                'error': f'Error al actualizar el producto: {str(e)}'
            })
        
        
    
    # Mostrar formulario de edición
    return render(request, 'editar_producto.html', {
        'producto': producto,
        'tallas': tallas,
        'tallas_seleccionadas_ids': tallas_seleccionadas_ids,
        'modelos': modelos,
        'colores': colores,
        'colores_seleccionados_ids': colores_seleccionados_ids,  # Esto es lo importante

    })

def obtener_modelos_por_marca(request, marca_id):
    modelos = Modelo.objects.filter(marca_id=marca_id).values('id', 'nombre')
    modelos_list = list(modelos)
    return JsonResponse(modelos_list, safe=False)

# views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Marca, Modelo, Producto, Color, Talla

def catalogo_principal(request):
    """Vista principal del catálogo"""
    # Obtener todos los productos activos con sus relaciones
    productos = Producto.objects.filter(activo=True).select_related(
        'modelo__marca'
    ).prefetch_related(
        'colores', 
        'imagenes'  # ← ¡Importante prefetch las imágenes!
    )
    
    # Obtener marcas y colores para los filtros
    marcas = Marca.objects.all()
    listamarca = []
    for marca in marcas:
        if not marca.activo:
            print(f'{marca.nombre} no está activo')
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
    
    return render(request, 'catalogo_principal.html', context)

def productos_por_marca(request, marca_slug=None):
    """Vista para mostrar productos de una marca específica"""
    if marca_slug:
        marca = get_object_or_404(Marca, slug=marca_slug, activo=True)
        productos = Producto.objects.filter(
            modelo__marca=marca, 
            activo=True
        ).select_related('modelo__marca').prefetch_related('colores', 'imagenes')
    else:
        marca = None
        productos = Producto.objects.filter(activo=True).select_related('modelo__marca').prefetch_related('colores', 'imagenes')
    
    marcas = Marca.objects.filter(activo=True)
    colores = Color.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'marca_actual': marca,
        'marcas': marcas,
        'colores': colores,
    }
    
    return render(request, 'productos_por_marca.html', context)

def productos_por_modelo(request, marca_slug, modelo_slug):
    """Vista para mostrar productos de un modelo específico"""
    marca = get_object_or_404(Marca, slug=marca_slug, activo=True)
    modelo = get_object_or_404(Modelo, slug=modelo_slug, marca=marca, activo=True)
    
    productos = Producto.objects.filter(
        modelo=modelo, 
        activo=True
    ).select_related('modelo__marca').prefetch_related('colores', 'imagenes')
    
    marcas = Marca.objects.filter(activo=True)
    colores = Color.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'marca_actual': marca,
        'modelo_actual': modelo,
        'marcas': marcas,
        'colores': colores,
    }
    
    return render(request, 'productos_por_modelo.html', context)

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

def buscar_productos(request):
    """Vista para búsqueda de productos"""
    query = request.GET.get('q', '')
    
    if query:
        productos = Producto.objects.filter(
            Q(modelo__nombre__icontains=query) |
            Q(modelo__marca__nombre__icontains=query) |
            Q(colores__nombre__icontains=query),
            activo=True
        ).select_related('modelo__marca').prefetch_related('colores', 'imagenes').distinct()
    else:
        productos = Producto.objects.filter(activo=True).select_related('modelo__marca').prefetch_related('colores', 'imagenes')
    
    marcas = Marca.objects.filter(activo=True)
    colores = Color.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'query': query,
        'marcas': marcas,
        'colores': colores,
    }
    
    return render(request, 'resultados_busqueda.html', context)

def productos_ofertas(request):
    """Vista para mostrar productos en oferta"""
    productos = Producto.objects.filter(
        precio_descuento__isnull=False,
        activo=True
    ).select_related('modelo__marca').prefetch_related('colores', 'imagenes')
    
    marcas = Marca.objects.filter(activo=True)
    colores = Color.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'marcas': marcas,
        'colores': colores,
        'es_oferta': True,
    }
    
    return render(request, 'productos_ofertas.html', context)

# views.py
def filtrar_productos(request):
    """Vista para filtros avanzados"""
    productos = Producto.objects.filter(activo=True).select_related('modelo__marca').prefetch_related('colores', 'imagenes')
    
    # Obtener parámetros de filtro
    marca_ids = request.GET.getlist('marca')
    color_ids = request.GET.getlist('color')
    talla_ids = request.GET.getlist('talla')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    ordenar = request.GET.get('ordenar', 'nombre')
    
    # Aplicar filtros
    if marca_ids:
        productos = productos.filter(modelo__marca_id__in=marca_ids)
    
    if color_ids:
        productos = productos.filter(colores__id__in=color_ids)
    
    if talla_ids:
        productos = productos.filter(tallas__id__in=talla_ids)
    
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
    
    # Ordenar
    if ordenar == 'precio_asc':
        productos = productos.order_by('precio')
    elif ordenar == 'precio_desc':
        productos = productos.order_by('-precio')
    elif ordenar == 'nombre':
        productos = productos.order_by('modelo__nombre')
    elif ordenar == 'nuevo':
        productos = productos.order_by('-fecha_creacion')
    
    marcas = Marca.objects.filter(activo=True)
    colores = Color.objects.filter(activo=True)
    tallas = Talla.objects.all()
    
    context = {
        'productos': productos,
        'marcas': marcas,
        'colores': colores,
        'tallas': tallas,
        'parametros_filtro': request.GET,
    }
    

    return render(request, 'catalogo/filtrar_productos.html', context)