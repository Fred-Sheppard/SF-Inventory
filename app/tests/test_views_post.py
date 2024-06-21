from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from app.models import Stock, Catalogue, Bom, Location, Brand, BomItems


class PostTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.brand = Brand.objects.create(name="Test Brand")
        self.catalogue_item = Catalogue.objects.create(
            part_number="123",
            brand=self.brand,
            description="First Item",
        )
        self.catalogue_item2 = Catalogue.objects.create(
            part_number="456",
            brand=self.brand,
            description="Second Item"
        )
        self.catalogue_item3 = Catalogue.objects.create(
            part_number="789",
            brand=self.brand,
            description="Third Item"
        )
        self.location = Location.objects.create(location_name="Test Location")
        self.bom = Bom.objects.create(name="Bom 1")
        self.bom_item = BomItems.objects.create(part_number=self.catalogue_item, quantity=2, bom=self.bom)
        self.stock = Stock.objects.create(
            part_number=self.catalogue_item,
            location=self.location,
            quantity=10,
            modified_by=self.user.username
        )
        self.stock2 = Stock.objects.create(
            part_number=self.catalogue_item2,
            location=self.location,
            quantity=3,
            modified_by=self.user.username
        )
        self.client.login(username='testuser', password='password')

    def test_stock_create_success(self):
        self.assertFalse(Stock.objects.filter(part_number='789').exists())
        response = self.client.post(reverse('stock'), {
            'part_number': '789',
            'location': self.location.id,
            'quantity': 5,
            'submit-stock': 'submit-stock'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Stock.objects.filter(part_number='789').exists())
        self.assertRegex(response.content.decode(), "<td.*?789.*?<\\/td>")

    def test_stock_create_failure(self):
        response = self.client.post(reverse('stock'), {
            'part_number': 'NotReal',
            'location': self.location.id,
            'quantity': 5,
            'submit-stock': 'submit-stock'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Part number does not exist")
        self.assertFalse(Stock.objects.filter(part_number='789').exists())
        self.assertNotRegex(response.content.decode(), "<td.*?789.*?<\\/td>")

    def test_stock_post_filter_form(self):
        response = self.client.post(reverse('stock'), {
            'submit-filter': 'submit-filter',
            'part_number': '123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "catalogue/123")
        self.assertNotContains(response, "catalogue/456")

    def test_checkout_stock_post(self):
        response = self.client.post(reverse('checkout_stock', args=[self.stock.stock_id]), {
            'quantity': 5,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "123")
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 5)

    def test_catalogue_new_post(self):
        response = self.client.post(reverse('catalogue_new'), {
            'part_number': 'NewPN',
            'brand': self.catalogue_item.brand_id,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Catalogue.objects.filter(part_number='NewPN').exists())

    def test_catalogue_edit_post(self):
        self.assertIsNone(self.catalogue_item.category)
        response = self.client.post(reverse('catalogue_edit', args=[self.catalogue_item.part_number]), {
            'brand': self.catalogue_item.brand_id,
            'category': "Test Category"
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.catalogue_item.refresh_from_db()
        self.assertEqual(self.catalogue_item.category, 'Test Category')

    def test_location_new_post(self):
        response = self.client.post(reverse('location_new'), {
            'location_name': 'New Location',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Location.objects.filter(location_name='New Location').exists())

    def test_bom_new_post(self):
        response = self.client.post(reverse('bom_new'), {
            'name': 'New BOM',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Bom.objects.filter(name='New BOM').exists())

    def test_bom_edit_post(self):
        self.assertEqual(self.bom_item.quantity, 2)
        response = self.client.post(reverse('bom_edit', args=[self.bom.bom_id]), {
            "bomitems_set-TOTAL_FORMS": "1",
            "bomitems_set-INITIAL_FORMS": "1",
            "bomitems_set-0-id": "1",
            "bomitems_set-0-part_number": "123",
            "bomitems_set-0-quantity": "10",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bom_item.refresh_from_db()
        self.assertEqual(self.bom_item.quantity, 10)
