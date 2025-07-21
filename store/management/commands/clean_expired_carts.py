from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import Cart, CartItem

class Command(BaseCommand):
    help = 'Cleans up expired carts'

    def handle(self, *args, **options):
        # Delete acrts older than 3 days
        expiration_time = timezone.now() - timezone.timedelta(days=3)
        deleted_count, _ = Cart.objects.filter(last_activity__lt=expiration_time).delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} expired carts.'))
