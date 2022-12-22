from django.urls import path 
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout', views.logout_view, name='logout'),
    path('operator/dashboard', views.dashboard, name="dashboard"),
    path('operator/sinkron', views.sinkron, name="sinkron"),

    # ADMIN ROUTE 

    # Slider Route
    path('operator/slider', views.sliderIndex, name="slider"),
    path('operator/slider/tambah', views.sliderTambah, name="tambah-slider"),
    path('operator/slider/hapus/<int:pk>', views.sliderHapus, name="hapus-slider"),
    path('operator/slider/edit/<int:pk>', views.sliderEdit, name="edit-slider"),

    path('operator/resep/', views.resepIndexFull, name="resep-index-full"),
    path('operator/resep-dari-user/', views.resepDariUser, name="resep-dari-user"),
    path('operator/resep-verified/<int:pk>', views.resepVerified, name="url-verified"),
    path('operator/resep-pending/<int:pk>', views.resepPending, name="url-pending"),
    path('operator/resep-gagal/<int:pk>', views.resepGagal, name="url-gagal"),

    # User Add Resep Route
    path('siram/resep', views.resepIndex, name="resep"),
    path('siram/resep/tambah', views.resepTambah, name="tambah-resep"),
    path('siram/resep/hapus/<int:pk>', views.resepHapus, name="hapus-resep"),
    path('siram/resep/edit/<int:pk>', views.resepEdit, name="edit-resep"),
    path('siram/resep/detail/<int:pk>', views.resepDetail, name="detail-resep"),

    # Artikel Route
    path('operator/artikel', views.artikelIndex, name="artikel"),
    path('operator/artikel/tambah', views.artikelTambah, name="tambah-artikel"),
    path('operator/artikel/hapus/<int:pk>', views.artikelHapus, name="hapus-artikel"),
    path('operator/artikel/edit/<int:pk>', views.artikelEdit, name="edit-artikel"),
    path('operator/artikel/detail/<int:pk>', views.artikelDetail, name="detail-artikel-op"),


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


    # USER ROUTE
    path('tentang/', views.tentang, name="tentang"),
    path('resep-masakan/', views.resepAll, name="resep-all"),
    path('resep-pilihan/', views.resepByUser, name="resep-by-user"),
    path('artikel/', views.artikelPage, name="artikel-page"),
    path('artikel/<str:slug>', views.artikelByKategori, name="artikel-by-kategori"),
    path('resep-masakan/detail-resep/<str:key>', views.detailResep, name="detail-resep"),
    path('resep-favorit/', views.resepFavorit, name="resep-favorit"),
    path('resep-masakan/kategori/<str:key>', views.detailKategori, name="detail-kategori"),
    path('artikel/detail-artikel/<str:slug>', views.detailArtikel, name="detail-artikel"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)