from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Listing, Category, AdminLog, Cidade
from .forms import ListingForm


def is_admin(user):
    return user.is_staff


def home(request):
    """Página inicial com listagem de anúncios"""
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    cidade_id = request.GET.get('cidade', '')
    
    listings = Listing.objects.filter(status='approved')
    
    if search_query:
        listings = listings.filter(
            Q(business_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    if category_id:
        listings = listings.filter(category_id=category_id)
    
    if cidade_id:
        listings = listings.filter(cidade_id=cidade_id)  # Agora funciona
    
    paid_listings = listings.filter(plan='paid').order_by('-created_at')[:6]
    free_listings = listings.filter(plan='free').order_by('-created_at')
    
    paginator = Paginator(free_listings, 12)
    page_number = request.GET.get('page', 1)
    free_listings_page = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    cidades = Cidade.objects.filter(ativa=True)
    
    context = {
        'paid_listings': paid_listings,
        'free_listings': free_listings_page,
        'categories': categories,
        'cidades': cidades,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id else None,
        'cidade_selecionada': int(cidade_id) if cidade_id else None,
        'total_listings': listings.count(),
    }
    
    return render(request, 'listings/home.html', context)


def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug, status='approved')
    listing.views += 1
    listing.save(update_fields=['views'])
    
    related_listings = Listing.objects.filter(
        status='approved',
        category=listing.category
    ).exclude(id=listing.id)[:4]
    
    context = {
        'listing': listing,
        'related_listings': related_listings,
    }
    
    return render(request, 'listings/listing_detail.html', context)


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.status = 'pending'
            listing.save()
            messages.success(request, 'Anúncio criado! Aguarde aprovação.')
            return redirect('meus_anuncios')
    else:
        form = ListingForm()
    
    return render(request, 'listings/create_listing.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_listings(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    listings = Listing.objects.all()
    
    if status_filter:
        listings = listings.filter(status=status_filter)
    
    if search_query:
        listings = listings.filter(
            Q(business_name__icontains=search_query) |
            Q(owner__username__icontains=search_query)  # Corrigido: era owner_email
        )
    
    listings = listings.order_by('-created_at')
    paginator = Paginator(listings, 10)
    page_number = request.GET.get('page', 1)
    listings_page = paginator.get_page(page_number)
    
    context = {
        'listings': listings_page,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'listings/admin_listings.html', context)


@login_required
@user_passes_test(is_admin)
def approve_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    listing.status = 'approved'
    listing.save()
    
    AdminLog.objects.create(
        admin=request.user,
        listing=listing,
        action='approve'
    )
    
    messages.success(request, f'Anúncio "{listing.business_name}" aprovado!')
    return redirect('admin_listings')


@login_required
@user_passes_test(is_admin)
def reject_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    reason = request.POST.get('reason', '')
    
    listing.status = 'rejected'
    listing.save()
    
    AdminLog.objects.create(
        admin=request.user,
        listing=listing,
        action='reject',
        reason=reason
    )
    
    messages.success(request, f'Anúncio "{listing.business_name}" rejeitado!')
    return redirect('admin_listings')


@login_required
@user_passes_test(is_admin)
def mark_paid(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    listing.plan = 'paid'  # Corrigido: era is_paid = True
    listing.save()
    
    AdminLog.objects.create(
        admin=request.user,
        listing=listing,
        action='mark_paid'
    )
    
    messages.success(request, f'Anúncio "{listing.business_name}" marcado como pago!')
    return redirect('admin_listings')


@login_required
@user_passes_test(is_admin)
def mark_free(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    listing.plan = 'free'  # Corrigido: era is_paid = False
    listing.save()
    
    AdminLog.objects.create(
        admin=request.user,
        listing=listing,
        action='mark_free'
    )
    
    messages.success(request, f'Anúncio "{listing.business_name}" marcado como gratuito!')
    return redirect('admin_listings')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Painel administrativo principal"""
    total_listings = Listing.objects.count()
    pending = Listing.objects.filter(status='pending').count()
    approved = Listing.objects.filter(status='approved').count()
    rejected = Listing.objects.filter(status='rejected').count()
    total_views = Listing.objects.filter(status='approved').aggregate(
        total=Sum('views')
    )['total'] or 0
    
    # Últimos anúncios pendentes
    pending_listings = Listing.objects.filter(status='pending').order_by('-created_at')[:5]
    
    context = {
        'total_listings': total_listings,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'total_views': total_views,
        'pending_listings': pending_listings,
    }
    return render(request, 'listings/admin_dashboard.html', context)

# resto das views igual...
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada! Agora cadastre seu anúncio.')
            return redirect('create_listing')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def meus_anuncios(request):
    listings = Listing.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'listings': listings,
        'total': listings.count(),
        'aprovados': listings.filter(status='approved').count(),
        'pendentes': listings.filter(status='pending').count(),
        'rejeitados': listings.filter(status='rejected').count(),
    }
    return render(request, 'listings/meus_anuncios.html', context)


@login_required
def editar_anuncio(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.status = 'pending'
            listing.save()
            messages.success(request, 'Anúncio atualizado! Aguarde nova aprovação.')
            return redirect('meus_anuncios')
    else:
        form = ListingForm(instance=listing)
    
    context = {
        'form': form, 
        'listing': listing,
        'editando': True
    }
    return render(request, 'listings/create_listing.html', context)