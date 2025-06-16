from django.db import models


class Person(models.Model):
    cpf = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=255, db_column='nome')
    gender = models.CharField(max_length=10)
    date = models.CharField(max_length=10, db_column='nasc')

    class Meta:
        managed = False  # existing table
        db_table = 'cpf'
