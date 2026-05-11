from django.urls import path
from .views import adminSeletto, display

urlpatterns = [
    path('', adminSeletto, name='adminSeletto'),
    path('display/', display, name='display'),
]