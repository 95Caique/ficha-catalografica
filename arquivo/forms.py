from django import forms
from .models import Ficha  # supondo que você tenha um modelo chamado Ficha

class FichaForm(forms.ModelForm):
    class Meta:
        model = Ficha
        fields = '__all__'