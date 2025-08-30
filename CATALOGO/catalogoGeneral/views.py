from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, login_required
from django.http import JsonResponse
from .models import Producto, Modelo, Color, Talla, Marca, ImagenProducto, TipoMarca
import json
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout    


def login (request):
    return render(request, 'login.html')

def logear (request):
    usuario = request.POST.get('username')
    password = request.POST.get('password')

    print(f'Usuario: {usuario}, Password: {password}')
    
    usuario_autenticado = authenticate(request, username=usuario, password=password)

    if usuario_autenticado is not None:
        auth_login(request, usuario_autenticado)
        return redirect('gestion_productos')
    else:
        messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
        return redirect('login')
    
def logout(request):
    auth_logout(request)
    return redirect('login')

def autenticar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('gestion_productos')  # Redirige a la página de gestión de productos
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
            return redirect('login')
    return redirect('login')

def obtener_tipos(request):
    tipos = TipoMarca.objects.all().values('id', 'nombre')
    tipos_list = list(tipos)
    print('cargados')
    return JsonResponse(tipos_list, safe=False)


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('gestion_productos')
    return render(request, 'catalog/confirmar_eliminacion.html', {'producto': producto})


@login_required
def gestion_marcas(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    marcas = Marca.objects.all()
    tipo = TipoMarca.objects.all()
    for marca in marcas:
        print(f'{marca.nombre} hola')

    return render(request, 'marcas.html', {'marcas': marcas,
                                           'tipo': tipo})

def guardar_marca(request):
    if request.method == 'POST':
        tipos = request.POST.get('tipos_seleccionados', '').split(',')
        for tipo in tipos:
            print(f'tipo id: {tipo}')
        nombre = request.POST.get('nombre_marca')
        print(f'{nombre} hola')
        descripcion = request.POST.get('descripcion')
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre de la marca es obligatorio.'})
        
        if Marca.objects.filter(nombre=nombre).exists():
            messages.error(request, f'La marca {nombre} ya existe.')
            return redirect('gestion_marcas')

        enviar = Marca(
            nombre=nombre,
            activo=1,
            descripcion=descripcion

        ) 

        enviar.save()
        for tipo_id in tipos:
            print(f'tipo id: {tipo_id}')
            tipo = TipoMarca.objects.get(id=tipo_id)
            enviar.tipoProducto.add(tipo)

        tiposProductos = []
        for i in tipos:
            tipoP = TipoMarca.objects.get(id=i)
            print(f'tipoP: {tipoP.nombre}') 
            tiposProductos.append(tipoP.nombre)
        marca = Marca.objects.get(nombre=nombre)
        
        return render(request, 'confirmacion.html', {'url' : '../../marcas',
                                                    'accion' : 'Marca Creada',
                                                    'nombre' : marca.nombre,
                                                    'tipos' : tiposProductos,
                                                     })
        
    return render(request, 'marca.html')

def actualizarMarca (request, marca_id):
    print(f'Actualizar marca ID: {marca_id}')
    nombre = request.POST.get('nombre')
    if Marca.objects.filter(nombre=nombre).exclude(id=marca_id).exists():
        messages.error(request, f'La marca {nombre} ya existe.')
        return redirect('editar_marca', marca_id=marca_id)
    
    descripcion = request.POST.get('descripcion')  
    activoStr = request.POST.get('activo') 
    print(f'{activoStr} {type(activoStr)} hola activo')
    activo = bool(activoStr) 
    print(f'{activo} {type(activo)} hola activo')
    tipos = request.POST.get('tipos_ids', '').split(',')
    print(f'Actualizar marca ID: {marca_id}, Nombre: {nombre}, Descripción: {descripcion}, Activo: {activo}, Tipos: {tipos}')
    marca = get_object_or_404(Marca, id=marca_id)
    marca.nombre = nombre
    marca.descripcion = descripcion
    marca.activo = activo
    marca.tipoProducto.clear()  # Limpiar tipos anteriores
    listatipos = []
    for tipo_id in tipos:
        print(f'tipo id: {tipo_id}')
        tipo = TipoMarca.objects.get(id=tipo_id)
        listatipos.append(tipo.nombre)
        marca.tipoProducto.add(tipo)
    marca.save()    

    return render(request, 'confirmacion.html', {'url' : '../../marcas',
                                                'accion' : 'Marca Actualizar',
                                                'nombre' : marca.nombre,
                                                'tipos' : listatipos,
                                                 })

def eliminar_marca(request, marca_id):
    print(f'Eliminar marca ID: {marca_id}')
    marca = get_object_or_404(Marca, id=marca_id)
    nombre_marca = marca.nombre  # Guardar el nombre antes de eliminar
    marca.delete()
    return render(request, 'confirmacion.html', {'url' : '../../marcas',
                                                'accion' : 'Marca Eliminada',
                                                'nombre' : nombre_marca,
                                                 })

def obtener_tipos_por_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)
    tipos = marca.tipoProducto.all().values('id', 'nombre')
    print(f'tipos: {tipos}')

    tipos_list = list(tipos)
    return JsonResponse({'tipos' : tipos_list}, safe=False)

