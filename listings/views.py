from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .models import Banner, Listing, ListingImage, Category, AdminLog, Cidade, Anunciante
from .forms import ListingForm, CadastroAnuncianteForm
import secrets
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404




GALERIA_MAX_FOTOS = 5
GALERIA_MAX_TAMANHO_MB = 2


def _salvar_galeria(listing, arquivos):
    """
    Salva as fotos extras enviadas no formulário de anúncio. Limita a
    quantidade total (já existentes + novas) e o tamanho de cada arquivo,
    devolvendo uma lista de avisos pra mostrar ao usuário quando algo é
    ignorado (em vez de travar o cadastro inteiro por causa de uma foto).
    """
    avisos = []
    vagas = GALERIA_MAX_FOTOS - listing.galeria.count()
    proxima_ordem = listing.galeria.count()

    for arquivo in arquivos:
        if vagas <= 0:
            avisos.append(f'Limite de {GALERIA_MAX_FOTOS} fotos na galeria atingido — algumas fotos não foram salvas.')
            break
        if arquivo.size > GALERIA_MAX_TAMANHO_MB * 1024 * 1024:
            avisos.append(f'"{arquivo.name}" ultrapassa {GALERIA_MAX_TAMANHO_MB}MB e foi ignorada.')
            continue
        ListingImage.objects.create(listing=listing, imagem=arquivo, ordem=proxima_ordem)
        proxima_ordem += 1
        vagas -= 1

    return avisos


def is_admin(user):
    return user.is_staff


