from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('paineis/', include('paineis.urls')),
    path('accounts/', include('accounts.urls')),
    path('filas/', include('filas.urls')),
    path('atendimentos/', include('atendimentos.urls')),
]