@login_required
def gestion_modelos(request):
    # Obtener todos los modelos con sus relaciones precargadas
    modelos = Modelo.objects.select_related('marca').prefetch_related('tipoProducto').all()
    marcas = Marca.objects.all()
    
    
    # Crear una lista de tuplas (modelo, tipos_de_marca)
    listaproductos = []
    
    for modelo in modelos:
        # Obtener los tipos de producto asociados a este modelo
        tipos_del_modelo = modelo.tipoProducto.all()
        
        # Obtener los tipos de producto disponibles para la marca de este modelo
        tipos_de_la_marca = modelo.marca.tipoProducto.all()
        
        print(f'Modelo: {modelo.nombre}, Marca: {modelo.marca.nombre}')
        print(f'Tipos del modelo: {[t.nombre for t in tipos_del_modelo]}')
        print(f'Tipos de la marca: {[t.nombre for t in tipos_de_la_marca]}')
        print('---')
        
        listaproductos.append((modelo, tipos_del_modelo, tipos_de_la_marca))
    
    # Debug
    for i, (modelo, tipos_modelo, tipos_marca) in enumerate(listaproductos, 1):
        print(f'{i}. {modelo.nombre} tiene {tipos_modelo.count()} tipos y su marca tiene {tipos_marca.count()} tipos')
    
    return render(request, 'modelos.html', {
        'modelos': modelos,
        'marcas': marcas,
        'listaproductos': listaproductos,
    })
     
def guardar_modelo(request):
    if request.method == 'POST':
        marca_id = request.POST.get('marca')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        activo = True

        print(f'{activo} {type(activo)} hola activo')
        
        if not nombre or not marca_id:
            return JsonResponse({'success': False, 'error': 'El nombre y la marca del modelo son obligatorios.'})
        
        if Modelo.objects.filter(nombre=nombre, marca_id=marca_id).exists():
            messages.error(request, f'El modelo {nombre} ya existe para esta marca.')
            return redirect('gestion_modelos')
        
        marca = get_object_or_404(Marca, id=marca_id)
        modelo, created = Modelo.objects.update_or_create(
            marca=marca,
            nombre=nombre,
            defaults={'descripcion': descripcion, 'activo': activo}
        )

        tipos = request.POST.get('tipos_seleccionados', '').split(',')
        modelo.tipoProducto.clear()  # Limpiar tipos anteriores
        tipoMarcalista = []
        for tipo_id in tipos:
            print(f'tipo id: {tipo_id}')
            tipo = TipoMarca.objects.get(id=tipo_id)
            tipoMarcalista.append(tipo.nombre)
            modelo.tipoProducto.add(tipo)
        
        return render(request, 'confirmacion.html', {'url' : '../../modelos',
                                                    'accion' : 'Modelo Creado',
                                                    'nombre' : modelo.nombre,
                                                    'tipos' : tipoMarcalista,
                                                     })
    
    
    marcas = Marca.objects.all()
    return render(request, 'crear_modelo.html', {'marcas': marcas})

@login_required
def editar_modelo(request, modelo_id):
    print('--- editar_modelo ---')
    modelo = get_object_or_404(Modelo, id=modelo_id)
    tipoSeleccionado = modelo.tipoProducto.all()
    print(f'tipoSeleccionado: {[t.nombre for t in tipoSeleccionado]}')
    tiposMarca = modelo.marca.tipoProducto.all()
    print(f'tiposMarca: {[t.nombre for t in tiposMarca]}')
    
    return render(request, 'editarModelos.html', {
        'modelo': modelo,
        'tipoSeleccionado': tipoSeleccionado,
        'tiposMarca': tiposMarca,
    })

