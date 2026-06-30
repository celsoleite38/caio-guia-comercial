from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from.models import AdminLog, Category, Cidade, Listing, ListingImage, Rating, Banner


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Cidade)
class CidadeAdmin(ImportExportModelAdmin):
    list_display = ['nome', 'estado', 'ativa', 'created_at']
    list_filter = ['estado', 'ativa']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome', 'estado')}

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ['imagem', 'ordem']

@admin.register(Listing)
class ListingAdmin(ImportExportModelAdmin):
    list_display = ['business_name', 'owner', 'status', 'plan', 'destaque_topo', 'data_expiracao', 'created_at', 'views']
    list_editable = ['status', 'destaque_topo']
    list_filter = ['status', 'plan', 'category', 'destaque_topo', 'cidade']
    search_fields = ['business_name', 'owner__username']
    readonly_fields = ['slug', 'views', 'created_at']
    inlines = [ListingImageInline]

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

@admin.register(ListingImage)
class ListingImageAdmin(ImportExportModelAdmin):
    list_display = ['listing', 'imagem', 'ordem']
    list_filter = ['listing']
    search_fields = ['listing__business_name']

@admin.register(AdminLog)
class AdminLogAdmin(ImportExportModelAdmin):
    list_display = ['listing', 'admin', 'action', 'reason', 'created_at']
    list_filter = ['action']
    search_fields = ['listing__business_name']
    readonly_fields = ['listing', 'admin', 'action', 'reason', 'created_at']

@admin.register(Rating)
class RatingAdmin(ImportExportModelAdmin):
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

@admin.register(Banner)
class BannerAdmin(ImportExportModelAdmin):
    list_display = ('titulo', 'ativo', 'ordem', 'criado_em')
    list_editable = ('ativo', 'ordem')
    list_filter = ('ativo',)
    search_fields = ('titulo',)