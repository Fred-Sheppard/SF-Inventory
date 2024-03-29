from django import forms

from app.models import Stock, Catalogue, BomItems, Project, Location, Bom, BomChecklist


class Util:
    @staticmethod
    def clean_part_number(part_number: str):
        # Account for Siemens part barcodes
        if part_number.startswith('1p'):
            part_number = part_number[2:]
            print(part_number)
        try:
            entry = Catalogue.objects.get(part_number=part_number)
        except Catalogue.DoesNotExist:
            raise forms.ValidationError('Part number not found in catalogue')
        return entry


class StockForm(forms.ModelForm):
    part_number = forms.CharField()

    def clean_part_number(self):
        return Util.clean_part_number(self.cleaned_data['part_number'])

    class Meta:
        model = Stock
        exclude = []


class StockFilterForm(forms.Form):
    part_number = forms.ModelChoiceField(queryset=Catalogue.objects.filter(stock__isnull=False).distinct('pk'),
                                         required=False)
    location = forms.ModelChoiceField(queryset=Location.objects.filter(stock__isnull=False).distinct('pk'),
                                      required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.filter(stock__isnull=False).distinct('pk'),
                                     required=False)


class CatalogueForm(forms.ModelForm):
    def clean_part_number(self):
        return self.cleaned_data['part_number'][2:]

    class Meta:
        model = Catalogue
        exclude = []


class BomItemsForm(forms.ModelForm):
    part_number = forms.CharField(label='Part Number')

    def clean_part_number(self):
        return Util.clean_part_number(self.cleaned_data['part_number'])

    class Meta:
        model = BomItems
        fields = ['id', 'part_number', 'quantity']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['id', 'project_name']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['id', 'location_name']


class BomForm(forms.ModelForm):
    class Meta:
        model = Bom
        fields = ['bom_id', 'name']


class BomChecklistForm(forms.Form):
    part_number = forms.CharField()
    bom_id = forms.HiddenInput()

    def __init__(self, *args, **kwargs):
        self.bom_id = kwargs.pop('bom_id', None)
        super(BomChecklistForm, self).__init__(*args, **kwargs)

    def clean_part_number(self):
        part_number = self.cleaned_data['part_number']
        if not BomChecklist.objects.filter(bom_id=self.bom_id, part_number=part_number).exists():
            raise forms.ValidationError('Part number not found in BOM')
        quantity_remaining = BomChecklist.objects.get(bom_id=self.bom_id, part_number=part_number).quantity_remaining
        if quantity_remaining <= 0:
            raise forms.ValidationError('All required items of this P/N have already been scanned')
        return part_number