def actualizar_modelo(request, modelo_id):
    try:
        modelo = get_object_or_404(Modelo, id=modelo_id)
        
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        activo = request.POST.get('activo') == 'true'
        tipos_ids = request.POST.get('tipo_id', '').split(',')
        print(f'tipos_ids (raw): {tipos_ids}')
        
        # Filtrar IDs vacíos
        tipos_ids = [id for id in tipos_ids if id]
        
        # Validaciones
        if not nombre:
            messages.error(request, 'El nombre del modelo es requerido')
            return redirect('editar_modelo', modelo_id=modelo_id)
        
        # Verificar si ya existe otro modelo con el mismo nombre en la misma marca
        if Modelo.objects.filter(marca=modelo.marca, nombre=nombre).exclude(id=modelo_id).exists():
            messages.error(request, f'Ya existe un modelo con el nombre "{nombre}" en esta marca')
            return redirect('editar_modelo', modelo_id=modelo_id)
        
        # Actualizar el modelo
        modelo.nombre = nombre
        modelo.descripcion = descripcion
        modelo.activo = activo
        
        # Actualizar tipos de producto
        tipos_seleccionados = TipoMarca.objects.filter(id__in=tipos_ids)
        modelo.tipoProducto.set(tipos_seleccionados)
        
        modelo.save()
        
        return render(request, 'confirmacion.html', {'url' : '../../modelos',
                                                     'accion' : 'Modelo Actualizado',
                                                     'nombre' : modelo.nombre,
                                                     'tipos' : [t.nombre for t in tipos_seleccionados],
                                                      })
        
    except Exception as e:
        messages.error(request, f'Error al actualizar el modelo: {str(e)}')
        return redirect('editar_modelo', modelo_id=modelo_id)

def eliminar_modelo(request, modelo_id):
    print(f'Eliminar modelo ID: {modelo_id}')
    modelo = get_object_or_404(Modelo, id=modelo_id)
    nombre_modelo = modelo.nombre  # Guardar el nombre antes de eliminar
    modelo.delete()
    return render(request, 'confirmacion.html', {'url' : '../../modelos',
                                                'accion' : 'Modelo Eliminado',
                                                'nombre' : nombre_modelo,
                                                 })

@login_required
def gestion_colores(request):
    colores = Color.objects.all()
    return render(request, 'colores.html', {'colores': colores})   

def guardar_color(request):
    if request.method == 'POST':
        nombre = request.POST.get('color-nombre')

        print(f'{nombre} hola')
        activo = True
        codigo_hex = request.POST.get('colores_hex', '#FFFFFF')        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del color es obligatorio.'})
        
        
        colorEncontrado = Color.objects.filter(nombre=nombre, codigo_hex=codigo_hex).exists()
        print(f'colorEncontrado: {colorEncontrado}')
        
        if Color.objects.filter(nombre=nombre, codigo_hex=codigo_hex).exists():
            messages.error(request, f'El color {nombre} ya existe.')
            return redirect('gestion_colores')
        elif Color.objects.filter(nombre=nombre).exists():
            messages.error(request, f'El nombre del color {nombre} ya existe.')
            return redirect('gestion_colores')
        

        enviar = Color(
            nombre=nombre,
            codigo_hex=codigo_hex,
            activo=activo,
        )

        enviar.save()
        color = Color.objects.get(nombre=nombre)
        
        return render(request, 'confirmacion.html', {'url' : '../../colores',
                                                    'accion' : 'Color Creado',
                                                    'nombre' : color.nombre,
                                                     })
    
    return render(request, 'colores.html') 

@login_required
def editar_color(request, color_id):
    color = get_object_or_404(Color, id=color_id)
    
    context = {
        'color': color,
    }
    return render(request, 'editarColores.html', context)

