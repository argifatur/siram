import http
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect,reverse
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from .models import *
from django.http import HttpResponse, JsonResponse
from . import forms
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import requests


url_api = 'https://masak-apa-tomorisakura.vercel.app/api/'
# Create your views here.
def home(request):
    sliders = Slider.objects.all()
    artikels = Artikel.objects.all().order_by('-id')[:9]
    # Kategori Resep
    url_kategori_resep = f'{url_api}/category/recipes/'
    kategori_reseps = requests.get(url_kategori_resep)
    data_kategori_resep = kategori_reseps.json()
    api_kategori_resep = data_kategori_resep['results']

    for kategori in api_kategori_resep:
        if KategoriResep.objects.filter(key=kategori['key']).exists() == False:
            KategoriResep.objects.create(
                category=kategori['category'],
                key = kategori['key'],
            )
        else:
            KategoriResep.objects.filter(key=kategori['key']).update(category=kategori['category'],key=kategori['key'])

    # Resep
    url_new_resep = f'{url_api}/recipes-length/?limit=9'
    kategori_reseps = requests.get(url_new_resep)
    data_resep = kategori_reseps.json()
    api_resep = data_resep['results']

    q = request.GET.get('q')
    if request.GET.get('q'):
        # Cari dari api
        url_cari = f'{url_api}/search/?q={q}'
        cari = requests.get(url_cari)
        data = cari.json()
        resep_cari_api = data['results']
        cari_resep_siram = Resep.objects.filter(title__icontains=request.GET.get('q'),is_from_api=0)[:9]
        context = {'api_kategori_resep':api_kategori_resep,'api_resep':api_resep,'sliders':sliders,'media_url':settings.MEDIA_URL,'q':q,'resep_cari_api':resep_cari_api,'cari_resep_siram':cari_resep_siram,'artikels':artikels}
    else:
        context = {'api_kategori_resep':api_kategori_resep,'api_resep':api_resep,'sliders':sliders,'media_url':settings.MEDIA_URL,'q':q,'artikels':artikels}
    return render(request, 'frontend/home.html', context)


def resepByKategori(request, key):
    nama_kategori = key.replace('-',' ')
    # Resep
    url_resep_by_kategori = f'{url_api}/category/recipes/{key}'
    reseps = requests.get(url_resep_by_kategori)
    data_resep = reseps.json()
    api_resep = data_resep['results']

    context = {'api_resep':api_resep,'media_url':settings.MEDIA_URL,'nama_kategori':nama_kategori}
    return render(request, 'frontend/resep_by_kategori.html', context)

def resepAll(request):
    # Resep
    url_resep = f'{url_api}/recipes'
    reseps = requests.get(url_resep)
    data_resep = reseps.json()
    api_resep = data_resep['results']

    # Kategori Resep
    url_kategori_resep = f'{url_api}/category/recipes/'
    kategori_reseps = requests.get(url_kategori_resep)
    data_kategori_resep = kategori_reseps.json()
    api_kategori_resep = data_kategori_resep['results']


    context = {'api_resep':api_resep,'media_url':settings.MEDIA_URL,'api_kategori_resep':api_kategori_resep}
    return render(request, 'frontend/resep-full.html', context)

def resepFavorit(request):
    # Resep
    resep_favorit = Bookmarks.objects.filter(user=request.user)


    context = {'resep_favorit':resep_favorit}
    return render(request, 'frontend/favorit.html', context)

