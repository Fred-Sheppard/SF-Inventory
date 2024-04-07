import django_tables2 as tables
from django.db.models import Sum
from django_tables2 import Column
from django_tables2.utils import Accessor

from .models import Catalogue, BomItems, Stock, BomChecklist


class BomItemsTable(tables.Table):
    class Meta:
        model = BomItems
        fields = ['id', 'part_number', 'quantity']


class TotalQuantityColumn(Column):
    def render(self, record):
        total_quantity = Stock.objects.filter(part_number=record.part_number).aggregate(total_quantity=Sum('quantity'))[
                             'total_quantity'] or 0
        return total_quantity


class BomChecklistTable(tables.Table):
    part_number = tables.Column(linkify={"viewname": "catalogue_entry", "args": [Accessor("part_number")]})
    quantity_in_stock = TotalQuantityColumn(accessor='part_number', verbose_name='In Stock')

    class Meta:
        model = BomChecklist
        fields = ['part_number', 'quantity_remaining']


class CatalogueTable(tables.Table):
    part_number = tables.Column(linkify={"viewname": "catalogue_entry", "args": [Accessor("part_number")]})
    brand = tables.Column(linkify={"viewname": "brand", "args": [Accessor("brand")]})

    class Meta:
        model = Catalogue
        exclude = ['image', 'last_modified', 'modified_by', 'url']


class StockTable(tables.Table):
    part_number = tables.Column(linkify={"viewname": "catalogue_entry", "args": [Accessor("part_number")]})
    location = tables.Column(linkify={"viewname": "location", "args": [Accessor("location__id")]})
    project = tables.Column(linkify={"viewname": "project", "args": [Accessor("project__id")]})
    check_out = tables.Column(linkify={"viewname": "checkout_stock", "args": [Accessor("stock_id")]})

    class Meta:
        model = Stock
        exclude = ['image']
        sequence = ('...', 'check_out')
