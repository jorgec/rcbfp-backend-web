from django import forms
from incidents.models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'