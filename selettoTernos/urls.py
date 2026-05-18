from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('paineis/', include('paineis.urls')),
    path('accounts/', include('accounts.urls')),
    path('filas/', include('filas.urls')),
    path('atendimentos/', include('atendimentos.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()