def detailResep(request, key):
    # Resep
    

    if request.user.is_authenticated:
        bookmark = Bookmarks.objects.filter(key_resep=key,user=request.user).exists()
    # Resep
    if Resep.objects.filter(key=key).exists() == False:
        from_api = 1
        url_detail_resep = f'{url_api}/recipe/{key}'
        reseps = requests.get(url_detail_resep)
        data_resep = reseps.json()
        resep = data_resep['results']
        ingredient = resep['ingredient']
        step = resep['step']
        url_youtube = ""
    else:
        from_api = 0
        resep = Resep.objects.get(key=key)
        ingredient = resep.ingredient.split(", ")
        step = resep.step.split(", ")

    if request.method == 'POST':
        if request.POST.get('key_bookmarks'):
            url_resep_detail = f'{url_api}/recipe/{key}'
            resepnya = requests.get(url_resep_detail)
            datanya = resepnya.json()
            result = datanya['results']
            Bookmarks.objects.create(
                key_resep = key,
                title_resep=result['title'],
                times_resep=result['times'],
                difficulty_resep=result['difficulty'],
                thumb_resep=result['thumb'],
                serving_resep=result['servings'],
                user=request.user,
            )
            messages.success(request, "Yey, Kamu Berhasil Menambah Bookmark! Cek di bagian Profil ya")
        elif request.POST.get('key_unbookmarks'):
            Bookmarks.objects.get(key_resep=key,user=request.user).delete()
            messages.success(request, "Bookmark Berhasil Dihapus.")
        return redirect(request.META.get('HTTP_REFERER'))
    if request.user.is_authenticated:
        context = {'resep':resep,'media_url':settings.MEDIA_URL,'ingredient':ingredient,'step':step,'from_api':from_api,'key':key,'bookmark':bookmark}
    else:
        context = {'resep':resep,'media_url':settings.MEDIA_URL,'ingredient':ingredient,'step':step,'from_api':from_api,'key':key}
    return render(request, 'frontend/detail_resep.html', context)

def detailKategori(request, key):
    # Resep
    url_detail_kategori = f'{url_api}/category/recipes/{key}'
    kategori_resep = requests.get(url_detail_kategori)
    data_kategori = kategori_resep.json()
    api_kategori = data_kategori['results']
    kategori = KategoriResep.objects.get(key=key)

    # Kategori Resep
    url_kategori_resep = f'{url_api}/category/recipes/'
    kategori_reseps = requests.get(url_kategori_resep)
    data_kategori_resep = kategori_reseps.json()
    api_kategori_resep = data_kategori_resep['results']


    context = {'api_kategori':api_kategori,'media_url':settings.MEDIA_URL,'key':key,'kategori':kategori,'api_kategori_resep':api_kategori_resep}
    return render(request, 'frontend/detail_kategori.html', context)

@login_required(login_url='login')
def dashboard(request):
    return render(request,'operator/dashboard.html')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    username = request.POST.get('username')
    password =request.POST.get('password')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            user_profile = User.objects.get(username=username)
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username / Password Salah, Silakan Coba Lagi',extra_tags='danger')
            return redirect('login')
    return render(request, 'frontend/login.html')

def registerPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == 1:
            return redirect('dashboard')
        else:
            messages.info(request, 'Anda Telah Login.')
            return redirect('home')
    
    form = forms.UserForm()

    if request.method == 'POST':
        form = forms.UserForm(request.POST)
        if request.POST.get('password1') == request.POST.get('password2'):
            if form.is_valid():
                user_new = form.save()
                messages.success(request, "Terimakasih Telah Registrasi, Sekarang Anda Telah Login.")
                new_user = authenticate(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        )
                login(request, new_user)
                return redirect('home')
            else:
                messages.error(request, "Data Tidak Valid. Pastikan Data Benar. Password Minimal 8 Karakter Dengan Kombinasi Huruf, Angka & Simbol.", extra_tags="danger" )
                return redirect('register')
        else:
            messages.error(request, "Password & Konfirmasi Password Harus Sama.", extra_tags="danger" )
            return redirect('register')
       

    context = {'form':form}
    return render(request, 'frontend/register.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

# Slider Views
@login_required(login_url='login')
def sliderIndex(request):
    sliders = Slider.objects.all()
    context = {'sliders':sliders,'media_url':settings.MEDIA_URL}
    return render(request,'operator/slider/index.html', context)

@login_required(login_url='login')
def sliderHapus(request,pk):
    slider = Slider.objects.get(id=pk)
    if request.method == 'POST':
        if slider.gambar:
            if os.path.isfile(slider.gambar.path):
                os.remove(slider.gambar.path)
        slider.delete()
        messages.success(request, "Sukses Menghapus Slider." )
        return redirect('slider')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Slider. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/slider/hapus.html', {'obj':slider})

@login_required(login_url='login')
def sliderTambah(request):
    if request.method == 'POST':
        if request.FILES.get('gambar'):
            upload = request.FILES['gambar']
            Slider.objects.create(
                judul=request.POST.get('judul'),
                gambar=upload.name,
            )
            gambar = upload.name
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        else:
            messages.error(request, "Gambar Harus Diisi." )
            return redirect('slider')

        messages.success(request, "Sukses Menambah Slider." )
        return redirect('slider')
    context = {}
    return render(request,'operator/slider/tambah.html', context)

@login_required(login_url='login')
def sliderEdit(request,pk):
    slider = Slider.objects.get(id=pk)
    if request.method == 'POST':
        slider.judul  = request.POST.get('judul')
        slider.save()
        if request.FILES.get('gambar'):
            if slider.gambar:
                if os.path.isfile(slider.gambar.path):
                    os.remove(slider.gambar.path)
            upload = request.FILES['gambar']
            slider.gambar = upload.name
            slider.save()
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
            
        messages.success(request, "Sukses Mengubah Slider." )
        return redirect('slider')

    context = {'slider':slider,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/slider/edit.html', context)


# Artikel Views
@login_required(login_url='login')
def artikelIndex(request):
    artikels = Artikel.objects.all()
    context = {'artikels':artikels,'media_url':settings.MEDIA_URL}
    return render(request,'operator/artikel/index.html', context)

@login_required(login_url='login')
def artikelHapus(request,pk):
    artikel = Artikel.objects.get(id=pk)
    if request.method == 'POST':
        artikel.delete()
        messages.success(request, "Sukses Menghapus Artikel." )
        return redirect('artikel')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Artikel. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/artikel/hapus.html', {'obj':artikel})

@login_required(login_url='login')
def artikelTambah(request):
    kategoris = KategoriArtikel.objects.all()
    form = forms.ArtikelForm()
    if request.method == 'POST':
        kat = KategoriArtikel.objects.get(id=request.POST.get('kategori'))
        if request.FILES.get('gambar'):
            upload = request.FILES['gambar']
            gambar = upload.name
            Artikel.objects.create(
                judul=request.POST.get('judul'),
                isi=request.POST.get('isi'),
                kategori_artikel_id=request.POST.get('kategori'),
                status=request.POST.get('status'),
                author=request.user,
                thumbnail=gambar,
            )
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        else:
            Artikel.objects.create(
                judul=request.POST.get('judul'),
                isi=request.POST.get('isi'),
                kategori_artikel_id=request.POST.get('kategori'),
                status=request.POST.get('status'),
                author=request.user,
            )
        messages.success(request, "Sukses Menambah Artikel." )
        return redirect('artikel')
    context = {'kategoris':kategoris}
    return render(request,'operator/artikel/tambah.html', context)

@login_required(login_url='login')
def artikelEdit(request,pk):
    artikel = Artikel.objects.get(id=pk)
    kategoris = KategoriArtikel.objects.all()
    form = forms.ArtikelForm(instance=artikel)
    if request.method == 'POST':
        form = forms.ArtikelForm(request.POST, instance=artikel)
        artikel.judul  = request.POST.get('judul')
        artikel.isi  = request.POST.get('isi')
        artikel.status  = request.POST.get('status')
        artikel.kategori_artikel_id  = request.POST.get('kategori')
        artikel.save()
        if request.FILES.get('gambar'):
            if artikel.thumbnail:
                if os.path.isfile(artikel.thumbnail.path):
                    os.remove(artikel.thumbnail.path)
            upload = request.FILES['gambar']
            artikel.thumbnail = upload.name
            artikel.save()
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        messages.success(request, "Sukses Mengubah Artikel." )
        return redirect('artikel')

    context = {'form':form,'artikel':artikel,'kategoris':kategoris}
    return render(request, 'operator/artikel/edit.html', context)

@login_required(login_url='login')
def artikelDetail(request,pk):
    artikel = Artikel.objects.get(id=pk)
    kategoris = KategoriArtikel.objects.all()
    context = {'artikel':artikel,'kategoris':kategoris}
    return render(request, 'operator/artikel/detail.html', context)

def detailArtikel(request, slug):
    # Resep
    artikel = Artikel.objects.get(slug=slug)


    context = {'artikel':artikel,'media_url':settings.MEDIA_URL}
    return render(request, 'frontend/detail_artikel.html', context)


# Kategori Artikel Views
@login_required(login_url='login')
def kategoriArtikelIndex(request):
    kategoris = KategoriArtikel.objects.all()
    context = {'kategoris':kategoris}
    return render(request,'operator/kategori_artikel/index.html', context)

@login_required(login_url='login')
def kategoriArtikelHapus(request,pk):
    kategoriArtikel = KategoriArtikel.objects.get(id=pk)
    if request.method == 'POST':
        kategoriArtikel.delete()
        messages.success(request, "Sukses Menghapus Artikel." )
        return redirect('kategori-artikel')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Kategori Artikel. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/kategori_artikel/hapus.html', {'obj':artikel})

@login_required(login_url='login')
def kategoriArtikelTambah(request):
    # form = forms.ArtikelForm()
    if request.method == 'POST':
        KategoriArtikel.objects.create(
            nama_kategori=request.POST.get('nama_kategori')
        )
        messages.success(request, "Sukses Menambah Kategori Artikel." )
        return redirect('kategori-artikel')
    context = {}
    return render(request,'operator/kategori_artikel/tambah.html', context)

@login_required(login_url='login')
def kategoriArtikelEdit(request,pk):
    kategoriArtikel = KategoriArtikel.objects.get(id=pk)
    if request.method == 'POST':
        kategoriArtikel.nama_kategori  = request.POST.get('nama_kategori')
        kategoriArtikel.save()
        messages.success(request, "Sukses Mengubah Kategori Artikel." )
        return redirect('kategori-artikel')

    context = {'kategoriArtikel':kategoriArtikel}
    return render(request, 'operator/kategori_artikel/edit.html', context)


# Kategori Produk Views
@login_required(login_url='login')
def kategoriProdukIndex(request):
    kategoris = KategoriProduk.objects.all()
    context = {'kategoris':kategoris}
    return render(request,'operator/kategori_produk/index.html', context)

@login_required(login_url='login')
def kategoriProdukHapus(request,pk):
    kategoriArtikel = KategoriProduk.objects.get(id=pk)
    if request.method == 'POST':
        kategoriArtikel.delete()
        messages.success(request, "Sukses Menghapus Kategori Produk." )
        return redirect('kategori-produk')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Kategori Produk. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/kategori_produk/hapus.html', {'obj':artikel})

@login_required(login_url='login')
def kategoriProdukTambah(request):
    # form = forms.ArtikelForm()
    if request.method == 'POST':
        KategoriProduk.objects.create(
            nama_kategori=request.POST.get('nama_kategori')
        )
        messages.success(request, "Sukses Menambah Kategori Produk." )
        return redirect('kategori-produk')
    context = {}
    return render(request,'operator/kategori_produk/tambah.html', context)

@login_required(login_url='login')
def kategoriProdukEdit(request,pk):
    kategoriProduk = KategoriProduk.objects.get(id=pk)
    if request.method == 'POST':
        kategoriProduk.nama_kategori  = request.POST.get('nama_kategori')
        kategoriProduk.save()
        messages.success(request, "Sukses Mengubah Kategori Produk." )
        return redirect('kategori-produk')

    context = {'kategoriProduk':kategoriProduk}
    return render(request, 'operator/kategori_produk/edit.html', context)


# Produk Views
@login_required(login_url='login')
def produkIndex(request):
    produks = Produk.objects.all()
    context = {'produks':produks}
    return render(request,'operator/produk/index.html', context)

@login_required(login_url='login')
def produkHapus(request,pk):
    produk = Produk.objects.get(id=pk)
    if request.method == 'POST':
        if produk.gambar:
            if os.path.isfile(produk.gambar.path):
                os.remove(produk.gambar.path)
        produk.delete()
        messages.success(request, "Sukses Menghapus Produk." )
        return redirect('produk')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Produk. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/produk/hapus.html', {'obj':produk})

@login_required(login_url='login')
def produkTambah(request):
    kategoris = KategoriProduk.objects.all()
    if request.method == 'POST':
        if request.FILES.get('gambar'):
            upload = request.FILES['gambar']
            gambar = upload.name
            Produk.objects.create(
                nama_produk=request.POST.get('nama_produk'),
                deskripsi=request.POST.get('deskripsi'),
                kategori_produk_id=request.POST.get('kategori'),
                harga=request.POST.get('harga'),
                gambar=gambar,
                author=request.user,
            )
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        else:
            Produk.objects.create(
                nama_produk=request.POST.get('nama_produk'),
                deskripsi=request.POST.get('deskripsi'),
                kategori_produk_id=request.POST.get('kategori'),
                harga=request.POST.get('harga'),
                author=request.user,
            )
        messages.success(request, "Sukses Menambah Produk." )
        return redirect('produk')
    context = {'kategoris':kategoris}
    return render(request,'operator/produk/tambah.html', context)

@login_required(login_url='login')
def produkEdit(request,pk):
    produk = Produk.objects.get(id=pk)
    kategoris = KategoriProduk.objects.all()
    if request.method == 'POST':
        produk.nama_produk  = request.POST.get('nama_produk')
        produk.deskripsi  = request.POST.get('deskripsi')
        produk.harga  = request.POST.get('harga')
        produk.kategori_produk_id  = request.POST.get('kategori')
        produk.save()
        if request.FILES.get('gambar'):
            if produk.gambar:
                if os.path.isfile(produk.gambar.path):
                    os.remove(produk.gambar.path)
            upload = request.FILES['gambar']
            produk.gambar = upload.name
            produk.save()
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        messages.success(request, "Sukses Mengubah Produk." )
        return redirect('produk')

    context = {'produk':produk,'kategoris':kategoris,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/produk/edit.html', context)

@login_required(login_url='login')
def produkDetail(request,pk):
    artikel = Produk.objects.get(id=pk)
    kategoris = KategoriProduk.objects.all()
    context = {'artikel':artikel,'kategoris':kategoris}
    return render(request, 'operator/produk/detail.html', context)


# EDIT PROFIl
@login_required(login_url='home')
def profil(request):
    user = request.user
    form = forms.UserForm(instance=user)

    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=user)
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        if request.POST.get('password1'):
            if request.POST.get('password1') == request.POST.get('password2'):
                user.set_password(request.POST.get('password1'))
            else:
                 messages.error(request, "Password & Konfirmasi Password Harus Sama.", extra_tags="danger" )
                 return redirect('profil')
        user.save()
        messages.success(request, "Sukses Mengubah Profil." )
        return redirect('profil')

    context = {'user':user,'form':form}
    return render(request, 'operator/profil.html', context)



# SETTINGS
@login_required(login_url='login')
def setting(request):
    setting = Setting.objects.all()
    context = {'setting':setting}
    return render(request,'operator/setting/index.html', context)