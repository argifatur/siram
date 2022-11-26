from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "password1", "password2","first_name","last_name")

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        # user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ArtikelForm(ModelForm):
    class Meta:
        model = Artikel
        fields = '__all__'