def actualizar_color(request, color_id):
    print(f'Actualizar color ID: {color_id}')
    nombre = request.POST.get('nombre')
    codigo_hex = request.POST.get('codigo_hex', '#FFFFFF')
    activoStr = request.POST.get('activo')

    if Color.objects.filter(nombre=nombre).exclude(id=color_id).exists():
        messages.error(request, f'El nombre del color {nombre} ya existe.')
        return redirect('editar_color', color_id=color_id)
    elif Color.objects.filter(codigo_hex=codigo_hex).exclude(id=color_id).exists():
        messages.error(request, f'El código HEX {codigo_hex} ya está asignado a otro color.')
        return redirect('editar_color', color_id=color_id)
    
    if activoStr == '1':
        activo = True
    else:
        activo = False
    print(f'{activoStr} {type(activoStr)} hola activo')
    print(f'{activo} {type(activo)} hola activo')
    
    print(f'Actualizar color ID: {color_id}, Nombre: {nombre}, Código HEX: {codigo_hex}, Activo: {activo}')
    
    color = get_object_or_404(Color, id=color_id)
    color.nombre = nombre
    color.codigo_hex = codigo_hex
    color.activo = activo
    color.save()    

    return render(request, 'confirmacion.html', {'url' : '../../colores',
                                                'accion' : 'Color Actualizado',
                                                'nombre' : color.nombre,
                                                 })

def eliminar_color(request, color_id):
    print(f'Eliminar color ID: {color_id}')
    color = get_object_or_404(Color, id=color_id)
    nombre_color = color.nombre  # Guardar el nombre antes de eliminar
    color.delete()
    return render(request, 'confirmacion.html', {'url' : '../../colores',
                                                'accion' : 'Color Eliminado',
                                                'nombre' : nombre_color,
                                                 })

@login_required
def gestion_tallas(request):
    tallas = Talla.objects.all()
    return render(request, 'tallas.html', {'tallas': tallas})   

def guardar_talla(request):
    if request.method == 'POST':
        valor = request.POST.get('talla-valor')
        tipo = request.POST.get('tipo-talla', 'NUM')
        orden = request.POST.get('orden', 0)

        tallaExiste = Talla.objects.filter(valor=valor, tipo=tipo).exists()
        if tallaExiste:
            messages.error(request, f'La talla {valor} de tipo {tipo} ya existe.')
            return redirect('gestion_tallas')
        
        
        if not valor:
            messages.error(request, 'El valor de la talla es obligatorio.')
            return redirect('gestion_tallas')
        
        enviar = Talla(
            valor=valor,
            tipo=tipo,
            orden=orden
        )

        enviar.save()
        talla = Talla.objects.get(valor=valor)
        
        return render(request, 'confirmacion.html', {'url' : '../../tallas',
                                                    'accion' : 'Talla Creada',
                                                    'nombre' : talla.valor,
                                                     })
    
    return render(request, 'tallas.html')

def cargar_tallas(request):
    tallas = Talla.objects.all().values('id', 'valor', 'tipo')
    tallas_list = list(tallas)
    return JsonResponse(tallas_list, safe=False)

def editar_talla(request, talla_id):
    talla = get_object_or_404(Talla, id=talla_id)
    
    context = {
        'talla': talla,
    }
    return render(request, 'editarTallas.html', context)

def actualizar_talla(request, talla_id):
    valor = request.POST.get('valor')

    tallas = Talla.objects.all()
    for i in tallas:
        if i.valor == valor and i.id != talla_id:
            print(f'La talla {valor} ya existe con ID {i.id}')
            messages.error(request, f'La talla {valor} ya existe.')
            return redirect('editar_talla', talla_id=talla_id)
        
    print(f'Actualizar talla ID: {talla_id}')
    tipo = request.POST.get('tipo', 'NUM')
    orden = request.POST.get('orden', 0)
    activo = request.POST.get('activo', 'off') == 'on'
    
    print(f'Actualizar talla ID: {talla_id}, Valor: {valor}, Tipo: {tipo}, Orden: {orden}, Activo: {activo}')
    
    talla = get_object_or_404(Talla, id=talla_id)
    talla.valor = valor
    talla.tipo = tipo
    talla.orden = orden
    talla.activo = activo
    talla.save()    

    return render(request, 'confirmacion.html', {'url' : '../../tallas',
                                                'accion' : 'Talla Actualizada',
                                                'nombre' : talla.valor,
                                                 })

def eliminar_talla(request, talla_id):
    print(f'Eliminar talla ID: {talla_id}')
    talla = get_object_or_404(Talla, id=talla_id)
    nombre_talla = talla.valor  # Guardar el nombre antes de eliminar
    talla.delete()
    return render(request, 'confirmacion.html', {'url' : '../../tallas',
                                                'accion' : 'Talla Eliminada',
                                                'nombre' : nombre_talla,
                                                 })

