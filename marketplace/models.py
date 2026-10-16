from django.db import models
from django.conf import settings
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

# --------------------------
# Seller Profile
# --------------------------
class SellerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} ({self.user.phone_number})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_seller_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'seller':
        SellerProfile.objects.create(user=instance)


# --------------------------
# Item Model
# --------------------------
class Item(models.Model):
    PRICE_THRESHOLD = Decimal('5000.00')
    MIN_FEE = Decimal('50.00')

    CATEGORY_CHOICES = [
        ('clothes', 'Clothes'),
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('services', 'Services'),
        ('tools', 'Tools'),
        ('agriculture', 'Agriculture'),
        ('food', 'Food & Beverages'),
        ('books', 'Books & Stationery'),
        ('other', 'Other'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    image_url = models.URLField(blank=True, null=True)
    contact_call = models.CharField(max_length=20, blank=True, null=True)
    contact_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # <-- new field
    is_paid = models.BooleanField(default=False)
    fee_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_fee(self):
        """Return the fee the seller should pay based on rules."""
        seller_items = self.seller.items.exclude(id=self.id).order_by('created_at')

        if self.price < self.PRICE_THRESHOLD:
            # First item under 5000 is free
            if not seller_items.filter(price__lt=self.PRICE_THRESHOLD).exists():
                return Decimal('0.00')
            return self.MIN_FEE
        else:
            # First item >=5000 is 5%, others 10%
            if not seller_items.filter(price__gte=self.PRICE_THRESHOLD).exists():
                return self.price * Decimal('0.05')
            return self.price * Decimal('0.10')

    def mark_as_paid(self):
        self.fee_paid = self.calculate_fee()
        self.is_paid = True
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.title} ({self.seller.user.name})"


# --------------------------
# Auto-mark first <5000 item as paid
# --------------------------
@receiver(post_save, sender=Item)
def auto_mark_first_cheap_item(sender, instance, created, **kwargs):
    if created and instance.price < Item.PRICE_THRESHOLD:
        # Check if this is the first <5000 item for this seller
        previous_cheap_items = instance.seller.items.filter(price__lt=Item.PRICE_THRESHOLD).exclude(id=instance.id)
        if not previous_cheap_items.exists():
            instance.mark_as_paid()

