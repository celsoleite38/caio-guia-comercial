from django.contrib import admin
from .models import AdminLog, Category, Cidade, Listing, ListingImage, Rating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'estado', 'ativa', 'created_at']
    list_filter = ['estado', 'ativa']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome', 'estado')}


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ['imagem', 'ordem']


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    # 1. Tabela de Listagem: Define as colunas que aparecem na tabela do Admin
    list_display = ['business_name', 'owner', 'status', 'plan', 'destaque_topo', 'data_expiracao', 'created_at', 'views']
    
    # 2. Edição Rápida: Permite alterar o status e ativar/desativar o carrossel direto na tabela
    list_editable = ['status', 'destaque_topo'] 
    
    # 3. Filtros Laterais e Busca
    list_filter = ['status', 'plan', 'category', 'destaque_topo', 'cidade']
    search_fields = ['business_name', 'owner__username']
    
    # 4. Campos de Apenas Leitura
    readonly_fields = ['slug', 'views', 'created_at']
    inlines = [ListingImageInline]

    # 5. Organização dos blocos dentro da página de edição do Anúncio
    fieldsets = (
        ('Informações do Negócio', {
            'fields': ('business_name', 'slug', 'description', 'category', 'logo')
        }),
        ('Contato', {
            'fields': ('phone', 'whatsapp', 'email', 'address', 'cidade')
        }),
        ('Benefícios do Plano Pago', {
            'fields': ('instagram', 'website'),
            'description': 'Só aparecem publicados no site se o anúncio estiver com plano Pago e dentro do prazo de destaque.',
        }),
        ('Configurações do Sistema', {
            'fields': ('owner', 'views', 'created_at')
        }),
        ('Status e Controle de Planos', {
            'fields': ('status', 'plan', 'data_expiracao', ('destaque_topo', 'data_expiracao_topo')),
            'description': 'Controle de aprovação e veiculação de anúncios premium no topo.',
        }),
    )


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['listing', 'admin', 'action', 'reason', 'created_at']
    list_filter = ['action']
    search_fields = ['listing__business_name']
    readonly_fields = ['listing', 'admin', 'action', 'reason', 'created_at']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'stars', 'created_at']
    list_filter = ['stars', 'created_at']
    search_fields = ['listing__business_name', 'user__username']
    readonly_fields = ['listing', 'user', 'created_at', 'updated_at']
    fieldsets = (
        ('Avaliacao', {
            'fields': ('listing', 'user', 'stars')
        }),
        ('Comentario', {
            'fields': ('comment',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativo', 'ordem', 'criado_em')
    list_editable = ('ativo', 'ordem')  # Permite ativar/desativar direto na listagem
    list_filter = ('ativo',)
    search_fields = ('titulo',)