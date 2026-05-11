from django.views.generic import TemplateView
from django.shortcuts import render
class totemViews(TemplateView):
    template_name = 'totem.html'

def adminSeletto(request):
    return render(request, 'adminSeletto.html')

def display(request):
    return render(request, 'display.html')

