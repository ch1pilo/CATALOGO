# catalog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('modelos/', views.gestion_modelos, name='gestion_modelos'),
    path('modelos/guardar/', views.guardar_modelo, name='guardar_modelo'),
    path('editar-modelo/<int:modelo_id>/', views.editar_modelo, name='editar_modelo'),
    path('actualizar-modelo/<int:modelo_id>/', views.actualizar_modelo, name='actualizar_modelo'),
    path('eliminar-modelo/<int:modelo_id>/', views.eliminar_modelo, name='eliminar_modelo'),

    path('obtener-modelos/<int:marca_id>/', views.obtener_modelos_por_marca, name='obtener-modelos'),
    path('obtener-tallas/', views.cargar_tallas, name='cargar_tallas'),
    path('obtener_tipos/', views.obtener_tipos, name='obtener_tipos'),

    path('editar-marca/<int:marca_id>/', views.editar_marca, name='editar_marca'),
    path('actualizar-marca/<int:marca_id>/', views.actualizarMarca, name='actualizar_marca'),
    path('eliminar-marca/<int:marca_id>/', views.eliminar_marca, name='eliminar_marca'),

    path('marcas/', views.gestion_marcas, name='gestion_marcas'),
    path('marcas/guardar/', views.guardar_marca, name='guardar_marca'),
  
    #path('marcas/crear/', views.crear_marca, name='crear_marca'),

    path('colores/', views.gestion_colores, name='gestion_colores'),
    path('colores/guardar/', views.guardar_color, name='guardar_color'),
    path('editar-color/<int:color_id>/', views.editar_color, name='editar_color'),
    path('actualizar-color/<int:color_id>/', views.actualizar_color, name='actualizar_color'),
    path('eliminar-color/<int:color_id>/', views.eliminar_color, name='eliminar_color'),

    path('tallas/', views.gestion_tallas, name='gestion_tallas'),
    path('tallas/guardar/', views.guardar_talla, name='guardar_talla'),
    path('editar-talla/<int:talla_id>/', views.editar_talla, name='editar_talla'),
    path('actualizar-talla/<int:talla_id>/', views.actualizar_talla, name='actualizar_talla'),
    path('eliminar-talla/<int:talla_id>/', views.eliminar_talla, name='eliminar_talla'),

    path('productos/', views.gestion_productos, name='gestion_productos'),
    path('productos/guardar/', views.guardar_producto, name='guardar_producto'),
    path('obtener-productos/', views.obtener_productos, name='obtener_productos'),
    path('eliminar-producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
    path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('actualizar-producto/<int:producto_id>/', views.editar_producto, name='actualizar_producto'),

    path('EmpiShoes/zapatos/catalogo_zapatos', views.catalogo_principal, name='catalogo_principal'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('ofertas/', views.productos_ofertas, name='productos_ofertas'),
    path('marca/<slug:marca_slug>/', views.productos_por_marca, name='productos_por_marca'),
    path('marca/<slug:marca_slug>/modelo/<slug:modelo_slug>/', views.productos_por_modelo, name='productos_por_modelo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    path('filtrar-productos/', views.filtrar_productos, name='filtrar_productos'),
    path('obtener-detalles-producto/<int:producto_id>/', views.obtener_detalles_producto, name='obtener_detalles_producto'),
    path('obtener_tipos_por_marca/<int:marca_id>/', views.obtener_tipos_por_marca, name='obtener_tipos_por_marca'),
    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('logear/', views.logear, name='logear'),
]