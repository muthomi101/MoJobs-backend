from rest_framework import serializers
from .models import SellerProfile, Item

# --------------------------
# Seller Profile Serializer
# --------------------------
class SellerProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = SellerProfile
        fields = ['name', 'phone_number', 'location', 'is_verified', 'created_at']
        read_only_fields = ['name', 'phone_number', 'is_verified', 'created_at']


# --------------------------
# Item Serializer
# --------------------------
class ItemSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.user.name', read_only=True)
    contact_call = serializers.CharField(source='seller.user.phone_number', read_only=True)
    fee = serializers.SerializerMethodField()
    fee_type = serializers.SerializerMethodField()  # for frontend
    mpesa_ref = serializers.CharField(write_only=True, required=False)  # optional field

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'description',
            'price',
            'category',
            'location',        # item location
            'image_url',
            'contact_call',    # single phone field
            'is_paid',
            'fee_paid',
            'is_active',
            'created_at',
            'seller_name',
            'fee',
            'fee_type',
            'mpesa_ref',
        ]
        read_only_fields = [
            'is_paid',
            'fee_paid',
            'is_active',
            'created_at',
            'seller_name',
            'fee',
            'fee_type',
            'contact_call',
        ]

    def get_fee(self, obj):
        return obj.calculate_fee()

    def get_fee_type(self, obj):
        # First, check if the item was free
        if obj.fee_paid == 0:
            return "free"

        # Count previous items for this seller (excluding current)
        seller_items_count = obj.seller.items.exclude(id=obj.id).count()

        if obj.price < Item.PRICE_THRESHOLD:
            # Subsequent items under 5000
            return "paid"
        else:
            # Items >=5000
            if seller_items_count == 0:
                return "first item 5%"  # first item >=5000
            return "10%"                # subsequent items >=5000

