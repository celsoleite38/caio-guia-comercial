from django import forms
from .models import Listing, Cidade, Category, Anunciante
from django.contrib.auth.models import User


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'business_name', 
            'description', 
            'category', 
            'cidade',  # Já tá aqui
            'phone', 
            'whatsapp', 
            'email',
            'address', 
            'logo',
            'instagram',
            'website',
        ]
        labels = {
            'business_name': 'Nome do Negócio',
            'description': 'Descrição',
            'category': 'Categoria *',
            'cidade': 'Cidade *',
            'phone': 'Telefone *',
            'whatsapp': 'WhatsApp',
            'email': 'Email do Negócio *',
            'address': 'Endereço',
            'logo': 'Logo/Foto',
            'instagram': 'Instagram',
            'website': 'Site',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.Select(attrs={'class': 'form-select'}),  # Select
            'category': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/seunegocio'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://seusite.com.br'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostra só cidades ativas no select
        self.fields['cidade'].queryset = Cidade.objects.filter(ativa=True)
        self.fields['cidade'].empty_label = "Selecione a cidade"
        self.fields['category'].empty_label = "Selecione a categoria"
        
        # Obriga cidade e categoria
        self.fields['cidade'].required = True
        self.fields['category'].required = True

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Logo deve ter no máximo 2MB')
        return logo
    


class CadastroAnuncianteForm(forms.ModelForm):
    # Campos extras do User que o anunciante vai preencher na mesma tela
    nome = forms.CharField(
        max_length=150, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crie uma senha forte'}), 
        required=True
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a senha novamente'}), 
        required=True,
        label="Confirme a Senha"
    )

    class Meta:
        model = Anunciante
        # Campos do modelo Anunciante que vão para a tela
        fields = ['telefone', 'is_whatsapp', 'tipo_pessoa', 'documento', 'rua', 'numero', 'bairro', 'cidade']
        
        widgets = {
            'tipo_pessoa': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Selecione o tipo primeiro'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Av. Paulista'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Centro'}),
            'cidade': forms.Select(attrs={'class': 'form-control form-select'}), # Combobox automático do banco
        }

    
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error('confirmar_senha', "As senhas digitadas não são iguais.")
        
        return cleaned_data