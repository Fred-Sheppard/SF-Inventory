import django.contrib.auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, QuerySet
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls.base import reverse_lazy, reverse

from app.forms import StockForm, CatalogueForm, BomItemsForm, LocationForm, BomForm, BomChecklistForm, \
    StockFilterForm, CatalogueEditForm, UserCreateForm, CheckoutForm, BomItemsFormset
from app.models import Stock, Catalogue, Bom, BomItems, Location, BomChecklist, CheckedOutStock, Brand
from app.tables import CatalogueTable, StockTable, BomItemsTable, BomChecklistTable


class Util:
    @staticmethod
    def save_with_user(request, form):
        instance = form.save(commit=False)
        instance.modified_by = request.user.username
        instance.created_by = request.user.username
        instance.save()

    @staticmethod
    def form_page(request, form_type, redirect_to, context=None):
        if context is None:
            context = {}
        if request.method == 'POST':
            form = form_type(request.POST)
            if form.is_valid():
                Util.save_with_user(request, form)
                return redirect(redirect_to)
        else:
            form = form_type()
        context = context | {'form': form}
        return render(request, 'form.html', context)

    @staticmethod
    def generate_bom_checklist(bom_id):
        items = BomItems.objects.filter(bom_id=bom_id).all()
        BomChecklist.objects.filter(bom_id=bom_id).delete()
        for item in items:
            BomChecklist(bom=item.bom, part_number=item.part_number, quantity_remaining=item.quantity).save()


def register(request):
    context = {
        'heading': 'Register a new account',
        'button_text': 'Login',
        'button_url': '/accounts/login/'
    }
    return Util.form_page(request, UserCreateForm, default, context)


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                django.contrib.auth.login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return redirect(default)
    else:
        form = AuthenticationForm()
    context = {
        'heading': 'Login',
        'button_text': 'Register',
        'button_url': '/register',
        'form': form,
    }
    return render(request, 'form.html', context)


@login_required
def logout(request):
    django.contrib.auth.logout(request)
    return redirect(login)


@login_required
def default(request):
    return redirect(stock)


@login_required
def index(request):
    boms = Bom.objects.all().order_by('name')
    locations = Location.objects.all().order_by('location_name')
    return render(request, 'index.html', {'boms': boms, 'locations': locations})


@login_required
def handle_stock_form(request, form):
    """Deal with the post request of the stock input form.
    The form must be valid."""
    try:
        entry = Stock.objects.get(
            part_number=form.cleaned_data['part_number'],
            location=form.cleaned_data['location'],
        )
        entry.quantity += form.cleaned_data['quantity']
    except Stock.DoesNotExist:
        entry = form.save(commit=False)
    entry.modified_by = request.user.username
    entry.save()


@login_required
def handle_stock_filter(request, form) -> str:
    """Deal with the post request of the stock filter form.
    The form must be valid.
    Returns the filter url"""

    part_number = form.cleaned_data['part_number']
    location_ = Location.objects.filter(location_name=form.cleaned_data['location']).first()
    url = reverse_lazy('stock') + '?'
    if part_number is not None:
        url += f'part_number={part_number}&'
    if location_:
        url += f'location={location_.id}&'
    # Remove the final &
    return url[:-1]


@login_required
def filter_stock_from_parameters(request) -> QuerySet:
    part_number_ = request.GET.get('part_number')
    location_ = request.GET.get('location')
    query = Q()
    if part_number_:
        query &= Q(part_number=part_number_)
    if location_:
        query &= Q(location=location_)
    return Stock.objects.filter(query).all()


@login_required
def stock(request):
    if request.method == 'POST':
        if 'submit-stock' in request.POST:
            form = StockForm(request.POST)
            filter_form = StockFilterForm()
            if form.is_valid():
                handle_stock_form(request, form)
                return redirect(stock)
        elif 'submit-filter' in request.POST:
            filter_form = StockFilterForm(request.POST)
            form = StockForm()
            if filter_form.is_valid():
                url = handle_stock_filter(request, filter_form)
                return redirect(url)
        else:
            raise ValueError('Invalid button name that called this post request')
    else:
        part_number = request.GET.get('initial_pn')
        form = StockForm(initial={'part_number': part_number})
        filter_form = StockFilterForm()
    # If the form being posted is not valid, it will fall through here to display errors
    stock_list = filter_stock_from_parameters(request)
    context = {
        'form': form,
        'filter_form': filter_form,
        'table': StockTable(stock_list),
        'catalogue': Catalogue.objects.all(),
        'checked_out': CheckedOutStock.objects.all().order_by('checked_out_id').reverse()
    }
    return render(request, 'stock.html', context)


@login_required
def checkout_stock(request, stock_id):
    entry = get_object_or_404(Stock, stock_id=stock_id)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            checked_out = CheckedOutStock.from_stock(entry)
            if quantity >= entry.quantity:
                entry.delete()
            else:
                entry.quantity -= quantity
                entry.save()
                checked_out.quantity = quantity
            checked_out.modified_by = request.user.username
            checked_out.save()
            return redirect(stock)
    else:
        form = CheckoutForm()
    table = StockTable([entry], exclude=['check_out'])
    return render(request, 'checkout.html', {'entry': entry, 'table': table, 'form': form})


