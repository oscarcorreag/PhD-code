from django import forms


class CoordsForm(forms.Form):
    top = forms.FloatField(required=True)
    left = forms.FloatField(required=True)
    bottom = forms.FloatField(required=True)
    right = forms.FloatField(required=True)
