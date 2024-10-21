from django import forms
from .models import Attendee


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['name', 'email', 'phone', 'company']

    def clean_email(self):
        # Remove this function to skip the check for existing email addresses
        return self.cleaned_data['email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add Bootstrap class

from .models import NameTagTemplate

class NameTagTemplateForm(forms.ModelForm):
    class Meta:
        model = NameTagTemplate
        fields = ['template']  # Specify the template field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add Bootstrap class