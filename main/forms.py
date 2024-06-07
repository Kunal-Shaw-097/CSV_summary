from django import forms

class CSVform(forms.Form):
    Input_csv_file = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))
 