@login_required
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

            if Producto.objects.filter(modelo_id=modelo_id, colores__id__in=colores_ids, tallas__id__in=tallas_ids).exists():
                messages.error(request, 'El producto con la combinación seleccionada de modelo, color y talla ya existe.')
                return redirect('gestion_productos')
            
            
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
            
            return render(request, 'confirmacion.html', {'url' : '../../productos',
                                                        'accion' : 'Producto Creado',
                                                        'nombre' : producto.modelo.nombre,
                                                         })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error: {str(e)}'})

@login_required
def editar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)
    tipos = TipoMarca.objects.filter(activo=True)
    
    context = {
        'marca': marca,
        'tipos': tipos,
    }
    return render(request, 'editarMarca.html', context)

@login_required
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

def catalogo_principal(request):
    """Vista principal del catálogo"""
    # Obtener todos los productos activos con sus relaciones
    productos = Producto.objects.filter(activo=True, modelo__tipoProducto__nombre='Calzado').select_related(
        'modelo__marca'
    ).prefetch_related(
        'colores', 
        'imagenes'  # ← ¡Importante prefetch las imágenes!
    )

    # Obtener marcas y colores para los filtros
    marcas = Marca.objects.filter(tipoProducto__nombre='Calzado', activo=True).distinct()
    listamarca = []
    for marca in marcas:
        print(f'marca : {marca.nombre} ')
        for producto in productos:
            print(f'producto : {producto.modelo.marca.nombre} = {marca.nombre}')
            if producto.modelo.marca.nombre == marca.nombre:
                listamarca.append(marca)
                print(f'marca agregada : {marca.nombre} ')
       
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
    
    print(f'marcas lista : {listamarca}')
    print(f'marcas : {type(marcas)}')
    print(f'colores : {colores}')
    for marca in listamarca:
        print(f'{marca.nombre} hola')

    for color in colores:
        print(f'{color.nombre} hola')
        
    context = {
        'productos': productos,
        'marcas': listamarca,
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


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # ¡IMPORTANTE! Añade este decorador
def filtrar_productos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            marcas = data.get('marcas', [])
            precio = data.get('precio', '')
            
            
            print(f"Filtros recibidos - Marcas: {marcas}, Precio: {precio}")
            
            # Filtrar productos
            productos = Producto.objects.all()
            
            productos = productos.filter(modelo__tipoProducto__nombre='Calzado', ).distinct()

            if marcas:
                productos = productos.filter(modelo__marca__id__in=marcas, modelo__tipoProducto__nombre='Calzado').distinct()
                print(f"Productos después de filtrar por marcas: {productos.count()}")
                
            if precio:
                if precio == '0-50':
                    
                    productos = productos.filter(
                        Q(precio__lt=50, activo=True, modelo__tipoProducto__nombre='Calzado') |
                        Q(precio_descuento__lt=50, modelo__tipoProducto__nombre='Calzado')
                    ).distinct()

                if precio == '50-100':
                    productos = productos.filter(
                        modelo__tipoProducto__nombre='Calzado', 
                        activo=True
                    ).filter(
                        Q(precio_descuento__isnull=False, precio_descuento__gte=50, precio_descuento__lt=100) |
                        Q(precio_descuento__isnull=True, precio__gte=50, precio__lt=100)
                    ).distinct()
                             

                if precio == '100-200':
                    productos = productos.filter(
                        modelo__tipoProducto__nombre='Calzado', 
                        activo=True
                    ).filter(
                        Q(precio_descuento__isnull=False, precio_descuento__gte=100, precio_descuento__lt=200) |
                        Q(precio_descuento__isnull=True, precio__gte=100, precio__lt=200)
                    ).distinct()

                if precio == '200+':
                    productos = productos.filter(
                        modelo__tipoProducto__nombre='Calzado', 
                        activo=True
                    ).filter(
                        Q(precio_descuento__isnull=False, precio_descuento__gte=200,) |
                        Q(precio_descuento__isnull=True, precio__gte=200)
                    ).distinct()
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

def eliminar_producto(request, producto_id):    
    print(f'Eliminar producto ID: {producto_id}')
    producto = get_object_or_404(Producto, id=producto_id)
    nombre_producto = producto.modelo.nombre  # Guardar el nombre antes de eliminar
    producto.delete()
    return render(request, 'confirmacion.html', {'url' : '../../productos',
                                                'accion' : 'Producto Eliminado',
                                                'nombre' : nombre_producto,
                                                 })