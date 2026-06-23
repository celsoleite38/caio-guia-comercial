from django import forms
from .models import Rating


class RatingForm(forms.ModelForm):
    """Formulário para criar/editar avaliações de anúncios"""
    
    class Meta:
        model = Rating
        fields = ['stars', 'comment']
        labels = {
            'stars': 'Classificação (estrelas)',
            'comment': 'Comentário (opcional)',
        }
        widgets = {
            'stars': forms.RadioSelect(
                choices=[(i, f'{i} Estrela{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-check-input'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Compartilhe sua experiência (máximo 200 caracteres)',
                    'maxlength': '200',
                }
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '')
        if len(comment) > 200:
            raise forms.ValidationError('O comentário não pode ter mais de 200 caracteres.')
        return comment
