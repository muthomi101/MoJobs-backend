from rest_framework import generics, permissions, serializers
from .models import SellerProfile, Item
from .serializers import SellerProfileSerializer, ItemSerializer

# --------------------------
# Seller Profile
# --------------------------
class SellerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.seller_profile
        except SellerProfile.DoesNotExist:
            raise serializers.ValidationError("No seller profile found for this user")


# --------------------------
# Item CRUD
# --------------------------
class ItemCreateView(generics.CreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Only sellers can create items
        try:
            seller_profile = self.request.user.seller_profile
        except SellerProfile.DoesNotExist:
            raise serializers.ValidationError("Only sellers can create items")

        # Save the item first
        item = serializer.save(seller=seller_profile)

        # Calculate fee immediately using existing logic
        item.fee_paid = item.calculate_fee()
        item.save()

        # Check if Mpesa reference is provided (optional)
        mpesa_ref = self.request.data.get('mpesa_ref')
        if mpesa_ref:
            # Automatically mark as paid and active
            item.mark_as_paid()


class ItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only active items are publicly visible
        return Item.objects.filter(is_active=True)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]  # Public GET

    def get_queryset(self):
        """
        Public users: only active items
        Authenticated sellers/admins: full queryset for update/delete
        """
        user = self.request.user
        if user.is_authenticated:
            try:
                # Sellers can only access their own items for update/delete
                return Item.objects.filter(seller=user.seller_profile)
            except SellerProfile.DoesNotExist:
                # Admins or other users can access all items
                return Item.objects.all()
        # Anonymous users: only active items
        return Item.objects.filter(is_active=True)

    def perform_update(self, serializer):
        # Only authenticated users can update
        if not self.request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to update")

        instance = serializer.save()

        # Recalculate fee if price is updated
        if 'price' in self.request.data:
            instance.fee_paid = instance.calculate_fee()
            instance.save()

        # Automatically mark as paid if Mpesa reference is provided
        mpesa_ref = self.request.data.get('mpesa_ref')
        if mpesa_ref:
            instance.mark_as_paid()


# views.py
class MyItemsListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            return Item.objects.filter(seller=self.request.user.seller_profile)
        except SellerProfile.DoesNotExist:
            return Item.objects.none()  # user is not a seller