def home(request):
    """Página inicial com listagem de anúncios, filtros, médias de notas e ordenação"""
    # 1. Captura os parâmetros da URL
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    cidade_id = request.GET.get('cidade', '')
    ordenacao = request.GET.get('ordenar', '')  # Novo filtro de ordenação
    
    # 2. Base QuerySet: Traz apenas os aprovados e já calcula a média de notas usando o relacionamento real ('ratings__stars')
    listings = Listing.objects.filter(status='approved').annotate(
        media_nota=Avg('ratings__stars')
    )
    
    # 3. Aplica os filtros de busca (se existirem) mantendo a persistência dos dados
    if search_query:
        listings = listings.filter(
            Q(business_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    if category_id:
        listings = listings.filter(category_id=category_id)
    
    if cidade_id:
        listings = listings.filter(cidade_id=cidade_id)

    # 4. Define o critério de Destaque Pago (Plano pago E não expirado)
    agora = timezone.now()
    eh_destaque = Q(plan='paid') & (Q(data_expiracao__isnull=True) | Q(data_expiracao__gt=agora))

    banners_topo = Listing.objects.filter(
        status='approved',
        destaque_topo=True,
    ).exclude(
        slug=""
    ).exclude(
        logo=""
    ).filter(
        Q(data_expiracao_topo__isnull=True) | Q(data_expiracao_topo__gt=agora)
    )

    paid_listings = Listing.objects.filter(
        status='approved',
        plan='paid'
    ).annotate(
        media_nota=Avg('ratings__stars')
    ).exclude(slug="").filter(
        Q(data_expiracao__isnull=True) | Q(data_expiracao__gt=agora)
    )

    # CORREÇÃO AQUI: Adicionado .annotate() para os anúncios gratuitos trazerem a nota do banco
    free_listings = Listing.objects.filter(
        status='approved',
        plan='free'
    ).annotate(
        media_nota=Avg('ratings__stars')
    ).exclude(slug="")

    
    if ordenacao == 'melhores':
        paid_listings = paid_listings.order_by('-media_nota', '-created_at')
        free_listings = free_listings.order_by('-media_nota', '-created_at')
    elif ordenacao == 'piores':
        # Coloca quem tem nota mais baixa primeiro, e joga quem não tem avaliação para o final
        paid_listings = paid_listings.order_by('media_nota', '-created_at')
        free_listings = free_listings.order_by('media_nota', '-created_at')
    else:
        # Ordenação padrão por data de criação se nenhum filtro de nota for selecionado
        paid_listings = paid_listings.order_by('-created_at')
        free_listings = free_listings.order_by('-created_at')

    # Limita os destaques exibidos no topo (ex: no máximo 6)
    paid_listings = paid_listings[:6]
    
    # 7. Paginação dos anúncios gratuitos
    paginator = Paginator(free_listings, 12)
    page_number = request.GET.get('page', 1)
    free_listings_page = paginator.get_page(page_number)
    
    # 8. Querysets auxiliares para montar as caixas de seleção do HTML
    categories = Category.objects.all()
    cidades = Cidade.objects.filter(ativa=True)

    # Busca apenas os banners ativos para o topo
    banners = Banner.objects.filter(ativo=True)
    
    context = {
        'paid_listings': paid_listings,
        'free_listings': free_listings_page,
        'categories': categories,
        'cidades': cidades,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
        'cidade_selecionada': int(cidade_id) if cidade_id and cidade_id.isdigit() else None,
        'ordenacao': ordenacao,  # Enviado para manter o <select> marcado no HTML
        'total_listings': listings.count(),
        'banners': banners_topo,
    }
    
    return render(request, 'listings/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')



def listing_detail(request, slug):
    # 1. Busca o anúncio apenas pelo slug para não dar 404 imediato
    listing = get_object_or_404(Listing, slug=slug)
    
    # 2. Se NÃO estiver aprovado, valida quem está tentando acessar
    if listing.status != 'approved':
        if not (request.user.is_authenticated and (request.user.is_staff or request.user == listing.user)):
            raise Http404("No Listing matches the given query.")
    else:
        # 3. Só contabiliza a visualização se o anúncio já estiver aprovado e público
        listing.views += 1
        listing.save(update_fields=['views'])
    
    # 4. Busca anúncios relacionados (apenas aprovados)
    related_listings = Listing.objects.filter(
        status='approved',
        category=listing.category
    ).exclude(id=listing.id)[:4]

    # 5. Distribuição de estrelas (continua igual)
    stars_query = listing.ratings.values('stars').annotate(total=Count('id'))
    stars_distribution = {i: 0 for i in range(1, 6)}
    for item in stars_query:
        stars_distribution[item['stars']] = item['total']
        
    ratings_by_stars = sorted(stars_distribution.items(), key=lambda x: x[0], reverse=True)
    
    context = {
        'listing': listing,
        'related_listings': related_listings,
        'ratings_by_stars': ratings_by_stars, # Certifique-se de passar isso se usar no template
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

            avisos = _salvar_galeria(listing, request.FILES.getlist('galeria'))
            for aviso in avisos:
                messages.warning(request, aviso)

            messages.success(request, 'Anúncio criado! Aguarde aprovação.')
            return redirect('meus_anuncios')
    else:
        form = ListingForm()
    
    return render(request, 'listings/create_listing.html', {'form': form, 'galeria_max_fotos': GALERIA_MAX_FOTOS})


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
@require_POST
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
@require_POST
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
@require_POST
def mark_paid(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    dias = request.POST.get('dias', '').strip()

    listing.plan = 'paid'
    if dias.isdigit() and int(dias) > 0:
        listing.data_expiracao = timezone.now() + timedelta(days=int(dias))
        descricao_prazo = f'destaque por {dias} dias'
    else:
        listing.data_expiracao = None
        descricao_prazo = 'destaque sem prazo definido'
    listing.save()

    AdminLog.objects.create(
        admin=request.user,
        listing=listing,
        action='mark_paid',
        reason=descricao_prazo,
    )
    
    messages.success(request, f'Anúncio "{listing.business_name}" marcado como pago ({descricao_prazo}).')
    return redirect('admin_listings')


@login_required
@user_passes_test(is_admin)
@require_POST
def mark_free(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    listing.plan = 'free'  # Corrigido: era is_paid = False
    listing.data_expiracao = None
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
    pending_count = Listing.objects.filter(status='pending').count()
    approved_count = Listing.objects.filter(status='approved').count()
    rejected_count = Listing.objects.filter(status='rejected').count()
    total_views = Listing.objects.filter(status='approved').aggregate(
        total=Sum('views')
    )['total'] or 0
    
    # Últimos anúncios pendentes
    pending_listings = Listing.objects.filter(status='pending').order_by('-created_at')[:5]
    
    context = {
        'total_listings': total_listings,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_views': total_views,
        'pending_listings': pending_listings,
    }
    return render(request, 'listings/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_categories(request):
    """Gerenciamento de categorias: cria pelo form da página e lista as existentes."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', '🏢').strip() or '🏢'
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'Informe o nome da categoria.')
        elif Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Já existe uma categoria chamada "{name}".')
        else:
            Category.objects.create(name=name, icon=icon, description=description)
            messages.success(request, f'Categoria "{name}" criada!')
            return redirect('admin_categories')

    categories = Category.objects.all().order_by('name')
    return render(request, 'listings/admin_categories.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if category.listings.exists():
        messages.error(
            request,
            f'Não dá pra excluir "{category.name}": ainda há anúncios usando essa categoria.',
        )
    else:
        category.delete()
        messages.success(request, 'Categoria excluída.')
    return redirect('admin_categories')

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

            # Remove as fotos que o anunciante marcou pra excluir
            remover_ids = request.POST.getlist('remover_foto')
            if remover_ids:
                listing.galeria.filter(id__in=remover_ids).delete()

            avisos = _salvar_galeria(listing, request.FILES.getlist('galeria'))
            for aviso in avisos:
                messages.warning(request, aviso)

            messages.success(request, 'Anúncio atualizado! Aguarde nova aprovação.')
            return redirect('meus_anuncios')
    else:
        form = ListingForm(instance=listing)
    
    context = {
        'form': form, 
        'listing': listing,
        'editando': True,
        'galeria_max_fotos': GALERIA_MAX_FOTOS,
    }
    return render(request, 'listings/create_listing.html', context)


def cadastrar_anunciante(request):
    if request.method == 'POST':
        form = CadastroAnuncianteForm(request.POST)
        if form.is_valid():
            # 1. Cria o User (Authentication) desativado por padrão
            user = User.objects.create_user(
                username=form.cleaned_data['email'].lower(), # E-mail como login
                email=form.cleaned_data['email'].lower(),
                password=form.cleaned_data['senha'],
                first_name=form.cleaned_data['nome'],
                is_active=False # Usuário não consegue logar até confirmar o e-mail
            )
            
            # 2. Cria o perfil do Anunciante com os dados complementares
            anunciante = form.save(commit=False)
            anunciante.user = user
            
            # Gera um token único e seguro de 64 caracteres
            token = secrets.token_urlsafe(32)
            anunciante.token_ativacao = token
            anunciante.save()

            # 3. Monta e envia o e-mail com o link de ativação
            # request.get_host() pega o domínio atual automaticamente (ex: caioindica.com.br ou localhost)
            link_ativacao = f"http://{request.get_host()}/accounts/ativar/{token}/"
            
            assunto = 'Confirme seu cadastro - Caio Indica'
            mensagem = f"Olá {user.first_name},\n\nObrigado por se cadastrar no Caio Indica!\n\nPara garantir a segurança da plataforma, precisamos que confirme seu e-mail clicando no link abaixo:\n\n{link_ativacao}\n\nSe você não realizou este cadastro, por favor ignore este e-mail."
            
            try:
                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                # Redireciona para uma página informando que o e-mail foi enviado
                return render(request, 'accounts/cadastro_pendente.html', {'email': user.email})
            except Exception as e:
                # Caso o servidor de e-mail falhe (ex: falta de credenciais no settings), remove o usuário criado para não travar o banco
                user.delete()
                messages.error(request, "Erro ao enviar e-mail de ativação. Tente novamente mais tarde.")
    else:
        form = CadastroAnuncianteForm()
    
    # Renderiza o seu arquivo correto dentro da pasta accounts
    return render(request, 'accounts/signup.html', {'form': form})


def ativar_conta_anunciante(request, token):
    # Procura o anunciante com o token correspondente
    anunciante = get_object_or_404(Anunciante, token_ativacao=token)
    
    # Ativa o usuário principal do Django Auth
    user = anunciante.user
    user.is_active = True
    user.save()
    
    # Atualiza o perfil do Anunciante e invalida o token para não ser reutilizado
    anunciante.email_confirmado = True
    anunciante.token_ativacao = None
    anunciante.save()
    
    # Redireciona para a tela de login com uma mensagem de sucesso
    messages.success(request, "Sua conta foi ativada com sucesso! Agora você pode fazer login.")
    return redirect('login') # Altere para o nome da sua rota de login, se for diferente