from django import forms

class csv_form(forms.Form):
    Input_csv_file = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))


class column_select_form(forms.Form):
    columns = forms.MultipleChoiceField(label="Select Column to generate stats", choices=[], widget=forms.CheckboxSelectMultiple, required=False)
    
    def __init__(self, *args, **kwargs):
        column_names = kwargs.pop('columns', [])
        initial_choices = kwargs.pop('initial_choices', [])
        super(column_select_form, self).__init__(*args, **kwargs)
        self.fields['columns'].choices = [(col, col) for col in column_names]
        if initial_choices : 
            self.fields['columns'].initial = initial_choices


plot_choices = [
   # ("line", "Line Plot"),
   # ("bar" , "Vertical Bar Plot"),
   # ("barh", "Horizontal Bar Plot"),
    ("hist", "Histogram"),
    ("box" , "Boxplot"),
   # ("kde" , "Kernal Density Estimation Plot"),
   # ("area", "Area Plot"),
    ("pie" , "Pie Plot"),
   # ("scatter", "Scatter Plot"),
]

class axis_select_form(forms.Form):
    column_x = forms.ChoiceField(label='Select Column to generate plot', choices=[])
   #column_y = forms.ChoiceField(label='Select Y-axis Column to generate stats', choices=[])
    plot_type = forms.ChoiceField(label='Select the type of plot', choices=plot_choices)
    
    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        initial_choices = kwargs.pop('initial_choices', [])
        super(axis_select_form, self).__init__(*args, **kwargs)
        self.fields['column_x'].choices = [(col, col) for col in columns]
        #self.fields['column_y'].choices = [(col, col) for col in columns]
        if initial_choices: 
            self.fields['column_x'].initial = [initial_choices[0]]
            #self.fields['column_y'].initial = [initial_choices[1]]
            self.fields['plot_type'].initial = [initial_choices[1]]


imputation_choices = [
    ("mean", "Mean Imputation"),
    ("median", "Median Imputation"),
    ("mode", "Mode Imputation"),
]

class missing_values_form(forms.Form):
    missing_value_strat = forms.ChoiceField(label='Select Imputation method', choices=imputation_choices)

