from django import forms
from .models import Listing, Cidade, Category

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