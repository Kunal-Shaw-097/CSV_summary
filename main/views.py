from django.shortcuts import render
from .forms import CSVform
from .models import CSVmodel
from uuid import uuid4
import pandas as pd
import numpy as np

# Create your views here.
def index(request):
    if request.method == "POST": 
        context = {}
        context['csvform'] = CSVform()
        if request.FILES.get('Input_csv_file', False):
            print(request.FILES['Input_csv_file'])
            id= request.session.get("id", str(uuid4()))
            request.session[id] = id
            CSV = CSVmodel(id=id, csv=request.FILES['Input_csv_file'])
            CSV.save()
        df = pd.read_csv(CSV.csv.path)
        top5 = df.head(10).to_html()
        context['top5'] = top5
        return render(request, "index.html", context= context)

    