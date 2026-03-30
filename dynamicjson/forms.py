from django import forms


class DynamicNamesForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "name"}),
    )

