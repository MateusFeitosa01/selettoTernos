from django import forms
from django.core.validators import RegexValidator
from filas.models import ObservacaoAtendimento


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


class ObservacaoAtendimentoForm(forms.ModelForm):
    class Meta:
        model = ObservacaoAtendimento
        fields = [
            'status',
            'tipo_evento',
            'data_evento',
            'cidade',
            'local',
            'nomes_noivos',
            'contato_noivos',
            'universidade',
            'curso',
            'contato_formando',
            'nome_aniversariante',
            'tipo_evento_outro',
            'nome_cliente_observacao',
            'descricao',
            'motivo_nao_fechamento',
        ]
        widgets = {
            'status': forms.RadioSelect(
                choices=ObservacaoAtendimento.STATUS_CHOICES,
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'tipo_evento': forms.Select(attrs={
                'class': 'form-select rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
            }),
            'data_evento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Digite a cidade',
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Digite o local/venue',
            }),
            'nomes_noivos': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Nomes dos noivos',
            }),
            'contato_noivos': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': '(XX) XXXXX-XXXX',
            }),
            'universidade': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Digite a universidade',
            }),
            'curso': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Digite o curso',
            }),
            'contato_formando': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': '(XX) XXXXX-XXXX',
            }),
            'nome_aniversariante': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Nome do aniversariante',
            }),
            'tipo_evento_outro': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Descreva o tipo de evento',
            }),
            'nome_cliente_observacao': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Nome do cliente',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Descrição adicional',
                'rows': 4,
            }),
            'motivo_nao_fechamento': forms.TextInput(attrs={
                'class': 'form-control rounded-4 py-3 px-4 border-0 text-white',
                'style': 'background-color: rgb(38, 38, 38);',
                'placeholder': 'Digite o motivo do não fechamento',
            }),
        }