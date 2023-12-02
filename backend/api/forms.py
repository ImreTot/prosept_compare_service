from django import forms


class MarkupRequestForm(forms.Form):
    key = forms.CharField(max_length=255)