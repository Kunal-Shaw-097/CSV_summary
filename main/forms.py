from django import forms

class CSVform(forms.Form):
    Input_csv_file = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))


class ColumnSelectForm(forms.Form):
    column = forms.ChoiceField(label='Select Column', choices=[])
    
    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        initial_choice = kwargs.pop('initial_choice', [])
        super(ColumnSelectForm, self).__init__(*args, **kwargs)
        self.fields['column'].choices = [(col, col) for col in columns]
        if initial_choice : 
            self.fields['column'].initial = initial_choice
