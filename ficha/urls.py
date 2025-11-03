from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='arquivo:index_ficha', permanent=False)),
    path('', include('arquivo.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)