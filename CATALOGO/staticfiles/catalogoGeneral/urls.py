# catalog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('modelos/', views.gestion_modelos, name='gestion_modelos'),
    path('modelos/guardar/', views.guardar_modelo, name='guardar_modelo'),
    path('obtener-modelos/<int:marca_id>/', views.obtener_modelos_por_marca, name='obtener-modelos'),
    path('obtener-tallas/', views.cargar_tallas, name='cargar_tallas'),

    path('marcas/', views.gestion_marcas, name='gestion_marcas'),
    path('marcas/guardar/', views.guardar_marca, name='guardar_marca'),
  
    #path('marcas/crear/', views.crear_marca, name='crear_marca'),

    path('colores/', views.gestion_colores, name='gestion_colores'),
    path('colores/guardar/', views.guardar_color, name='guardar_color'),

    path('tallas/', views.gestion_tallas, name='gestion_tallas'),
    path('tallas/guardar/', views.guardar_talla, name='guardar_talla'),

    path('productos/', views.gestion_productos, name='gestion_productos'),
    path('productos/guardar/', views.guardar_producto, name='guardar_producto'),
    path('obtener-productos/', views.obtener_productos, name='obtener_productos'),
    
    path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('actualizar-producto/<int:producto_id>/', views.editar_producto, name='actualizar_producto'),

    path('', views.catalogo_principal, name='catalogo_principal'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('ofertas/', views.productos_ofertas, name='productos_ofertas'),
    path('marca/<slug:marca_slug>/', views.productos_por_marca, name='productos_por_marca'),
    path('marca/<slug:marca_slug>/modelo/<slug:modelo_slug>/', views.productos_por_modelo, name='productos_por_modelo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
]