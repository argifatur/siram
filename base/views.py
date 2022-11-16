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

# Create your views here.
def home(request):
    return render(request, 'base/home.html')

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
    context = {'sliders':sliders}
    return render(request,'operator/slider/index.html', context)

@login_required(login_url='login')
def sliderHapus(request,pk):
    slider = Slider.objects.get(id=pk)
    if request.method == 'POST':
        slider.delete()
        messages.success(request, "Sukses Menghapus Slider." )
        return redirect('slider')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Slider. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/slider/hapus.html', {'obj':slider})

@login_required(login_url='login')
def sliderTambah(request):
    if request.method == 'POST':
        Slider.objects.create(
            judul=request.POST.get('judul'),
            gambar=request.POST.get('gambar'),
        )
        if request.FILES.get('gambar'):
            upload = request.FILES['gambar']
            gambar = upload.name
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        messages.success(request, "Sukses Menambah Slider." )
        return redirect('slider')
    context = {}
    return render(request,'operator/slider/tambah.html', context)

@login_required(login_url='login')
def sliderEdit(request,pk):
    slider = Slider.objects.get(id=pk)
    form = forms.SliderForm(instance=slider)
    if request.method == 'POST':
        form = forms.SliderForm(request.POST, instance=slider)
        slider.judul  = request.POST.get('judul')
        slider.isi  = request.POST.get('isi')
        slider.status  = request.POST.get('status')
        slider.kategori_id  = request.POST.get('kategori')
        slider.save()
        messages.success(request, "Sukses Mengubah Slider." )
        return redirect('slider')

    context = {'form':form,'slider':slider}
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
        artikel.kategori_id  = request.POST.get('kategori')
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


