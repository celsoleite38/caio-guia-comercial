from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from . import rating_views

urlpatterns = [
    # Público
    path('', views.home, name='home'),
    path('anuncio/<slug:slug>/', views.listing_detail, name='listing_detail'),
    #path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_listing, name='create_listing'),
    path('meus-anuncios/', views.meus_anuncios, name='meus_anuncios'),
    path('meus-anuncios/<int:listing_id>/editar/', views.editar_anuncio, name='editar_anuncio'),
    
    # Painel Admin Customizado - troquei de admin/ pra painel/
    path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/anuncios/', views.admin_listings, name='admin_listings'),
    path('painel/anuncios/<int:listing_id>/aprovar/', views.approve_listing, name='approve_listing'),
    path('painel/anuncios/<int:listing_id>/rejeitar/', views.reject_listing, name='reject_listing'),
    path('painel/anuncios/<int:listing_id>/pago/', views.mark_paid, name='mark_paid'),
    path('painel/anuncios/<int:listing_id>/gratis/', views.mark_free, name='mark_free'),
    path('painel/categorias/', views.admin_categories, name='admin_categories'),
    path('painel/categorias/<int:category_id>/deletar/', views.delete_category, name='delete_category'),
    #cidades
    path('painel/cidades/', views.admin_cities, name='admin_cities'),
    path('painel/cidades/<int:city_id>/deletar/', views.delete_city, name='delete_city'),
    
    # Rotas de Avaliacoes
    path('anuncio/<int:listing_id>/avaliar/', rating_views.create_rating, name='create_rating'),
    path('avaliacao/<int:rating_id>/deletar/', rating_views.delete_rating, name='delete_rating'),
    path('api/anuncio/<int:listing_id>/avaliacoes/', rating_views.listing_ratings, name='listing_ratings_api'),
]