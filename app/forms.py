from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.validators import MinValueValidator, ValidationError
from django.utils.text import slugify

from app.models import Stock, Catalogue, BomItems, Project, Location, Bom, BomChecklist


class Util:
    @staticmethod
    def clean_part_number(part_number: str):
        # Account for Siemens barcodes
        if part_number.startswith('1p'):
            part_number = part_number[2:]
        try:
            entry = Catalogue.objects.get(part_number=part_number)
        except Catalogue.DoesNotExist:
            raise forms.ValidationError('Part number not found in catalogue')
        return entry


class BomChecklistForm(forms.Form):
    part_number = forms.CharField()
    bom_id = forms.HiddenInput()

    def __init__(self, *args, **kwargs):
        self.bom_id = kwargs.pop('bom_id', None)
        if not self.bom_id:
            raise ValueError("bom_id must be supplied")
        super(BomChecklistForm, self).__init__(*args, **kwargs)

    def clean_part_number(self):
        part_number = self.cleaned_data['part_number']
        if not BomChecklist.objects.filter(bom_id=self.bom_id, part_number=part_number).exists():
            raise forms.ValidationError('Part number not found in BOM')
        quantity_remaining = BomChecklist.objects.get(bom_id=self.bom_id, part_number=part_number).quantity_remaining
        if quantity_remaining <= 0:
            raise forms.ValidationError('All required items of this P/N have already been scanned')
        return part_number


class BomForm(forms.ModelForm):
    class Meta:
        model = Bom
        fields = ['bom_id', 'name']


class BomItemsForm(forms.ModelForm):
    part_number = forms.CharField(label='Part Number')

    def __init__(self, *args, bom_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.bom_id = bom_id

    def clean_part_number(self):
        pn = Util.clean_part_number(self.cleaned_data['part_number'])
        return pn

    def save(self, commit=True):
        instance = super(BomItemsForm, self).save(commit=False)
        instance.bom_id = self.bom_id
        if commit:
            instance.save()
        return instance

    class Meta:
        model = BomItems
        fields = ['id', 'part_number', 'quantity']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Part Number already exists in BOM."
            }
        }


class BomItemsFormset(forms.BaseInlineFormSet):
    def clean(self):
        super(BomItemsFormset, self).clean()
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        part_numbers = set()
        for form in self.forms:
            # noinspection PyUnresolvedReferences
            if self.can_delete and self._should_delete_form(form):
                continue
            try:
                part_number = form.cleaned_data['part_number']
            except KeyError:
                continue
            if part_number in part_numbers:
                raise ValidationError(f"Part Number already exists in BOM: {part_number}")
            part_numbers.add(part_number)


class CatalogueEditForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        exclude = ['part_number', 'modified_by', 'image']


class CatalogueForm(forms.ModelForm):
    def clean_part_number(self):
        part_number = self.cleaned_data['part_number']
        # Remove the leading 1p for Siemens barcodes
        if part_number.startswith('1p'):
            part_number = part_number[2:]
        return part_number

    def clean_brand(self):
        brand = self.cleaned_data['brand']
        return slugify(brand)

    class Meta:
        model = Catalogue
        exclude = ['modified_by', 'image']


class CheckoutForm(forms.Form):
    quantity = forms.IntegerField(initial=1, required=True, validators=[MinValueValidator(1)])


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['id', 'location_name']


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['id', 'project_name']


class StockFilterForm(forms.Form):
    part_number = forms.ModelChoiceField(queryset=Catalogue.objects.filter(stock__isnull=False).distinct('pk'),
                                         required=False)
    location = forms.ModelChoiceField(queryset=Location.objects.filter(stock__isnull=False).distinct('pk'),
                                      required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.filter(stock__isnull=False).distinct('pk'),
                                     required=False)


class StockForm(forms.ModelForm):
    part_number = forms.CharField()
    quantity = forms.IntegerField(initial=1, required=True, validators=[MinValueValidator(1)])

    def clean_part_number(self):
        return Util.clean_part_number(self.cleaned_data['part_number'])

    class Meta:
        model = Stock
        exclude = ['modified_by']


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
