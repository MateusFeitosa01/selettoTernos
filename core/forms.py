from django import forms

class ClienteForm(forms.Form):
    nome = forms.CharField(
        max_length=100,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg rounded-4',
            'placeholder': 'Digite seu nome completo'
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg rounded-4',
            'placeholder': 'Digite seu email'
        })
    )

    whatsapp = forms.CharField(
        max_length=20,
        label='WhatsApp',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg rounded-4',
            'placeholder': '(83) 99999-9999'
        })
    )