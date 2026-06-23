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
    list_display = ['business_name', 'owner', 'status', 'plan', 'data_expiracao', 'created_at', 'views']
    list_filter = ['status', 'plan', 'category']
    search_fields = ['business_name', 'owner__username']
    list_editable = ['status']  # plan fica de fora daqui de propósito: usar "Marcar como pago" no painel
                                 # (lá dá pra definir o prazo do destaque). Editar `plan` aqui na lista não
                                 # quebra nada, só fica sem prazo de expiração (destaque "vitalício").
    readonly_fields = ['slug', 'views', 'created_at']
    inlines = [ListingImageInline]

    fieldsets = (
        ('Informações do Negócio', {
            'fields': ('business_name', 'slug', 'description', 'category', 'logo')
        }),
        ('Contato', {
            'fields': ('phone', 'whatsapp', 'email', 'address', 'cidade')
        }),
        ('Benefícios do plano pago', {
            'fields': ('instagram', 'website'),
            'description': 'Só aparecem publicados no site se o anúncio estiver com plano Pago e dentro do prazo de destaque.',
        }),
        ('Configurações', {
            'fields': ('owner', 'status', 'plan', 'data_expiracao', 'views')
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
