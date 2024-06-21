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
            part_number="12345",
            brand=self.brand,
            description="Test Part",
        )
        self.catalogue_item2 = Catalogue.objects.create(
            part_number="678",
            brand=self.brand,
            description="Second Item"
        )
        self.catalogue_item3 = Catalogue.objects.create(
            part_number="999",
            brand=self.brand,
            description="Third Item"
        )
        self.location = Location.objects.create(location_name="Test Location")
        self.bom = BomItems.objects.create(part_number="12345", quantity=2)
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

    def test_register_post(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration

    def test_login_post(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_stock_create_success(self):
        response = self.client.post(reverse('stock'), {
            'part_number': '999',
            'location': self.location.id,
            'quantity': 5,
            'submit-stock': 'submit-stock'
        }, follow=True)
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "999")

    def test_stock_create_failure(self):
        response = self.client.post(reverse('stock'), {
            'part_number': 'NotReal',
            'location': self.location.id,
            'quantity': 5,
            'submit-stock': 'submit-stock'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Part number does not exist")

    def test_stock_post_filter_form(self):
        response = self.client.post(reverse('stock'), {
            'submit-filter': 'submit-filter',
            'part_number': '12345',
        }, follow=True)
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "catalogue/12345")
        self.assertNotContains(response, "catalogue/678")

    def test_checkout_stock_post(self):
        response = self.client.post(reverse('checkout_stock', args=[self.stock.stock_id]), {
            'quantity': 5,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "12345")
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 5)

    def test_catalogue_new_post(self):
        response = self.client.post(reverse('catalogue_new'), {
            'part_number': 'TP124',
            'brand': self.catalogue_item.brand_id,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Catalogue.objects.filter(part_number='TP124').exists())

    def test_catalogue_edit_post(self):
        response = self.client.post(reverse('catalogue_edit', args=[self.catalogue_item.part_number]), {
            'part_number': 'TP123',
            'brand': self.catalogue_item.brand_id,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.catalogue_item.refresh_from_db()
        self.assertEqual(self.catalogue_item.part_number, 'TP123')

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
        response = self.client.post(reverse('bom_edit', args=[self.bom.bom_id]), {
            'name': 'Edited BOM',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bom.refresh_from_db()
        self.assertEqual(self.bom.name, 'Edited BOM')
