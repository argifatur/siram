from django.forms import ModelForm
from .models import *


class ArtikelForm(ModelForm):
    class Meta:
        model = Artikel
        fields = '__all__'
