from django.shortcuts import render
from .forms import csv_form, column_select_form, axis_select_form
from .models import CSVmodel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3
import os


def index(request) :
    csvform = csv_form()
    session_keys = list(request.session.keys())
    print(session_keys)
    for id in session_keys:
        del request.session[id]
    return render(request, "index.html", context= {"csvform" : csvform})

# Create your views here.
def upload_csv(request):
    csvform = csv_form(request.POST, request.FILES)
    context = {
            "csvform" : csvform
        }
    if request.method == "POST": 
        if request.FILES.get('Input_csv_file', False) :
            CSV = CSVmodel(csv=request.FILES['Input_csv_file'])
            CSV.save()
            df = pd.read_csv(CSV.csv.path)
            top10 = df.head(10).to_html()
            num_df = df.select_dtypes(include=np.number)
            num_cols = list(num_df.columns)
            os.remove(CSV.csv.path)
            CSV.delete()

            request.session['uploaded'] = True
            request.session['df'] = df.to_dict()
            request.session['num_cols'] = num_cols

            column_form = column_select_form(columns=num_cols)
            axis_select = axis_select_form(columns=num_cols)

            context = {
                "csvform" : csvform,
                "column_form" : column_form,
                "top10" : top10,
                "uploaded" : request.session['uploaded'],
                "axis_select"  : axis_select,
            }

    return render(request, "index.html", context= context)


def calculate_stats(request): 
    csvform = csv_form(request.POST, request.FILES)
    if request.method == "POST":
        column_form = column_select_form(request.POST, columns=request.session.get('num_cols',[]))
        axis_select = axis_select_form(columns=request.session.get('num_cols',[]), initial_choices=request.session.get("plotted_columns_types", []))

        stat_cols = []
        if column_form.is_valid() : 
            stat_cols = column_form.cleaned_data['columns']

        df = pd.DataFrame(request.session['df'])
        top10 = df.head(10).to_html()
        num_df = df.select_dtypes(include=np.number)
        
        stats_dict = {}

        for col in stat_cols :
            stats_dict[col] = {
                "Mean" : round(float(num_df[col].mean()),2),
                "Median": round(float(num_df[col].median()), 2),
                "Standard Deviation": round(float(num_df[col].std()), 2),
                "Missing Value Count": int(num_df[col].isna().sum()),
                "Max value": round(float(num_df[col].max()), 2), 
                "Min value": round(float(num_df[col].min()), 2),
                "Unique value count": int(num_df[col].unique().__len__()),
            }

        request.session['stats_dict'] = stats_dict
        request.session['selected_columns'] = stat_cols

        context = {
                "csvform" : csvform,
                "column_form" : column_form,
                "top10" : top10,
                "stats_dict" : stats_dict,
                "uploaded" : request.session['uploaded'],
                "axis_select" : axis_select,
                "plot" : request.session.get("plot_html", None)
            }
    else :
        context = {
            "csvform" : csvform
        }
    
    return render(request, "index.html", context= context)

def generate_plots(request):
    csvform = csv_form(request.POST, request.FILES)

    if request.method == "POST":
        column_form = column_select_form(columns = request.session.get('num_cols',[]), initial_choices=request.session.get('selected_columns', []))
        axis_select = axis_select_form(request.POST, columns=request.session.get('num_cols',[]))

        df = pd.DataFrame(request.session['df'])
        top10 = df.head(10).to_html()
        #x_col, y_col, plot_type = request.POST['column_x'], request.POST['column_y'], request.POST['plot_type']
        x_col, plot_type = request.POST['column_x'], request.POST['plot_type']
        print(x_col)

        # if not x_col == y_col :
        #     fig = plt.figure()
        #     ax = fig.add_subplot()
        #     df.plot(x=x_col, y=y_col, ax=ax, kind=plot_type)
        #     html = mpld3.fig_to_html(fig)
        # else :
        #     html = "Column names can not be same"

        fig = plt.figure(figsize=(12, 10))
        plt.rcParams['font.size'] = 22

        if plot_type == "hist" :
            plt.hist(df[x_col])

        elif plot_type == "box" :
            plt.boxplot(df[x_col])

        else :

            bins = pd.cut(df[x_col], bins=min(len(df[x_col].unique()), 4))
            bin_counts = bins.value_counts().sort_index()

            bin_labels = [f'{round(interval.left, 2)} - {round(interval.right, 2)}' for interval in bin_counts.index]

            bin_counts_list = bin_counts.tolist()

            wedges, texts = plt.pie(bin_counts_list, startangle=90, shadow=True, explode=[0.1]*len(bin_counts_list))

            total = sum(bin_counts_list)
            legend_labels = [f'{label}: {count} ({count/total:.1%})' for label, count in zip(bin_labels, bin_counts_list)]

            plt.legend(wedges, legend_labels, title="Ranges", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            # Set the title
            plt.title(f"Pie plot for \"{x_col}\"")

            plt.tight_layout()

        html = mpld3.fig_to_html(fig, figid='plot')

        #request.session['plotted_columns_types'] = [x_col, y_col, plot_type]
        request.session['plotted_columns_types'] = [x_col, plot_type]
        request.session['plot_html'] = html

        context = {
            "csvform" : csvform,
            "column_form" : column_form,
            "top10" : top10,
            "stats_dict" : request.session.get('stats_dict', []),
            "uploaded" : request.session['uploaded'],
            "axis_select" : axis_select,
            "plot" : html,
        }
        
    else:
        context = {
            "csvform" : csvform
        }

    return render(request, "index.html", context= context)

        



