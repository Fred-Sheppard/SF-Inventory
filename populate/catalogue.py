import csv
import decimal
from decimal import Decimal

from app.models import Catalogue, Brand

Catalogue.objects.all().delete()

with open('populate/catalogue.csv', 'r') as file:
    reader = csv.DictReader(file)
    row: dict
    for row in reader:
        try:
            purchase_cost = Decimal(row['Purchasing Unit Price'].replace(',', ''))
        except decimal.InvalidOperation:
            purchase_cost = None

        try:
            sales_cost = Decimal(row['Sale Unit Price'].replace(',', ''))
        except decimal.InvalidOperation:
            sales_cost = None
        brand_name = row.get('Brand', None)
        brand, _ = Brand.objects.get_or_create(name=brand_name)

        catalogue_object = Catalogue.objects.create(
            part_number=row['Part Number'],
            brand=brand,
            category=row.get('Category', None),
            description=row.get('Common description', None),
            vendor_description=row.get('Vendor Description', None),
            purchase_unit_cost_eur=purchase_cost,
            sale_unit_cost_eur=sales_cost,
            notes=row.get('Notes', None),
            url=row.get('URL', None),
            modified_by=row.get('Created')
        )
