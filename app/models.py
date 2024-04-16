from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Bom(models.Model):
    bom_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=31)
    date_created = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f'BOM {self.bom_id} - {self.name}'


class BomItems(models.Model):
    bom = models.ForeignKey(Bom, models.CASCADE)
    part_number = models.ForeignKey('Catalogue', models.CASCADE, db_column='part_number')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"BOM {self.part_number} - {self.quantity}"

    class Meta:
        unique_together = ('bom', 'part_number')


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=31)

    def __str__(self):
        return self.name


class Catalogue(models.Model):
    part_number = models.CharField(primary_key=True, max_length=63)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, default='Empty')
    category = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    vendor_description = models.CharField(max_length=1023, blank=True, null=True)
    purchase_unit_cost_eur = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                                 verbose_name='Cost Price',
                                                 validators=[MinValueValidator(Decimal('0.01'))])
    sale_unit_cost_eur = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                             verbose_name='Selling Price',
                                             validators=[MinValueValidator(Decimal('0.01'))])
    notes = models.CharField(max_length=1023, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='images/parts')
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=20, null=True)

    def __str__(self):
        return str(self.part_number)


class Location(models.Model):
    location_name = models.CharField(max_length=63)

    def __str__(self):
        return self.location_name


class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    part_number = models.ForeignKey(Catalogue, models.CASCADE, db_column='part_number')
    location = models.ForeignKey(Location, models.DO_NOTHING, verbose_name='Location/Project')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField(blank=True, null=True)
    check_out = models.CharField(default='x', max_length=1, editable=False, auto_created=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"Stock {self.stock_id} - {self.part_number}. Quantity: {self.quantity}"


class CheckedOutStock(models.Model):
    checked_out_id = models.AutoField(primary_key=True, verbose_name='ID')
    part_number = models.ForeignKey(Catalogue, models.CASCADE, db_column='part_number')
    location = models.ForeignKey(Location, models.DO_NOTHING)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=20, null=True)

    @staticmethod
    def from_stock(stock: Stock):
        return CheckedOutStock(
            part_number=stock.part_number,
            location=stock.location,
            quantity=stock.quantity,
            comment=stock.comment,
        )

    def __str__(self):
        return f"CheckedOutStock {self.checked_out_id} - {self.part_number}. Quantity: {self.quantity}"


class BomChecklist(models.Model):
    part_number = models.OneToOneField('Catalogue', models.CASCADE, db_column='part_number')
    quantity_remaining = models.PositiveIntegerField()
    bom = models.ForeignKey(Bom, models.CASCADE)

    def __str__(self):
        return f"P/N: {self.part_number} - Quantity Remaining: {self.quantity_remaining}"
