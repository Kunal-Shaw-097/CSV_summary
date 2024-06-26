from django.shortcuts import render
from .forms import csv_form, column_select_form, axis_select_form, missing_values_form
from .models import CSVmodel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3
import os


def index(request) :
    csvform = csv_form()
    session_keys = list(request.session.keys())
    for id in session_keys:
        del request.session[id]
    return render(request, "index.html", context= {"csvform" : csvform})

# Create your views here.
def upload_csv(request):
    csvform = csv_form(request.POST, request.FILES)
    missing_value_form = missing_values_form()
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

            stats_dict = {}
            for col in num_cols :
                stats_dict[col] = {
                    "Mean" : round(float(num_df[col].mean()),2),
                    "Median": round(float(num_df[col].median()), 2),
                    "25th and 75th quantile" : num_df[col].quantile([0.25, 0.75]).to_list(),
                    "Standard Deviation": round(float(num_df[col].std()), 2),
                    "Max value": round(float(num_df[col].max()), 2), 
                    "Min value": round(float(num_df[col].min()), 2),
                    "Unique value count": int(num_df[col].unique().__len__()),
                    "Missing Value Count": int(num_df[col].isna().sum()),
                    "null_val_present" : True if int(num_df[col].isna().sum()) > 0 else False,
                    
                }

            
            request.session['stats_dict'] = stats_dict
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
                "missing_value_form": missing_value_form,
            }

    return render(request, "index.html", context= context)


def calculate_stats(request): 
    csvform = csv_form(request.POST, request.FILES)
    missing_value_form = missing_values_form()
    if request.method == "POST":
        column_form = column_select_form(request.POST, columns=request.session.get('num_cols',[]))
        axis_select = axis_select_form(columns=request.session.get('num_cols',[]), initial_choices=request.session.get("plotted_columns_types", []))

        stat_cols = []
        if column_form.is_valid() : 
            stat_cols = column_form.cleaned_data['columns']

        df = pd.DataFrame(request.session['df'])
        top10 = df.head(10).to_html()

        stats_dict = {}

        for col in stat_cols :
            stats_dict[col] = request.session['stats_dict'][col]

        request.session['selected_columns'] = stat_cols

        context = {
                "csvform" : csvform,
                "column_form" : column_form,
                "top10" : top10,
                "stats_dict" : stats_dict,
                "uploaded" : request.session['uploaded'],
                "axis_select" : axis_select,
                "plot" : request.session.get("plot_html", None),
                "missing_value_form": missing_value_form,
            }
    else :
        context = {
            "csvform" : csvform
        }
    
    return render(request, "index.html", context= context)


def handle_missing_values(request):
    csvform = csv_form(request.POST, request.FILES)
    missing_value_form = missing_values_form()
    if request.method == "POST":
        column_form = column_select_form(columns = request.session.get('num_cols',[]), initial_choices=request.session.get('selected_columns', []))
        axis_select = axis_select_form(columns=request.session.get('num_cols',[]), initial_choices=request.session.get("plotted_columns_types", []))

        df = pd.DataFrame(request.session['df'])
        top10 = df.head(10).to_html()

        imputation_strat = request.POST.get("missing_value_strat", [])
        
        if imputation_strat :
            imputation_col = request.POST['column_name_for_imputation']
            if imputation_strat == "mean":
                df[imputation_col] = df[imputation_col].fillna(df[imputation_col].mean())
            elif imputation_strat == "median":
                df[imputation_col] = df[imputation_col].fillna(df[imputation_col].median())
            else:
                df[imputation_col] = df[imputation_col].fillna(df[imputation_col].mode().dropna().values[0])

            request.session['stats_dict'][imputation_col] = {
                "Mean" : round(float(df[imputation_col].mean()),2),
                "Median": round(float(df[imputation_col].median()), 2),
                "25th and 75th quantile" : df[imputation_col].quantile([0.25, 0.75]).to_list(),
                "Standard Deviation": round(float(df[imputation_col].std()), 2),
                "Max value": round(float(df[imputation_col].max()), 2), 
                "Min value": round(float(df[imputation_col].min()), 2),
                "Unique value count": int(df[imputation_col].unique().__len__()),
                "Missing Value Count": int(df[imputation_col].isna().sum()),
                "null_val_present" : True if int(df[imputation_col].isna().sum()) > 0 else False,
                
            }
            request.session['df'] = df.to_dict()
            request.session.modified = True

        stats_dict = {}

        for col in request.session.get('selected_columns',[]):
            stats_dict[col] = request.session['stats_dict'][col]

        context = {
                "csvform" : csvform,
                "column_form" : column_form,
                "top10" : top10,
                "stats_dict" : stats_dict,
                "uploaded" : request.session['uploaded'],
                "axis_select" : axis_select,
                "plot" : request.session.get("plot_html", None),
                "missing_value_form": missing_value_form,
            }
    else :
        context = {
            "csvform" : csvform
        }

    return render(request, "index.html", context= context)


