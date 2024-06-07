from django.db import models

# Create your models here.
class CSVmodel(models.Model):
    id = models.CharField(primary_key= True, max_length=100)
    csv = models.FileField(upload_to='csv')
