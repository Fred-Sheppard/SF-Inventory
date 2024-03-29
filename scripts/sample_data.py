from app.models import *

# Projects
project1 = Project.objects.create(project_name="J&J 1")
project2 = Project.objects.create(project_name="Teagasc 1")
project3 = Project.objects.create(project_name="Danone 3")

# Locations
location1 = Location.objects.create(location_name="Loc-01-01")
location2 = Location.objects.create(location_name="Loc-01-02")
location3 = Location.objects.create(location_name="Loc-01-03")
location4 = Location.objects.create(location_name="Loc-01-04")

# Catalogue
catalogue1 = Catalogue.objects.create(
    part_number="1042033",
    brand="Sick",
    category="Photoelectric sensors",
    description="Photoelectric proximity sensor",
    vendor_description="""Photoelectric proximity sensor. Type: W4S-3. Sensing range 4mm - 180mm. PinPoint LED. PNP. M8, 4-pin. Adjustment: I/O Link with single teach-in button.
WTB4SC-3P2262A00""",
    purchase_unit_cost_eur=122.40,
    sale_unit_cost_eur=174.86,
    notes="Upgraded I/O Link version used for Teleflex Mexico & Limerick",
)
catalogue2 = Catalogue.objects.create(
    part_number="1050710",
    brand="Sick",
    category="Photoelectric sensors",
    description="Photoelectric proximity sensor",
    vendor_description="""Photoelectric proximity sensor. Type: GTE6-P4211. Sensing range <250mm. PinPoint LED. PNP. M8, 4-pin. Adjustment: Mechanical spindle. """,
    purchase_unit_cost_eur=48,
    sale_unit_cost_eur=69,
    notes="Sensors used on original Pouch Detection. Sensitivity could be adjusted by operators and was therefore upgraded to I/O Link version.",
)

# Bom (Bill of Materials)
bom1 = Bom.objects.create(name="Danone Filtration System")
bom2 = Bom.objects.create(name="J&J Assembly Line")

# BomItems (Bill of Materials Items)
BomItems.objects.create(quantity=1, bom=bom1, part_number=catalogue1)
BomItems.objects.create(quantity=3, bom=bom2, part_number=catalogue2)

# Stock
Stock.objects.create(quantity=3, comment="Ships out 2024-01-01", location_id=1, part_number=catalogue1,
                     project_id=1)
