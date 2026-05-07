from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

#teste

def horario(request):
    from datetime import datetime
    
    return render(request, 'partials/horario.html', {
        'hora': datetime.now()
    })