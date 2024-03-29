insert into app_project (project_name)
values ('J&J 1'),
       ('Teagasc 1'),
       ('Danone 3');

insert into app_location (location_name)
values ('Loc-01-01'),
       ('Loc-01-02'),
       ('Loc-01-03'),
       ('Loc-01-04');

insert into app_catalogue (part_number, brand, category, description, vendor_description, purchase_unit_cost_eur,
                           sale_unit_cost_eur, notes)
values ('1042033', 'Sick', 'Photoelectric sensors', 'Photoelectric proximity sensor', 'Photoelectric proximity sensor. Type: W4S-3. Sensing range 4mm - 180mm. PinPoint LED. PNP. M8, 4-pin. Adjustment: I/O Link with single teach-in button.
WTB4SC-3P2262A00', 122.40, 174.86, 'Upgraded I/O Link version used for Teleflex Mexico & Limerick'),
       ('1050710', 'Sick', 'Photoelectric sensors', 'Photoelectric proximity sensor',
        'Photoelectric proximity sensor. Type: GTE6-P4211. Sensing range <250mm. PinPoint LED. PNP. M8, 4-pin. Adjustment: Mechanical spindle. ',
        48, 69,
        'Sensors used on original Pouch Detection. Sensitivity could be adjusted by operators and was therefore upgraded to I/O Link version.');

insert into app_bom (name)
values ('Danone Filtration System'),
       ('J&J Assembly Line');

insert into app_bomitems (quantity, bom_id, part_number)
values (1, 1, '1042033'),
       (3, 2, '1050710');

insert into app_stock (quantity, comment, location_id, part_number, project_id, check_out)
values (3, 'Ships out 2024-01-01', 2, '1042033', 3, 'x');