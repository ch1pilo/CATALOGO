# catalog/urls.py
from django.urls import path
from . import views
from catalogoGeneral import views as catalogo_views
from accesorio import views as accesorio_views
urlpatterns = [
    path('catalogo_accesorio', accesorio_views.catalogo_accesorio, name='catalogo_accesorio'),
    path('catalogo_zapatos/', catalogo_views.catalogo_principal, name='catalogo_principal'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('catalogo_ropa', views.catalogo_Ropa, name='catalogo_Ropa'),
    path('filtrar-productosRopa/', views.filtrar_productosRopa, name='filtrar_productosRopa'),
    path('obtener-detalles-producto/<int:producto_id>/', views.obtener_detalles_producto, name='obtener_detalles_producto'),

]