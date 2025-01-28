from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Ficha


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nome', 'sobrenome', 'curso', 'ano', 'orientador', 'tipo_trabalho', 'titulo_obtido')
    search_fields = ('titulo', 'nome', 'sobrenome', 'curso', 'orientador', 'coorientador')
    list_filter = ('curso', 'ano', 'tipo_trabalho', 'titulo_obtido', 'fonte', 'genero_orientador')
    ordering = ('-ano', 'nome')
    list_per_page = 25

    # Especificando qual campo será usado como link na tabela do admin
    list_display_links = ('titulo',)