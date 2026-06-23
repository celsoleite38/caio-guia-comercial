"""
Views para gerenciar avaliações de anúncios.
Adicionar estas funções ao arquivo listings/views.py
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Avg
from .models import Listing, Rating
from .rating_forms import RatingForm


@login_required
def create_rating(request, listing_id):
    """
    Cria uma nova avaliação ou atualiza a existente para um anúncio.
    """
    listing = get_object_or_404(Listing, id=listing_id, status='approved')
    
    # Verifica se o usuário já avaliou este anúncio
    existing_rating = Rating.objects.filter(
        listing=listing,
        user=request.user
    ).first()
    
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=existing_rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.listing = listing
            rating.user = request.user
            rating.save()
            
            action = 'atualizada' if existing_rating else 'criada'
            messages.success(request, f'Avaliação {action} com sucesso!')
            return redirect('listing_detail', slug=listing.slug)
    else:
        form = RatingForm(instance=existing_rating)
    
    context = {
        'form': form,
        'listing': listing,
        'existing_rating': existing_rating,
    }
    return render(request, 'listings/create_rating.html', context)


@login_required
@require_POST
def delete_rating(request, rating_id):
    """
    Deleta uma avaliação (apenas o autor ou admin podem deletar).
    """
    rating = get_object_or_404(Rating, id=rating_id)
    
    if rating.user != request.user and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para deletar esta avaliação.')
        return redirect('listing_detail', slug=rating.listing.slug)
    
    listing_slug = rating.listing.slug
    rating.delete()
    messages.success(request, 'Avaliação deletada com sucesso!')
    return redirect('listing_detail', slug=listing_slug)


@require_GET
def listing_ratings(request, listing_id):
    """
    Retorna as avaliações de um anúncio em formato JSON.
    Útil para carregamento dinâmico via AJAX.
    """
    listing = get_object_or_404(Listing, id=listing_id, status='approved')
    ratings = listing.ratings.all()
    
    ratings_data = [
        {
            'id': rating.id,
            'user': rating.user.username,
            'stars': rating.stars,
            'comment': rating.comment,
            'created_at': rating.created_at.strftime('%d/%m/%Y'),
        }
        for rating in ratings
    ]
    
    return JsonResponse({
        'listing_id': listing.id,
        'average_rating': listing.average_rating,
        'total_ratings': listing.total_ratings,
        'ratings': ratings_data,
    })
