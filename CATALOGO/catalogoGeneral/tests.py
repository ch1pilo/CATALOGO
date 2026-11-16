import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Color, ImagenProducto, Marca, Modelo, Producto, Talla, TipoMarca

MEDIA_TMP = tempfile.mkdtemp(prefix='catalogo_test_media_')


def _bytes(img, fmt, **kw):
    b = BytesIO()
    img.save(b, format=fmt, **kw)
    return b.getvalue()


def foto_pequena(nombre='p.png', color=(200, 30, 30)):
    return SimpleUploadedFile(nombre, _bytes(Image.new('RGB', (300, 200), color), 'PNG'), 'image/png')


def foto_grande_exif(nombre='grande.jpg'):
    img = Image.new('RGB', (4000, 3000), (10, 120, 200))
    exif = Image.Exif()
    exif[0x0112] = 6  # rotar 90 grados al mostrar
    return SimpleUploadedFile(nombre, _bytes(img, 'JPEG', exif=exif), 'image/jpeg')


def foto_png_alfa(nombre='alfa.png'):
    img = Image.new('RGBA', (500, 500), (0, 0, 0, 0))
    for x in range(100, 400):
        for y in range(100, 400):
            img.putpixel((x, y), (255, 0, 0, 255))
    return SimpleUploadedFile(nombre, _bytes(img, 'PNG'), 'image/png')


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class VariasFotosPorColorTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def setUp(self):
        tipo = TipoMarca.objects.create(nombre='Calzado')
        marca = Marca.objects.create(nombre='MarcaX')
        marca.tipoProducto.add(tipo)
        self.modelo = Modelo.objects.create(marca=marca, nombre='ModeloX')
        self.modelo.tipoProducto.add(tipo)
        self.rojo = Color.objects.create(nombre='Rojo', codigo_hex='#FF0000')
        self.azul = Color.objects.create(nombre='Azul', codigo_hex='#0000FF')
        self.talla = Talla.objects.create(valor='40', tipo='NUM')
        User.objects.create_user('admin', password='x')
        self.client.login(username='admin', password='x')

    def _crear(self):
        data = {
            'modelo': self.modelo.id,
            'colores': f'{self.rojo.id},{self.azul.id}',
            'tallas': str(self.talla.id),
            'precio': '50', 'descuento': '', 'stock': '0',
            f'imagen_color_{self.rojo.id}': [foto_grande_exif(), foto_png_alfa(), foto_pequena('c.png')],
            f'imagen_color_{self.azul.id}': [foto_pequena('d.png'), foto_pequena('e.png'), foto_pequena('f.png')],
        }
        r = self.client.post(reverse('guardar_producto'), data)
        self.assertEqual(r.status_code, 200, r.content[:300])
        return Producto.objects.get()

    def _editar(self, color, archivos):
        p = Producto.objects.get()
        data = {
            'modelo_id': self.modelo.id,
            'colores_ids': f'{self.rojo.id},{self.azul.id}',
            'tallas_ids': str(self.talla.id),
            'precio': '50', 'precio_descuento': '', 'stock': '0', 'activo': 'true',
            f'imagen_color_{color.id}': archivos,
        }
        return self.client.post(reverse('actualizar_producto', args=[p.id]), data)

    def test_crear_convierte_a_webp_redimensiona_y_ordena(self):
        p = self._crear()
        rojas = list(p.imagenes.filter(color=self.rojo))
        azules = list(p.imagenes.filter(color=self.azul))
        self.assertEqual(len(rojas), 3)
        self.assertEqual(len(azules), 3)
        self.assertEqual([i.orden for i in rojas], [0, 1, 2])
        for img in rojas + azules:
            self.assertTrue(img.imagen.name.endswith('.webp'), img.imagen.name)
            self.assertTrue(os.path.exists(img.imagen.path))
            with Image.open(img.imagen.path) as im:
                self.assertEqual(im.format, 'WEBP')
                self.assertLessEqual(max(im.size), 1600)
        # grande 4000x3000 con EXIF 6 -> 3000x4000 -> 1200x1600
        with Image.open(rojas[0].imagen.path) as im:
            self.assertEqual(im.size, (1200, 1600))
        # PNG con transparencia conserva RGBA
        with Image.open(rojas[1].imagen.path) as im:
            self.assertEqual(im.mode, 'RGBA')
            self.assertEqual(im.getpixel((5, 5))[3], 0)
        # pequena no se agranda
        with Image.open(rojas[2].imagen.path) as im:
            self.assertEqual(im.size, (300, 200))
        # principal = la primera de cada color
        self.assertEqual([i.es_principal for i in rojas], [True, False, False])
        self.assertEqual([i.es_principal for i in azules], [True, False, False])

    def test_editar_suma_y_limita_a_seis_con_mensaje(self):
        p = self._crear()
        self._editar(self.rojo, [foto_pequena('g.png'), foto_pequena('h.png')])
        self.assertEqual(p.imagenes.filter(color=self.rojo).count(), 5)
        self.assertEqual(p.imagenes.filter(color=self.azul).count(), 3)  # no se tocan
        ordenes = [i.orden for i in p.imagenes.filter(color=self.rojo)]
        self.assertEqual(ordenes, [0, 1, 2, 3, 4])

        r = self._editar(self.rojo, [foto_pequena('i.png'), foto_pequena('j.png'), foto_pequena('k.png')])
        self.assertEqual(p.imagenes.filter(color=self.rojo).count(), 6)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('editar_producto', args=[p.id]))
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any('máximo es 6' in m and 'omitieron 2' in m for m in msgs), msgs)

        # ya con 6: todo se omite
        self._editar(self.rojo, [foto_pequena('l.png')])
        self.assertEqual(p.imagenes.filter(color=self.rojo).count(), 6)

    def test_archivo_que_no_es_imagen_se_salta_con_aviso(self):
        p = self._crear()
        falso = SimpleUploadedFile('malo.jpg', b'esto no es una imagen', 'image/jpeg')
        r = self._editar(self.azul, [falso, foto_pequena('ok.png')])
        self.assertEqual(p.imagenes.filter(color=self.azul).count(), 4)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any('malo.jpg' in m for m in msgs), msgs)

    def test_eliminar_foto_borra_archivo_registro_y_reasigna_principal(self):
        p = self._crear()
        principal = p.imagenes.filter(color=self.rojo).first()
        siguiente = p.imagenes.filter(color=self.rojo)[1]
        ruta = principal.imagen.path
        self.assertTrue(os.path.exists(ruta))

        r = self.client.post(reverse('eliminar_imagen_producto', args=[principal.id]))
        self.assertEqual(r.status_code, 200)
        datos = r.json()
        self.assertTrue(datos['ok'])
        self.assertEqual(datos['restantes'], 2)
        self.assertEqual(datos['principal_id'], siguiente.id)
        self.assertFalse(os.path.exists(ruta))
        self.assertFalse(ImagenProducto.objects.filter(id=principal.id).exists())
        siguiente.refresh_from_db()
        self.assertTrue(siguiente.es_principal)
        self.assertEqual(p.imagenes.filter(color=self.rojo, es_principal=True).count(), 1)

    def test_eliminar_por_get_se_rechaza(self):
        p = self._crear()
        img = p.imagenes.first()
        r = self.client.get(reverse('eliminar_imagen_producto', args=[img.id]))
        self.assertEqual(r.status_code, 405)
        self.assertTrue(ImagenProducto.objects.filter(id=img.id).exists())
        self.assertTrue(os.path.exists(img.imagen.path))

    def test_eliminar_sin_login_redirige_a_login(self):
        p = self._crear()
        img = p.imagenes.first()
        self.client.logout()
        for metodo in (self.client.post, self.client.get):
            r = metodo(reverse('eliminar_imagen_producto', args=[img.id]))
            self.assertEqual(r.status_code, 302)
            self.assertIn('/login/', r.url)
        self.assertTrue(ImagenProducto.objects.filter(id=img.id).exists())

    def test_eliminar_exige_csrf(self):
        p = self._crear()
        img = p.imagenes.first()
        c = Client(enforce_csrf_checks=True)
        c.login(username='admin', password='x')
        r = c.post(reverse('eliminar_imagen_producto', args=[img.id]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(ImagenProducto.objects.filter(id=img.id).exists())

    def test_paginas_publicas_y_edicion_responden(self):
        p = self._crear()
        self.assertEqual(self.client.get(reverse('zapato_detalle', args=[p.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('catalogo_principal')).status_code, 200)
        r = self.client.get(reverse('editar_producto', args=[p.id]))
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertEqual(html.count('btn-eliminar-foto" data-url'), 6)
        self.assertIn('multiple', html)
        r = self.client.post(reverse('filtrar_productos'), data='{}', content_type='application/json')
        self.assertEqual(r.status_code, 200)
