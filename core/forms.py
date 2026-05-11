from django import forms
from django.core.validators import RegexValidator


class ClienteForm(forms.Form):
    nome = forms.CharField(
        max_length=100,
        min_length=2,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg rounded-4',
            'placeholder': 'Digite seu nome completo'
        }),
        error_messages={
            'required': 'O nome é obrigatório.',
            'min_length': 'O nome deve ter pelo menos 2 caracteres.',
            'max_length': 'O nome deve ter no máximo 100 caracteres.'
        }
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg rounded-4',
            'placeholder': 'Digite seu email'
        }),
        error_messages={
            'required': 'O email é obrigatório.',
            'invalid': 'Digite um email válido.'
        }
    )

    whatsapp = forms.CharField(
        max_length=20,
        min_length=10,
        label='WhatsApp',
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
                message='Formato inválido. Use (XX) XXXXX-XXXX'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg rounded-4',
            'placeholder': '(83) 99999-9999'
        }),
        error_messages={
            'required': 'O WhatsApp é obrigatório.',
            'min_length': 'O WhatsApp deve ter pelo menos 10 caracteres.',
            'max_length': 'O WhatsApp deve ter no máximo 20 caracteres.'
        }
    )

    def clean_nome(self):
        """Validação customizada para o nome."""
        nome = self.cleaned_data['nome'].strip()
        if not nome.replace(' ', '').isalpha():
            raise forms.ValidationError('O nome deve conter apenas letras e espaços.')
        return nome.title()  # Capitaliza o nome

    def clean_whatsapp(self):
        """Validação customizada para o WhatsApp."""
        whatsapp = self.cleaned_data['whatsapp'].strip()
        # Remove caracteres especiais para validação
        numero_limpo = ''.join(filter(str.isdigit, whatsapp))
        if len(numero_limpo) < 10 or len(numero_limpo) > 11:
            raise forms.ValidationError('Número de WhatsApp inválido.')
        return whatsapp