from django.contrib import admin
from .models import Listing, Category, AdminLog, Cidade

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

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'owner', 'status', 'plan', 'created_at', 'views']
    list_filter = ['status', 'plan', 'category']
    search_fields = ['business_name', 'owner__username']
    list_editable = ['status', 'plan']  # Pra aprovar direto no admin
    readonly_fields = ['slug', 'views', 'created_at']
    
    fieldsets = (
        ('Informações do Negócio', {
            'fields': ('business_name', 'slug', 'description', 'category', 'logo')
        }),
        ('Contato', {
            'fields': ('phone', 'whatsapp', 'email', 'address', 'cidade')
        }),
        ('Configurações', {
            'fields': ('owner', 'status', 'plan', 'views')
        }),
    )