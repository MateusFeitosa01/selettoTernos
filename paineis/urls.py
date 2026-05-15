from django.urls import path
from .views import adminSeletto, display

urlpatterns = [
    path('', adminSeletto, name='paineis_adminSeletto'),
    path('display/', display, name='paineis_display'),
]