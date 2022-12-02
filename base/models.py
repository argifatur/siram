from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import datetime

# Create your models here.

class Slider(models.Model):
    judul = models.CharField(max_length=255)
    gambar = models.ImageField(upload_to='images_slider/',null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # class Meta:
    #     ordering = ['-updated', '-created']

    def __str__(self):
        return self.judul

class KategoriResep(models.Model):
    judul = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # class Meta:
    #     ordering = ['-updated', '-created']

    def __str__(self):
        return self.judul


class KategoriArtikel(models.Model):
    nama_kategori = models.CharField(max_length=200)
    created       = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.nama_kategori

class Artikel(models.Model):
    judul 		        = models.CharField(max_length=255)
    isi 		        = models.TextField()
    kategori_artikel    = models.ForeignKey(KategoriArtikel, on_delete=models.SET_NULL, null=True)
    author              = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status 	            = models.CharField(max_length=255) # Active Inactive
    published 	        = models.DateTimeField(auto_now_add=True)
    updated 	        = models.DateTimeField(auto_now=True)
    slug 		        = models.SlugField(blank=True, editable=False)

    def save(self, **kwargs):
        self.slug = slugify(self.judul)
        super().save()

    def get_absolute_url(self):
        url_slug = {'slug':self.slug}
        return reverse('blog', kwargs = url_slug)
        
    def __str__(self):
        return self.judul


class KategoriProduk(models.Model):
    nama_kategori = models.CharField(max_length=200)
    created       = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.nama_kategori

class Produk(models.Model):
    nama_produk         = models.CharField(max_length=255)
    deskripsi           = models.TextField()
    kategori_produk     = models.ForeignKey(KategoriProduk, on_delete=models.SET_NULL, null=True)
    author              = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    harga               = models.IntegerField(default=0) # Active Inactive
    gambar              = models.ImageField(upload_to='images_produk/',null=True)
    created             = models.DateTimeField(auto_now_add=True)
    updated             = models.DateTimeField(auto_now=True)
    slug                = models.SlugField(blank=True, editable=False)

    def save(self, **kwargs):
        self.slug = slugify(self.nama_produk)
        super().save()

    def get_absolute_url(self):
        url_slug = {'slug':self.slug}
        return reverse('blog', kwargs = url_slug)
        
    def __str__(self):
        return self.nama_produk


class Setting(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    created       = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.key