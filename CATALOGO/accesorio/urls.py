# catalog/urls.py
from django.urls import path
from . import views
from catalogoGeneral import views as catalogo_views
from ropa import views as ropa_views

urlpatterns = [
    path('catalogo_accesorio', views.catalogo_accesorio, name='catalogo_accesorio'),

    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('filtrar-productosAccesorio/', views.filtrar_productosRopa, name='filtrar_productosRopa'),
    path('obtener-detalles-producto/<int:producto_id>/', views.obtener_detalles_producto, name='obtener_detalles_producto'),

]