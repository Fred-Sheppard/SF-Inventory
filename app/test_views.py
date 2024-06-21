from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from app.models import Stock, Catalogue, Bom, Location, Brand


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.brand = Brand.objects.create(name="Test Brand")
        self.catalogue_item = Catalogue.objects.create(
            part_number="12345",
            brand=self.brand,
            description="Test Part",
        )
        self.location = Location.objects.create(location_name="Test Location")
        self.bom = Bom.objects.create(name="Test BOM")
        self.stock = Stock.objects.create(
            part_number=self.catalogue_item,
            location=self.location,
            quantity=10,
            modified_by=self.user.username
        )
        self.client.login(username='testuser', password='password')

    def test_default_view_redirect(self):
        response = self.client.get(reverse('default'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('stock'))

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, "Test BOM")
        self.assertContains(response, "Test Location")

    def test_register_view(self):
        self.client.logout()
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')
        self.assertContains(response, "Register a new account")

    def test_login_view(self):
        self.client.logout()
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')
        self.assertContains(response, "Login")

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_stock_view_get(self):
        response = self.client.get(reverse('stock'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stock.html')
        self.assertContains(response, "12345")
        self.assertContains(response, "Test Location")

    def test_checkout_stock_view(self):
        response = self.client.get(reverse('checkout_stock', args=[self.stock.stock_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')
        self.assertContains(response, "12345")

    def test_catalogue_view(self):
        response = self.client.get(reverse('catalogue'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table.html')
        self.assertContains(response, "Test Part")

    def test_catalogue_new_view(self):
        response = self.client.get(reverse('catalogue_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')
        self.assertContains(response, "New Entry")

    def test_catalogue_entry_view(self):
        response = self.client.get(reverse('catalogue_entry', args=["12345"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogue_entry.html')
        self.assertContains(response, "Test Part")

    def test_catalogue_edit_view(self):
        response = self.client.get(reverse('catalogue_edit', args=["12345"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')
        self.assertContains(response, "Editing 12345")

    def test_location_view(self):
        response = self.client.get(reverse('location', args=[self.location.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table.html')
        self.assertContains(response, "Test Location")

    def test_brand_view(self):
        response = self.client.get(reverse('brand', args=[self.brand.brand_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table.html')
        self.assertContains(response, "Test Brand")

    def test_location_new_view(self):
        response = self.client.get(reverse('location_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')
        self.assertContains(response, "New Location")

    def test_bom_view(self):
        response = self.client.get(reverse('bom', args=[self.bom.bom_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bom.html')
        self.assertContains(response, "Test BOM")

    def test_bom_new_view(self):
        response = self.client.get(reverse('bom_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')
        self.assertContains(response, "New Bom")

    def test_bom_edit_view(self):
        response = self.client.get(reverse('bom_edit', args=[self.bom.bom_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bom_edit.html')
        self.assertContains(response, self.bom.name)