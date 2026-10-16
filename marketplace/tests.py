# marketplace/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import SellerProfile, Item
from decimal import Decimal

class MarketplaceTests(APITestCase):

    def setUp(self):
        # Create a seller
        self.seller = User.objects.create_user(
            phone_number="0723000001",
            name="Test Seller",
            id_number="12345678",
            role="seller",
            password="securepassword"
        )
        self.token_url = reverse('token_obtain_pair')  # or your login endpoint
        self.items_url = reverse('item-create')  # or your create endpoint

    def authenticate(self):
        # Log in and get token
        response = self.client.post(
            '/api/accounts/login/',
            {'phone_number': '0723000001', 'password': 'securepassword'},
            format='json'
        )
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_first_item_under_5000_is_free(self):
        self.authenticate()
        data = {
            "title": "Basic Hammer",
            "description": "Simple hammer",
            "price": "3000.00",
            "category": "other",
            "contact_call": "0723000001",
            "contact_whatsapp": "0723000001"
        }
        response = self.client.post('/api/marketplace/items/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = Item.objects.get(id=response.data['id'])
        self.assertEqual(item.fee_paid, Decimal('0.00'))
        self.assertEqual(response.data['fee_type'], "free")
        self.assertFalse(item.is_paid)
        self.assertFalse(item.is_active)

    def test_second_item_under_5000_is_paid(self):
        self.authenticate()
        # create first free item
        Item.objects.create(
            seller=self.seller.seller_profile,
            title="Free Item",
            price=Decimal('2000.00'),
        )
        data = {
            "title": "Second Hammer",
            "description": "Another hammer",
            "price": "3000.00",
            "category": "other",
            "contact_call": "0723000001",
            "contact_whatsapp": "0723000001"
        }
        response = self.client.post('/api/marketplace/items/create/', data, format='json')
        item = Item.objects.get(id=response.data['id'])
        self.assertEqual(item.fee_paid, Decimal('50.00'))
        self.assertEqual(response.data['fee_type'], "paid")

    def test_first_item_over_5000_fee_5_percent(self):
        self.authenticate()
        data = {
            "title": "Premium Drill",
            "description": "High-end drill",
            "price": "10000.00",
            "category": "electronics",
            "contact_call": "0723000001",
            "contact_whatsapp": "0723000001"
        }
        response = self.client.post('/api/marketplace/items/create/', data, format='json')
        item = Item.objects.get(id=response.data['id'])
        self.assertEqual(item.fee_paid, Decimal('500.00'))  # 5% of 10000
        self.assertEqual(response.data['fee_type'], "first item 5%")

    def test_second_item_over_5000_fee_10_percent(self):
        self.authenticate()
        # create first >5000 item
        Item.objects.create(
            seller=self.seller.seller_profile,
            title="First Drill",
            price=Decimal('10000.00'),
        )
        data = {
            "title": "Second Drill",
            "description": "Another drill",
            "price": "15000.00",
            "category": "electronics",
            "contact_call": "0723000001",
            "contact_whatsapp": "0723000001"
        }
        response = self.client.post('/api/marketplace/items/create/', data, format='json')
        item = Item.objects.get(id=response.data['id'])
        self.assertEqual(item.fee_paid, Decimal('1500.00'))  # 10% of 15000
        self.assertEqual(response.data['fee_type'], "10%")

