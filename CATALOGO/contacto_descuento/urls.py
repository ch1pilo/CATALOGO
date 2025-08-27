from django.urls import path
from . import views
urlpatterns = [
    path('catalogo_descuento/', views.catalogo_descuento, name='catalogo_descuento'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('filtrar-productosDescuento/', views.filtrar_productosDescuento, name='filtrar_productosDescuentoa'),
    path('obtener-detalles-producto/<int:producto_id>/', views.obtener_detalles_producto, name='obtener_detalles_producto'),

    path('EmpiShoes/Contacto/', views.contacto, name='contacto'),
    path('mensaje_wasap/', views.mensaje_wasap, name='mensaje_wasap'),

    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),

    
]