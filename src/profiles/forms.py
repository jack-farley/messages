from django import forms

from .models import Profile


class AdminProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'birthdate',
        ]
