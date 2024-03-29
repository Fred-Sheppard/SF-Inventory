from django.db.models import Q, QuerySet
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls.base import reverse_lazy

from app.forms import StockForm, CatalogueForm, BomItemsForm, ProjectForm, LocationForm, BomForm, BomChecklistForm, \
    StockFilterForm
from app.models import Stock, Catalogue, Bom, BomItems, Location, Project, BomChecklist, CheckedOutStock
from app.tables import CatalogueTable, StockTable, BomItemsTable, BomChecklistTable


class Util:
    @staticmethod
    def form_page(request, form_type, redirect_to, context=None):
        if context is None:
            context = {}
        if request.method == 'POST':
            form = form_type(request.POST)
            if form.is_valid():
                form.save()
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


def index(request):
    boms = Bom.objects.all()
    projects = Project.objects.all()
    locations = Location.objects.all()
    return render(request, 'index.html', {'boms': boms, 'projects': projects, 'locations': locations})


def handle_stock_form(request, form):
    """Deal with the post request of the stock input form.
    The form must be valid."""
    try:
        entry = Stock.objects.get(
            part_number=form.cleaned_data['part_number'],
            location=form.cleaned_data['location'],
            project=form.cleaned_data['project']
        )
        entry.quantity += form.cleaned_data['quantity']
    except Stock.DoesNotExist:
        entry = form.save(commit=False)
    entry.save()


def handle_stock_filter(request, form):
    """Deal with the post request of the stock filter form.
    The form must be valid."""

    part_number = form.cleaned_data['part_number']
    location_ = Location.objects.filter(location_name=form.cleaned_data['location']).first()
    project_ = Project.objects.filter(project_name=form.cleaned_data['project']).first()
    url = reverse_lazy('stock') + '?'
    if part_number is not None:
        url += f'part_number={part_number}&'
    if location_:
        url += f'location={location_.id}&'
    if project_:
        url += f'project={project_.id}&'
    # Remove the final &
    return url[:-1]


def filter_stock_from_parameters(request) -> QuerySet:
    part_number_ = request.GET.get('part_number')
    location_ = request.GET.get('location')
    project_ = request.GET.get('project')
    query = Q()
    if part_number_:
        query &= Q(part_number=part_number_)
    if location_:
        query &= Q(location=location_)
    if project_:
        query &= Q(project=project_)
    return Stock.objects.filter(query).all()


def stock(request):
    if request.method == 'POST':
        if 'submit-stock' in request.POST:
            form = StockForm(request.POST)
            if form.is_valid():
                handle_stock_form(request, form)
                return redirect(stock)
        elif 'submit-filter' in request.POST:
            form = StockFilterForm(request.POST)
            if form.is_valid():
                url = handle_stock_filter(request, form)
                return redirect(url)
        else:
            raise ValueError('Invalid button name that called this post request')
    else:
        form = StockForm()
        filter_form = StockFilterForm()
    # If the form being posted is not valid, it will fall through here to display errors
    stock_list = filter_stock_from_parameters(request)
    table = StockTable(stock_list)
    catalogue_list = Catalogue.objects.all()
    checked_out = CheckedOutStock.objects.all()
    return render(request, 'stock.html', {'form': form, 'table': table, 'catalogue': catalogue_list,
                                          'checked_out': checked_out, 'filter_form': filter_form})


def delete_stock(request, part_number):
    stock_entry = get_object_or_404(Stock, part_number=part_number)
    checked_out = CheckedOutStock.from_stock(stock_entry)
    checked_out.save()
    stock_entry.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def catalogue(request):
    context = {
        'table': CatalogueTable(Catalogue.objects.all()),
        'button_url': '/catalogue/new',
        'button_text': 'New Item'
    }
    return render(request, 'table.html', context)


def catalogue_new(request):
    context = {
        'heading': 'New Entry',
        'button_url': '/catalogue',
        'button_text': 'Back to Catalogue'
    }
    return Util.form_page(request, CatalogueForm, catalogue_new, context)


def catalogue_entry(request, part_number):
    item = get_object_or_404(Catalogue, pk=part_number)
    entries = StockTable(Stock.objects.filter(part_number=item))
    context = {
        'table': CatalogueTable([item]),
        'entries': entries,
        'heading': f'{item}',
        'button_url': f'/catalogue/edit/{item.part_number}',
        'button_text': 'Edit'
    }
    return render(request, 'catalogue_entry.html', context)


def catalogue_edit(request, part_number):
    catalogue_item = get_object_or_404(Catalogue, pk=part_number)

    if request.method == 'POST':
        form = CatalogueForm(request.POST, instance=catalogue_item)
        if form.is_valid():
            form.save()
            return redirect(catalogue)
    else:
        form = CatalogueForm(instance=catalogue_item)

    context = {
        'form': form,
        'heading': f'Editing {catalogue_item.part_number}',
        'button_url': f'/catalogue/{catalogue_item.part_number}',
        'button_text': 'View Item'
    }
    return render(request, 'form.html', context)


def bom_edit(request, bom_id=None):
    # TODO fix
    boms = Bom.objects.all()
    if bom_id is None:
        return render(request, 'bom_default.html', {'boms': boms})
    bom_ = get_object_or_404(Bom, bom_id=bom_id)
    # noinspection PyPep8Naming
    BomItemsFormSet = inlineformset_factory(Bom, BomItems, form=BomItemsForm, extra=1)
    if request.method == 'POST':
        formset = BomItemsFormSet(request.POST, instance=bom_)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.bom_id = bom_id
                instance.save()
            for deleted in formset.deleted_objects:
                BomItems.delete(deleted)
            return redirect(bom_edit, bom_id)
    else:
        formset = BomItemsFormSet(instance=bom_)
    labels = ['Part Number', 'Quantity']
    return render(request, 'bom_edit.html', {'boms': boms, 'my_bom': bom_, 'formset': formset, 'labels': labels})


def location(request, loc_id):
    loc = get_object_or_404(Location, id=loc_id)
    table = StockTable(Stock.objects.filter(location=loc).all())
    return render(request, 'table.html', {'table': table, 'heading': loc.location_name})


def project(request, project_id):
    project_ = get_object_or_404(Project, id=project_id)
    table = StockTable(Stock.objects.filter(project=project_).all())
    return render(request, 'table.html', {'table': table, 'heading': project_.project_name})


def project_new(request):
    context = {
        'heading': 'New Project',
        'button_url': '/index',
        'button_text': 'View all Projects',
    }
    return Util.form_page(request, ProjectForm, project_new, context)


def location_new(request):
    context = {
        'heading': 'New Location',
        'button_url': '/index',
        'button_text': 'View all Locations',
    }
    return Util.form_page(request, LocationForm, location_new, context)


def bom_new(request):
    context = {
        'heading': 'New Bom',
        'button_url': '/index',
        'button_text': 'View all Boms',
    }
    return Util.form_page(request, BomForm, bom_new, context)


def generate_bom_checklist(request, bom_id):
    Util.generate_bom_checklist(bom_id)
    return redirect(request.META.get('HTTP_REFERER'))


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
