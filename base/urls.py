from django.urls import path 
from . import views

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
    path('operator/slider/detail/<int:pk>', views.sliderDetail, name="detail-slider"),

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



    path('operator/form', views.artikelTambah, name="form-statis"),
]