def generate_plots(request):
    csvform = csv_form(request.POST, request.FILES)
    missing_value_form = missing_values_form()
    if request.method == "POST":
        column_form = column_select_form(columns = request.session.get('num_cols',[]), initial_choices=request.session.get('selected_columns', []))
        axis_select = axis_select_form(request.POST, columns=request.session.get('num_cols',[]))

        df = pd.DataFrame(request.session['df'])
        top10 = df.head(10).to_html()

        x_col, plot_type = request.POST['column_x'], request.POST['plot_type']

        fig, ax = plt.subplots(figsize=(12, 10))
        rgba_color = (1/255, 75/255, 27/255, 0)  # RGBA color
        ax.set_facecolor(rgba_color)
        plt.rcParams['font.size'] = 22

        mean = request.session['stats_dict'][x_col]["Mean"]
        median = request.session['stats_dict'][x_col]["Median"]

        null_values = False
        if any(df[x_col].isna()):
                null_values = True

        if plot_type == "hist" :
            ax.hist(df[x_col], edgecolor='black')

            # ax.axvline(mean, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean}')
            # ax.axvline(median, color='b', linestyle='dashed', linewidth=2, label=f'Median: {median}')
            y_min = ax.get_ylim()[0]
            y_max = ax.get_ylim()[1]

            ax.plot([mean] * int(y_max - y_min + 1), np.arange(y_min, y_max), 'r--', label=f'Mean: {mean:.2f}')
            ax.plot([median] * int(y_max - y_min + 1), np.arange(y_min, y_max), 'b--', label=f'Median: {median:.2f}')
            
            ax.set_xlabel(f"{x_col} (ranges)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Histogram for \"{x_col}\"")
            ax.legend()

        elif plot_type == "box" :
            boxprops = dict(linestyle='-', linewidth=2, color='black')
            medianprops = dict(linestyle='-', linewidth=2.5, color='blue')
            meanprops = dict(marker='o', markerfacecolor='red', markersize=12)

            ax.boxplot(df[x_col], patch_artist=True, boxprops=boxprops, medianprops=medianprops, showmeans=True, meanprops=meanprops)

            # Set the title and labels
            ax.set_title(f"Box plot of {x_col}", color='black')
            ax.set_ylabel(x_col, color='black')

            # Annotate mean and median
            ax.annotate(f'Mean: {mean:.2f}', xy=(1, mean), xytext=(1.2, mean),
                        arrowprops=dict(facecolor='red', shrink=0.05), color='red')
            ax.annotate(f'Median: {median:.2f}', xy=(1, median), xytext=(0.6, median),
                        arrowprops=dict(facecolor='blue', shrink=0.05), color='blue')
            
            q1 = request.session['stats_dict'][x_col]["25th and 75th quantile"][0]
            q3 = request.session['stats_dict'][x_col]["25th and 75th quantile"][1]

            #Annotate Q1 and Q3
            ax.annotate(f'Q1: {q1:.2f}', xy=(1, q1), xytext=(1.1, q1),
                        arrowprops=dict(facecolor='green', shrink=0.05), color='green')
            ax.annotate(f'Q3: {q3:.2f}', xy=(1, q3), xytext=(1.1, q3),
                        arrowprops=dict(facecolor='green', shrink=0.05), color='green')

        else :
            df = df.dropna()    
            bins = pd.cut(df[x_col], bins=min(len(df[x_col].unique()), 4))
            bin_counts = bins.value_counts().sort_index()

            bin_labels = [f'{round(interval.left, 2)} - {round(interval.right, 2)}' for interval in bin_counts.index]

            bin_counts_list = bin_counts.tolist()

            wedges, texts = ax.pie(bin_counts_list, startangle=90, shadow=True, explode=[0.1]*len(bin_counts_list))

            total = sum(bin_counts_list)
            legend_labels = [f'{label}: {count} ({count/total:.1%})' for label, count in zip(bin_labels, bin_counts_list)]

            ax.legend(wedges, legend_labels, title="Ranges", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            # Set the title
            ax.set_title(f"Pie plot for \"{x_col}\"")

        plt.tight_layout()
        plt.plot()

        html = mpld3.fig_to_html(fig, figid='plot')

        #request.session['plotted_columns_types'] = [x_col, y_col, plot_type]
        request.session['plotted_columns_types'] = [x_col, plot_type]
        request.session['plot_html'] = html
        
        stats_dict = {}

        for col in request.session.get('selected_columns',[]):
            stats_dict[col] = request.session['stats_dict'][col]
        

        context = {
            "csvform" : csvform,
            "column_form" : column_form,
            "top10" : top10,
            "stats_dict" : stats_dict,
            "uploaded" : request.session['uploaded'],
            "axis_select" : axis_select,
            "plot" : html,
            "missing_value_form": missing_value_form,
            "null_values": null_values,
        }
        
    else:
        context = {
            "csvform" : csvform
        }

    return render(request, "index.html", context= context)

        



