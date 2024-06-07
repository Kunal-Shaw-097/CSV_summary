from django.shortcuts import render
from .forms import CSVform, ColumnSelectForm
from .models import CSVmodel
from uuid import uuid4
import pandas as pd
import numpy as np
import os


def index(request) :
    csvform = CSVform()
    return render(request, "index.html", context= {"csvform" : csvform})

# Create your views here.
def upload_csv(request):
    csvform = CSVform(request.POST, request.FILES)
    if request.method == "POST": 
        if request.FILES.get('Input_csv_file', False):
            id= request.session.get("id", str(uuid4()))
            request.session[id] = id
            CSV = CSVmodel(id=id, csv=request.FILES['Input_csv_file'])
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

            column_form = ColumnSelectForm(columns=num_cols)

            context = {
                "csvform" : csvform,
                "column_form" : column_form,
                "top10" : top10,
                "uploaded" : request.session['uploaded'],
            }
    else :
        context = {
            "csvform" : csvform
        }
    
    return render(request, "index.html", context= context)


def calculate_stats(request): 
    if request.method == "POST":
        col = request.POST["column"]
        csvform = CSVform(request.POST, request.FILES)
        column_form = ColumnSelectForm(columns = request.session['num_cols'], initial_choice = col)

        df = pd.DataFrame(request.session['df'])
        top10 = df.head(10).to_html()
        num_df = df.select_dtypes(include=np.number)
        
        dict = {}
        dict[col] = {
            "Mean" : num_df[col].mean(),
            "Media": num_df[col].median(),
            "Standard Deviation": num_df[col].std(),
            "Missing Value Count": num_df[col].isna().sum(),
        }
        context = {
                "csvform" : csvform,
                "column_form" : column_form,
                "top10" : top10,
                "stats" : dict,
                "uploaded" : request.session['uploaded'],
            }
    else :
        context = {
            "csvform" : csvform
        }
    
    return render(request, "index.html", context= context)

        



