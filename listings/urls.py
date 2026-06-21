from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Público
    path('', views.home, name='home'),
    path('anuncio/<slug:slug>/', views.listing_detail, name='listing_detail'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('create/', views.create_listing, name='create_listing'),
    path('meus-anuncios/', views.meus_anuncios, name='meus_anuncios'),
    path('meus-anuncios/<int:listing_id>/editar/', views.editar_anuncio, name='editar_anuncio'),
    
    # Painel Admin Customizado - troquei de admin/ pra painel/
    #path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/anuncios/', views.admin_listings, name='admin_listings'),
    path('painel/anuncios/<int:listing_id>/aprovar/', views.approve_listing, name='approve_listing'),
    path('painel/anuncios/<int:listing_id>/rejeitar/', views.reject_listing, name='reject_listing'),
    path('painel/anuncios/<int:listing_id>/pago/', views.mark_paid, name='mark_paid'),
    path('painel/anuncios/<int:listing_id>/gratis/', views.mark_free, name='mark_free'),
    #path('painel/categorias/', views.admin_categories, name='admin_categories'),
    #path('painel/categorias/<int:category_id>/deletar/', views.delete_category, name='delete_category'),
]