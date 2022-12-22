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
import shutil
from django.template import loader



url_api = 'https://masak-apa-tomorisakura.vercel.app/api/'

def testing(request):
    
    setting = Setting.objects.all()
    template = loader.get_template('main.html')
    context = {
        'setting': setting,
    }
    return HttpResponse(template.render(context, request))

# Create your views here.
def home(request):
    sliders = Slider.objects.all()
    artikels = Artikel.objects.filter(status='Active').order_by('-id')[:9]
    produks = Produk.objects.all()
    reseps = Resep.objects.all().order_by('-id')[:9]
    kategori_reseps = KategoriResep.objects.all()
   

    q = request.GET.get('q')
    if request.GET.get('q'):
        # Cari dari api
        cari_resep_siram = Resep.objects.filter(title__icontains=request.GET.get('q'),is_from_api=0,status='Verified')[:9]
        resep_cari_api = Resep.objects.filter(title__icontains=request.GET.get('q'),is_from_api=1)[:9]
        context = {'produks':produks,'reseps':reseps,'sliders':sliders,'media_url':settings.MEDIA_URL,'q':q,'resep_cari_api':resep_cari_api,'cari_resep_siram':cari_resep_siram,'artikels':artikels,'kategori_reseps':kategori_reseps}
    else:
        context = {'produks':produks,'reseps':reseps,'sliders':sliders,'media_url':settings.MEDIA_URL,'q':q,'artikels':artikels,'kategori_reseps':kategori_reseps}
    return render(request, 'frontend/home.html', context)


def resepAll(request):
    # Resep
    reseps = Resep.objects.all().exclude(status='Pending').exclude(status='Gagal').order_by('-id')
    kategori_reseps = KategoriResep.objects.all()


    context = {'reseps':reseps,'media_url':settings.MEDIA_URL,'kategori_reseps':kategori_reseps}
    return render(request, 'frontend/resep-full.html', context)

