from django.shortcuts import render, redirect
from django.contrib.auth import logout

def logout_view(request):
    """View customizada de logout que desautentica e redireciona para home"""
    logout(request)
    return redirect('home')
