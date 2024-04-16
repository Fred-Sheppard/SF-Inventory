from django.urls import path

from . import views

urlpatterns = [
    path('', views.default, name='default'),
    path('index', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('accounts/login/', views.login),
    path('logout/', views.logout, name='logout'),
    path('stock', views.stock, name='stock'),
    path('checkout_stock/<int:stock_id>', views.checkout_stock, name='checkout_stock'),
    path('catalogue', views.catalogue, name='catalogue'),
    path('catalogue/new', views.catalogue_new, name='catalogue_new'),
    path('catalogue/<str:part_number>', views.catalogue_entry, name='catalogue_entry'),
    path('catalogue/edit/<str:part_number>', views.catalogue_edit, name='catalogue_edit'),
    path('bom/<int:bom_id>', views.bom, name='bom'),
    path('bom/new', views.bom_new, name='bom_new'),
    path('bom/edit/<int:bom_id>', views.bom_edit, name='bom_edit'),
    path('generate_bom_checklist/<int:bom_id>', views.generate_bom_checklist, name='generate_bom_checklist'),
    path('location/new', views.location_new, name='location_new'),
    path('location/<int:loc_id>', views.location, name='location'),
    path('project/new', views.project_new, name='project_new'),
    path('project/<int:project_id>', views.project, name='project'),
    path('brand/<int:brand_id>', views.brand, name='brand'),
]