def resepFavorit(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login Untuk Mengakses Fitur Favorit.")
        return redirect('login')
    resep_favorit = Bookmarks.objects.filter(user=request.user)
    
    context = {'resep_favorit':resep_favorit}
    return render(request, 'frontend/favorit.html', context)

def resepByUser(request):
    reseps = Resep.objects.filter(is_from_api=0,status='Verified')
    # Kategori Resep
    api_kategori_resep = KategoriResep.objects.all()
    
    context = {'reseps':reseps,'media_url':settings.MEDIA_URL,'api_kategori_resep':api_kategori_resep}
    return render(request, 'frontend/resep_by_user.html', context)



def artikelPage(request):
    artikels = Artikel.objects.all()
    kategori_artikels = KategoriArtikel.objects.all()
    context = {'artikels':artikels, 'media_url':settings.MEDIA_URL,'kategori_artikels':kategori_artikels}
    return render(request, 'frontend/artikel.html', context)

def artikelByKategori(request, slug):
    kategori = KategoriArtikel.objects.get(slug=slug)
    artikels = Artikel.objects.filter(kategori_artikel_id=kategori.id)
    kategori_artikels = KategoriArtikel.objects.all()
    context = {'artikels':artikels, 'media_url':settings.MEDIA_URL,'kategori_artikels':kategori_artikels,'kategori':kategori}
    return render(request, 'frontend/artikel_by_kategori.html', context)

def detailResep(request, key):
    # Resep
    resep = Resep.objects.get(key=key)
    if request.user.is_authenticated:
        bookmark = Bookmarks.objects.filter(resep=resep,user=request.user).exists()
    ingredient = resep.ingredient.replace("[","").replace("]","").replace("', '","-").replace("'","").split("-")
    step = resep.step.replace("[","").replace("]","").replace("', '","-").replace("'","").split("-")

    if request.method == 'POST':
        if request.POST.get('key_bookmarks'):
            Bookmarks.objects.create(
                resep=resep,
                user=request.user,
            )
            messages.success(request, "Yey, Kamu Berhasil Menambah Bookmark! Cek di bagian Profil ya")
        elif request.POST.get('key_unbookmarks'):
            Bookmarks.objects.get(resep=resep,user=request.user).delete()
            messages.success(request, "Bookmark Berhasil Dihapus.")
        return redirect(request.META.get('HTTP_REFERER'))
    if request.user.is_authenticated:
        context = {'resep':resep,'media_url':settings.MEDIA_URL,'ingredient':ingredient,'step':step,'key':key,'bookmark':bookmark}
    else:
        context = {'resep':resep,'media_url':settings.MEDIA_URL,'ingredient':ingredient,'step':step,'key':key}
    return render(request, 'frontend/detail_resep.html', context)

def detailKategori(request, key):
    # Resep
    kategori = KategoriResep.objects.get(key=key)
    kategoris = KategoriResep.objects.all()
    reseps = Resep.objects.filter(kategori_resep=kategori,status='Verified')


    context = {'kategoris':kategoris,'media_url':settings.MEDIA_URL,'key':key,'kategori':kategori,'reseps':reseps}
    return render(request, 'frontend/detail_kategori.html', context)

@login_required(login_url='login')
def dashboard(request):
    jumlah_resep = Resep.objects.all().count()
    jumlah_artikel = Artikel.objects.all().count()
    jumlah_produk = Produk.objects.all().count()
    jumlah_favorit = Bookmarks.objects.filter(user=request.user).count()

    context = {'jumlah_resep':jumlah_resep,'jumlah_artikel':jumlah_artikel,'jumlah_produk':jumlah_produk,'jumlah_favorit':jumlah_favorit}
    return render(request,'operator/dashboard.html', context)

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
            return redirect('home')
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

    context = {'form':form,'artikel':artikel,'kategoris':kategoris,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/artikel/edit.html', context)

@login_required(login_url='login')
def artikelDetail(request,pk):
    artikel = Artikel.objects.get(id=pk)
    kategoris = KategoriArtikel.objects.all()
    context = {'artikel':artikel,'kategoris':kategoris,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/artikel/detail.html', context)

def detailArtikel(request, slug):
    # Resep
    artikel = Artikel.objects.get(slug=slug)


    context = {'artikel':artikel,'media_url':settings.MEDIA_URL}
    return render(request, 'frontend/detail_artikel.html', context)


def resepDariUser(request):
    resep_dari_user = Resep.objects.filter(is_from_api=0)
    
    context = {'resep_dari_user':resep_dari_user,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/resep/resep_dari_user.html', context)

def resepVerified(request, pk):
    resep = Resep.objects.get(id=pk)
    resep.status = 'Verified'
    resep.save()
    messages.success(request, "Sukses Mengubah Status Resep." )
    return redirect('resep-dari-user')
    
    context = {'resep_dari_user':resep_dari_user,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/resep/resep_dari_user.html', context)

def resepPending(request, pk):
    resep = Resep.objects.get(id=pk)
    resep.status = 'Pending'
    resep.save()
    messages.success(request, "Sukses Mengubah Status Resep." )
    return redirect('resep-dari-user')
    
    context = {'resep_dari_user':resep_dari_user,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/resep/resep_dari_user.html', context)

def resepGagal(request, pk):
    resep = Resep.objects.get(id=pk)
    resep.status = 'Gagal'
    resep.save()
    messages.success(request, "Sukses Mengubah Status Resep." )
    return redirect('resep-dari-user')
    
    context = {'resep_dari_user':resep_dari_user,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/resep/resep_dari_user.html', context)




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
                url=request.POST.get('url'),
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
                url=request.POST.get('url'),
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
        produk.url  = request.POST.get('url')
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


# USER
# Resep Views
@login_required(login_url='login')
def resepIndex(request):
    reseps = Resep.objects.filter(author=request.user)
    context = {'reseps':reseps,'media_url':settings.MEDIA_URL}
    return render(request,'operator/resep/index.html', context)

@login_required(login_url='login')
def resepIndexFull(request):
    reseps = Resep.objects.all()
    context = {'reseps':reseps,'media_url':settings.MEDIA_URL}
    return render(request,'operator/resep/full.html', context)

@login_required(login_url='login')
def resepHapus(request,pk):
    resep = Resep.objects.get(id=pk)
    if request.method == 'POST':
        if resep.thumb:
            if os.path.isfile(resep.thumb.path):
                os.remove(resep.thumb.path)
        resep.delete()
        messages.success(request, "Sukses Menghapus Resep." )
        return redirect('resep')
    else:
        messages.error(request, 'Terdapat Error Saat Hapus Resep. Pastikan Data Yang Ingin Dihapus Tidak Terkait Dengan Data Lain!', extra_tags="danger")
    return render(request, 'operator/resep/hapus.html', {'obj':resep})

@login_required(login_url='login')
def resepTambah(request):
    kategoris = KategoriResep.objects.all()
    if request.method == 'POST':
        key_slug = request.POST.get('title').replace(" ", "-").lower()
        if request.FILES.get('gambar'):
            upload = request.FILES['gambar']
            gambar = upload.name
            Resep.objects.create(
                title=request.POST.get('title'),
                key=key_slug,
                desc=request.POST.get('desc'),
                kategori_resep_id=request.POST.get('kategori_resep'),
                thumb=gambar,
                author=request.user,
                url_youtube=request.POST.get('url_youtube'),
                difficulty=request.POST.get('difficulty'),
                ingredient=request.POST.get('ingredient'),
                step=request.POST.get('step'),
                serving=request.POST.get('serving'),
                times=request.POST.get('times'),
                is_from_api=0,
                status='Pending'
            )
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        else:
            Resep.objects.create(
                title=request.POST.get('title'),
                key=key_slugs,
                desc=request.POST.get('desc'),
                kategori_resep_id=request.POST.get('kategori_resep'),
                thumb=gambar,
                author=request.user,
                url_youtube=request.POST.get('url_youtube'),
                difficulty=request.POST.get('difficulty'),
                ingredient=request.POST.get('ingredient'),
                step=request.POST.get('step'),
                serving=request.POST.get('serving'),
                times=request.POST.get('times'),
                is_from_api=0,
                status='Pending'
            )
        messages.success(request, "Sukses Menambah Resep." )
        return redirect('resep')
    context = {'kategoris':kategoris}
    return render(request,'operator/resep/tambah.html', context)

@login_required(login_url='login')
def resepEdit(request,pk):
    resep = Resep.objects.get(id=pk)
    kategoris = KategoriResep.objects.all()
    if request.method == 'POST':
        key_slug = request.POST.get('title').replace(" ", "-").lower()
        resep.title  = request.POST.get('title')
        key          = key_slug
        resep.desc  = request.POST.get('desc')
        resep.url_youtube  = request.POST.get('url_youtube')
        resep.kategori_resep_id  = request.POST.get('kategori_resep')
        resep.difficulty  = request.POST.get('difficulty')
        resep.ingredient  = request.POST.get('ingredient')
        resep.step  = request.POST.get('step')
        resep.serving  = request.POST.get('serving')
        resep.times  = request.POST.get('times')
        resep.save()
        if request.FILES.get('gambar'):
            if resep.thumb:
                if os.path.isfile(resep.thumb.path):
                    os.remove(resep.thumb.path)
            upload = request.FILES['gambar']
            resep.thumb = upload.name
            resep.save()
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
        messages.success(request, "Sukses Mengubah Resep." )
        return redirect('resep')

    context = {'resep':resep,'kategoris':kategoris,'media_url':settings.MEDIA_URL}
    return render(request, 'operator/resep/edit.html', context)

@login_required(login_url='login')
def resepDetail(request,pk):
    artikel = Resep.objects.get(id=pk)
    kategoris = Resep.objects.all()
    context = {'artikel':artikel,'kategoris':kategoris}
    return render(request, 'operator/resep/detail.html', context)

def sinkron(request):
    # Sinkron Kategori Resep
    url_kategori = f'{url_api}/category/recipes/'
    kategori = requests.get(url_kategori)
    data = kategori.json()
    kategori_resep = data['results']
    for kategori in kategori_resep:
        key_kategori = kategori['key']
        if KategoriResep.objects.filter(key=kategori['key']).exists() == False:
            KategoriResep.objects.create(
                category=kategori['category'],
                key = kategori['key'],
                is_from_api = 1
            )
        else:
            KategoriResep.objects.filter(key=kategori['key']).update(category=kategori['category'],key=kategori['key'])

        get_kategori = KategoriResep.objects.get(key=key_kategori)
        url_resep_by_kategori = f'{url_api}/category/recipes/{key_kategori}'
        reseps = requests.get(url_resep_by_kategori)
        data_resep = reseps.json()
        api_resep = data_resep['results']

        for resep in api_resep:
            image_url = resep['thumb']
            filename = r"media/"+image_url.split("/")[-1]
            nama_file_diubah = image_url.split("/")[-1]
            r = requests.get(image_url, stream = True)
            if r.status_code == 200:
                r.raw.decode_content = True            
                with open(filename,'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                print('Image sucessfully Downloaded: ',filename)
            else:
                print('Image Couldn\'t be retreived')

            key_resep = resep['key']
            # GET DETAIL DULU
            url_detail_resep = f'{url_api}/recipe/{key_resep}'
            detail_json_reseps = requests.get(url_detail_resep)
            json_detail_resep = detail_json_reseps.json()
            data_detail_resep = json_detail_resep['results']
            print('insert resep dengan kategori')

            ingredient_join = ', '.join(data_detail_resep['ingredient'])
            step_join = ', '.join(data_detail_resep['step'])

            if Resep.objects.filter(key=resep['key']).exists() == False:
                Resep.objects.create(
                    title=resep['title'],
                    key=resep['key'],
                    thumb=nama_file_diubah,
                    serving=resep['serving'],
                    times=resep['times'],
                    difficulty=resep['difficulty'],
                    is_from_api=1,

                    author_datePublished=data_detail_resep['author']['datePublished'],
                    author_user=data_detail_resep['author']['user'],
                    desc = data_detail_resep['desc'],
                    ingredient = ingredient_join,
                    step = step_join,

                    kategori_resep_id=get_kategori.id,
                    status = 'Verified'
                )
            else:
                Resep.objects.filter(key=resep['key']).update(
                    title=resep['title'],
                    key=resep['key'],
                    thumb=nama_file_diubah,
                    serving=resep['serving'],
                    times=resep['times'],
                    difficulty=resep['difficulty'],
                    is_from_api=1,

                    author_datePublished=data_detail_resep['author']['datePublished'],
                    author_user=data_detail_resep['author']['user'],
                    desc = data_detail_resep['desc'],
                    ingredient = ingredient_join,
                    step = step_join,

                    kategori_resep_id=get_kategori.id,
                    status = 'Verified'
                )

    # Sinkron Resep Aja
    url_resep = f'{url_api}/recipes'
    reseps = requests.get(url_resep)
    data_resep = reseps.json()
    api_resep = data_resep['results']
    for resep in api_resep:
        image_url = resep['thumb']
        filename = r"media/"+image_url.split("/")[-1]
        nama_file_diubah = image_url.split("/")[-1]
        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True            
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print('Image sucessfully Downloaded: ',filename)
        else:
            print('Image Couldn\'t be retreived')

        key_resep = resep['key']
        # GET DETAIL DULU
        url_detail_resep = f'{url_api}/recipe/{key_resep}'
        detail_reseps = requests.get(url_detail_resep)
        json_resep = detail_reseps.json()
        data_detail_resep = json_resep['results']

        ingredient_join = ', '.join(data_detail_resep['ingredient'])
        step_join = ', '.join(data_detail_resep['step'])

        if Resep.objects.filter(key=resep['key']).exists() == False:
            Resep.objects.create(
                title=resep['title'],
                key=resep['key'],
                thumb=nama_file_diubah,
                serving=resep['serving'],
                times=resep['times'],
                difficulty=resep['difficulty'],
                is_from_api=1,

                author_datePublished=data_detail_resep['author']['datePublished'],
                author_user=data_detail_resep['author']['user'],
                desc = data_detail_resep['desc'],
                ingredient = ingredient_join,
                step = step_join,
                status = 'Verified'
            )
        else:
            Resep.objects.filter(key=resep['key']).update(
                title=resep['title'],
                key=resep['key'],
                thumb=nama_file_diubah,
                serving=resep['serving'],
                times=resep['times'],
                difficulty=resep['difficulty'],
                is_from_api=1,

                author_datePublished=data_detail_resep['author']['datePublished'],
                author_user=data_detail_resep['author']['user'],
                desc = data_detail_resep['desc'],
                ingredient = ingredient_join,
                step = step_join,
                status = 'Verified'
            )

    messages.success(request, "Sukses Sinkronisasi, Silakan Cek Data." )
    return redirect(request.META.get('HTTP_REFERER'))
    context = {}
    return render(request, 'operaor/resep/index.html', context)


def tentang(request):
    context = {}
    return render(request, 'frontend/tentang.html', context)



