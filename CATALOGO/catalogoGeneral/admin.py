from django.contrib import admin
from .models import ImagenProducto

class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'color', 'imagen']
    list_filter = ['producto__modelo__marca']

admin.site.register(ImagenProducto, ImagenProductoAdmin)