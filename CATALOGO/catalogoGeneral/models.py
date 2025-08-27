from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TipoMarca(models.Model):
    tipo = (('ropa', 'Ropa'), ('calzado', 'Calzado'), ('accesorio', 'Accesorio'))
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.tipoProducto


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    tipoProducto = models.ManyToManyField(TipoMarca, related_name='marcas')
    def __str__(self):
        return self.nombre

class Modelo(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    tipoProducto = models.ManyToManyField(TipoMarca, related_name='modelos')
    class Meta:
        unique_together = ['marca', 'nombre']
    
    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"

class Color(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    codigo_hex = models.CharField(max_length=7, default='#FFFFFF')
    activo = models.BooleanField(default=True)
    
    
    def __str__(self):
        return self.nombre

class Talla(models.Model):
    TIPO_TALLA = (
        ('NUM', 'Numérica'),
        ('LET', 'Letras (XS, S, M, L, XL)'),
        ('EUR', 'Europea'),
        ('USA', 'Americana'),
    )
    
    valor = models.CharField(max_length=10)
    tipo = models.CharField(max_length=3, choices=TIPO_TALLA, default='NUM')
    orden = models.IntegerField(default=0)  # Para ordenar las tallas
    
    class Meta:
        unique_together = ['valor', 'tipo']
    
    def __str__(self):
        return f"{self.valor} ({self.get_tipo_display()})"

class Producto(models.Model):
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE, related_name='productos')
    colores = models.ManyToManyField(Color, related_name='productos')  # Plural
    tallas = models.ManyToManyField(Talla, related_name='productos')  # Nota el plural
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
        
    def __str__(self):
        return f"{self.modelo}"
    
    def obtener_colores_str(self):
        """Devuelve un string con todos los colores separados por coma"""
        return ", ".join([color.nombre for color in self.colores.all()])
    
    def obtener_tallas_str(self):
        """Devuelve un string con todas las tallas separadas por coma"""
        return ", ".join([talla.valor for talla in self.tallas.all()])

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='imagenes_producto')  # ✅ NUEVO

    imagen = models.ImageField(upload_to='productos/%Y/%m/%d/')
    es_principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        return f"Imagen de {self.producto}"