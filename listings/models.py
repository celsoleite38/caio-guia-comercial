from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """Modelo para categorias de negócios"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='🏢', help_text='Emoji ou ícone da categoria')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Cidade(models.Model):
    """Modelo para cidades do guia comercial"""
    nome = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=2, help_text='UF - Ex: MG, SP')
    slug = models.SlugField(unique=True, blank=True)
    ativa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'

    def __str__(self):
        return f"{self.nome}/{self.estado}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.nome}-{self.estado}")
        super().save(*args, **kwargs)



class Listing(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]
    
    PLAN_CHOICES = [
        ('free', 'Grátis'),
        ('paid', 'Pago'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    business_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='listings')
    cidade = models.ForeignKey('Cidade', on_delete=models.PROTECT, null=True, blank=True)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField()  # email do negócio
    address = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Benefícios do anúncio pago ---
    instagram = models.URLField(
        'Instagram', blank=True,
        help_text='Link completo do perfil. Só aparece publicado se o plano for Pago.',
    )
    website = models.URLField(
        'Site', blank=True,
        help_text='Link do site/cardápio digital. Só aparece publicado se o plano for Pago.',
    )
    data_expiracao = models.DateTimeField(
        'Destaque válido até', null=True, blank=True,
        help_text='Preenchido ao marcar como Pago no painel. Deixe em branco para destaque sem prazo definido.',
    )

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.business_name)
        super().save(*args, **kwargs)

    @property
    def link_whatsapp(self):
        """
        Monta o link do wa.me a partir de whatsapp (ou phone, se whatsapp
        estiver vazio), limpando formatação e garantindo o DDI 55.
        Sem isso, números digitados como "(24) 99999-9999" quebram o wa.me.
        """
        numero = ''.join(filter(str.isdigit, self.whatsapp or self.phone or ''))
        if not numero:
            return ''
        if not numero.startswith('55'):
            numero = '55' + numero
        return f'https://wa.me/{numero}'

    @property
    def esta_destacado(self):
        """
        Fonte única de verdade pra saber se o anúncio deve ser tratado como
        destaque AGORA. Usa isso (e não só `plan == 'paid'`) em qualquer
        lugar que decide o que mostrar, porque um plano pago vencido não
        deve continuar com os benefícios mesmo antes do cron rodar.
        """
        if self.plan != 'paid':
            return False
        if self.data_expiracao and timezone.now() > self.data_expiracao:
            return False
        return True


class ListingImage(models.Model):
    """
    Fotos extras do anúncio (além da logo principal). Benefício do plano
    pago — a galeria só é exibida publicamente quando `listing.esta_destacado`
    é verdadeiro, mas o upload fica disponível pra todo mundo desde já, pra
    não precisar pedir pro anunciante reenviar foto quando ele virar pago.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='galeria')
    imagem = models.ImageField(upload_to='anuncios/galeria/')
    ordem = models.PositiveSmallIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Foto da galeria'
        verbose_name_plural = 'Fotos da galeria'
        ordering = ['ordem', 'id']

    def __str__(self):
        return f'Foto de {self.listing.business_name}'


class AdminLog(models.Model):
    """Modelo para auditoria de ações administrativas"""
    
    ACTION_CHOICES = [
        ('approve', 'Aprovado'),
        ('reject', 'Rejeitado'),
        ('mark_paid', 'Marcado como Pago'),
        ('mark_free', 'Marcado como Gratuito'),
        ('delete', 'Deletado'),
    ]

    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.admin} - {self.get_action_display()} - {self.listing.business_name}'
