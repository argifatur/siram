from django.urls import path 
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout', views.logout_view, name='logout'),
    path('operator/dashboard', views.dashboard, name="dashboard"),

    # Slider Route
    path('operator/slider', views.sliderIndex, name="slider"),
    path('operator/slider/tambah', views.sliderTambah, name="tambah-slider"),
    path('operator/slider/hapus/<int:pk>', views.sliderHapus, name="hapus-slider"),
    path('operator/slider/edit/<int:pk>', views.sliderEdit, name="edit-slider"),

    # Artikel Route
    path('operator/artikel', views.artikelIndex, name="artikel"),
    path('operator/artikel/tambah', views.artikelTambah, name="tambah-artikel"),
    path('operator/artikel/hapus/<int:pk>', views.artikelHapus, name="hapus-artikel"),
    path('operator/artikel/edit/<int:pk>', views.artikelEdit, name="edit-artikel"),
    path('operator/artikel/detail/<int:pk>', views.artikelDetail, name="detail-artikel"),


    # Kategori Artikel Route
    path('operator/kategori-artikel', views.kategoriArtikelIndex, name="kategori-artikel"),
    path('operator/kategori-artikel/tambah', views.kategoriArtikelTambah, name="tambah-kategori-artikel"),
    path('operator/kategori-artikel/hapus/<int:pk>', views.kategoriArtikelHapus, name="hapus-kategori-artikel"),
    path('operator/kategori-artikel/edit/<int:pk>', views.kategoriArtikelEdit, name="edit-kategori-artikel"),

    # Kategori Produk Route
    path('operator/kategori-produk', views.kategoriProdukIndex, name="kategori-produk"),
    path('operator/kategori-produk/tambah', views.kategoriProdukTambah, name="tambah-kategori-produk"),
    path('operator/kategori-produk/hapus/<int:pk>', views.kategoriProdukHapus, name="hapus-kategori-produk"),
    path('operator/kategori-produk/edit/<int:pk>', views.kategoriProdukEdit, name="edit-kategori-produk"),

    # Produk Route
    path('operator/produk', views.produkIndex, name="produk"),
    path('operator/produk/tambah', views.produkTambah, name="tambah-produk"),
    path('operator/produk/hapus/<int:pk>', views.produkHapus, name="hapus-produk"),
    path('operator/produk/edit/<int:pk>', views.produkEdit, name="edit-produk"),
    path('operator/produk/detail/<int:pk>', views.produkDetail, name="detail-produk"),


    path('operator/setting', views.setting, name="setting"),
    path('operator/form', views.artikelTambah, name="form-statis"),
    path('operator/profil', views.profil, name="profil"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)