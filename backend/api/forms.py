from django import forms


class MarkupRequestForm(forms.Form):
    key = forms.CharField(max_length=255)


class RecordFilterForm(forms.Form):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    status = forms.ChoiceField(
        choices=[('matched', 'Matched'), ('unmatched', 'Unmatched')],
        required=False
    )