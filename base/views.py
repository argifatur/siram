import http
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect,reverse
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from .models import *
from django.http import HttpResponse
from . import forms
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

# Create your views here.
def home(request):
    return render(request, 'frontend/home.html')

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
            messages.info(request, 'Username OR password is incorrect')
            return redirect('login')
    return render(request, 'base/login_register.html')

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
    context = {'artikels':artikels}
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