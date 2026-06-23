from django.core.management.base import BaseCommand
from django.utils import timezone

from listings.models import AdminLog, Listing


class Command(BaseCommand):
    """
    Rebaixa pra "Grátis" todo anúncio pago cuja data de expiração já passou.

    Rode isso uma vez por dia via cron no VPS, por exemplo:
        0 3 * * * /caminho/venv/bin/python /caminho/manage.py expirar_destaques

    A home já trata anúncios vencidos como não-destaque mesmo sem esse
    comando rodar (ver `Listing.esta_destacado` e o filtro da view `home`),
    então isso aqui é só pra manter o campo `plan` do banco coerente — sem
    isso, o painel administrativo continuaria mostrando "Pago" pra um
    anúncio que já devia ter voltado a ser gratuito.
    """

    help = 'Rebaixa para "Grátis" os anúncios pagos com data de expiração vencida.'

    def handle(self, *args, **options):
        agora = timezone.now()
        expirados = Listing.objects.filter(
            plan='paid', data_expiracao__isnull=False, data_expiracao__lt=agora,
        )

        total = 0
        for listing in expirados:
            listing.plan = 'free'
            listing.data_expiracao = None
            listing.save(update_fields=['plan', 'data_expiracao'])
            AdminLog.objects.create(
                admin=None,
                listing=listing,
                action='mark_free',
                reason='Expirado automaticamente (expirar_destaques)',
            )
            total += 1

        self.stdout.write(self.style.SUCCESS(f'{total} anúncio(s) rebaixado(s) para gratuito.'))
