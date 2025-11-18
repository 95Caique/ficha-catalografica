from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe


from .models import Ficha


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'nome', 'sobrenome', 'curso', 'ano',
        'orientador', 'tipo_trabalho', 'titulo_obtido', 'pdf_link'
    )
    search_fields = ('titulo', 'nome', 'sobrenome', 'curso', 'orientador', 'coorientador')
    list_filter = ('curso', 'ano', 'tipo_trabalho', 'titulo_obtido', 'fonte', 'genero_orientador')
    ordering = ('-ano', 'nome')
    list_per_page = 25
    list_display_links = ('titulo',)

    def pdf_link(self, obj):
        try:
            url = reverse('arquivo:ficha_admin', args=[obj.pk])
            return mark_safe(f'<a href="{url}" target="_blank">Ver PDF</a>')
        except Exception:
            return '-'
    pdf_link.short_description = 'PDF'