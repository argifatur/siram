from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.KategoriArtikel)
admin.site.register(models.KategoriProduk)
admin.site.register(models.Artikel)
admin.site.register(models.Produk)