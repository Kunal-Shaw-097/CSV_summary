from django.urls import path
from . import views

app_name = "main"

urlpatterns= [
    path('', views.index,name='index'),
    path('upload_csv', views.upload_csv, name='upload_csv'),
    path('get_stats', views.calculate_stats, name='get_stats'),
    path('generate_plots', views.generate_plots, name='generate_plots')
]