@login_required
def delete_stock(request, stock_id):
    stock_entry = get_object_or_404(Stock, stock_id=stock_id)
    checked_out = CheckedOutStock.from_stock(stock_entry)
    checked_out.save()
    stock_entry.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def catalogue(request):
    table = CatalogueTable(Catalogue.objects.all(), order_by=('brand', 'part_number')),
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    context = {
        'table': table,
        # 'table': CatalogueTable(Catalogue.objects.all(), order_by=('brand', 'part_number')),
        'button_url': '/catalogue/new',
        'button_text': 'New Item',
        'heading': 'Catalogue',
    }
    return render(request, 'table.html', context)


@login_required
def catalogue_new(request):
    if request.method == 'POST':
        form = CatalogueForm(request.POST, )
        if form.is_valid():
            Util.save_with_user(request, form)
            if form.cleaned_data['scanToStock']:
                part_number = form.cleaned_data['part_number']
                url = f"{reverse('stock')}?initial_pn={part_number}"
                return HttpResponseRedirect(url)
            else:
                return redirect(catalogue_new)
    else:
        part_number = request.GET.get('part_number')
        form = CatalogueForm(initial={'part_number': part_number})
    context = {
        'heading': 'New Entry',
        'button_url': '/catalogue',
        'button_text': 'Back to Catalogue',
        'form': form
    }
    return render(request, 'form.html', context)


@login_required
def catalogue_entry(request, part_number):
    entry = get_object_or_404(Catalogue, pk=part_number)
    entries = StockTable(Stock.objects.filter(part_number=entry))
    context = {
        'table': CatalogueTable([entry]),
        'entries': entries,
        'heading': f'{entry}',
        'button_url': f'/catalogue/edit/{entry.part_number}',
        'button_text': 'Edit',
        'entry': entry
    }
    return render(request, 'catalogue_entry.html', context)


@login_required
def catalogue_edit(request, part_number):
    catalogue_item = get_object_or_404(Catalogue, pk=part_number)

    if request.method == 'POST':
        form = CatalogueEditForm(request.POST, instance=catalogue_item)
        if form.is_valid():
            Util.save_with_user(request, form)
            return redirect(catalogue_entry, part_number)
    else:
        form = CatalogueEditForm(instance=catalogue_item)

    context = {
        'form': form,
        'heading': f'Editing {catalogue_item.part_number}',
        'button_url': f'/catalogue/{catalogue_item.part_number}',
        'button_text': 'View Item'
    }
    return render(request, 'form.html', context)


@login_required
def location(request, loc_id):
    loc = get_object_or_404(Location, id=loc_id)
    table = StockTable(Stock.objects.filter(location=loc).all())
    return render(request, 'table.html', {'table': table, 'heading': loc.location_name})


@login_required
def brand(request, brand_id):
    brand_ = get_object_or_404(Brand, brand_id=brand_id)
    table = CatalogueTable(Catalogue.objects.filter(brand=brand_).all(), order_by='part_number')
    return render(request, 'table.html', {'table': table, 'heading': brand_.name})


@login_required
def location_new(request):
    context = {
        'heading': 'New Location',
        'button_url': '/index',
        'button_text': 'View all Locations',
    }
    return Util.form_page(request, LocationForm, index, context)


@login_required
def bom_new(request):
    if request.method == 'POST':
        form = BomForm(request.POST)
        if form.is_valid():
            Util.save_with_user(request, form)
            return redirect(bom_edit, Bom.objects.get(name=form.cleaned_data['name']).bom_id)
    else:
        form = BomForm()
    context = {
        'heading': 'New Bom',
        'button_url': '/index',
        'button_text': 'View all Boms',
        'form': form
    }
    return render(request, 'form.html', context)


@login_required
def generate_bom_checklist(request, bom_id):
    Util.generate_bom_checklist(bom_id)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def bom(request, bom_id):
    bom_ = get_object_or_404(Bom, bom_id=bom_id)
    bom_table = BomItemsTable(BomItems.objects.filter(bom=bom_))
    checklist_table = BomChecklistTable(BomChecklist.objects.filter(bom=bom_))
    if request.method == 'POST':
        form = BomChecklistForm(request.POST, bom_id=bom_id)
        if form.is_valid():
            # The part number has been validated to exist
            scanned = BomChecklist.objects.get(part_number=form.cleaned_data['part_number'])
            # The quantity has been validated to be greater than 0
            scanned.quantity_remaining -= 1
            scanned.save()
            return redirect(bom, bom_id)
    else:
        form = BomChecklistForm(bom_id=bom_id)
    context = {
        'form': form,
        'bom': bom_,
        'bom_table': bom_table,
        'checklist_table': checklist_table
    }
    return render(request, 'bom.html', context)


@login_required
def bom_edit(request, bom_id):
    bom_ = get_object_or_404(Bom, bom_id=bom_id)
    boms = Bom.objects.all()
    # noinspection PyPep8Naming
    MyFormSet = inlineformset_factory(Bom, BomItems, form=BomItemsForm, formset=BomItemsFormset, extra=1)
    if request.method == 'POST':
        formset = MyFormSet(request.POST, instance=bom_, form_kwargs={'bom_id': bom_id})
        if formset.is_valid():
            formset.save()
            return redirect(bom_edit, bom_id)
    else:
        formset = MyFormSet(instance=bom_, form_kwargs={'bom_id': bom_id})
        print(formset.as_table())
    labels = ['Part Number', 'Quantity']
    return render(request, 'bom_edit.html', {'boms': boms, 'my_bom': bom_, 'formset': formset, 'labels': labels})
